"""
op_load.py
----------
Operators responsible for loading render presets into the active scene.

Operators defined here:
    - RENDER_PRESET_OT_load              - Opens a file browser to pick a .json preset.
    - RENDER_PRESET_OT_load_preview      - Shows a diff dialog before applying (with per-item checkboxes).
    - RENDER_PRESET_OT_load_confirm      - Applies preset data directly (no dialog); used internally.
    - RENDER_PRESET_OT_load_from_path    - API operator for external addons (e.g. K-Tools Render Preview Manager).
    - RENDER_PRESET_OT_load_from_active_index - Loads the preset selected in the UIList widget.

Helper functions:
    - compare_settings                - Returns the diff between current and preset values.
    - build_comparison_list           - Builds a structured diff list used by the preview dialog.
    - build_comparison_list_for_load  - Variant used by the direct-load flow.
"""

import bpy
import json
import os
import math

from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from ..utils import get_all_render_settings
from .. import utils
from ..utils import PresetChangeItem

RENDER_SETTINGS = get_all_render_settings()

# =============================================================================
# Helper Functions
# =============================================================================
def are_values_equal(val1, val2, tolerance=1e-6):
    """
    Compara dois valores de forma inteligente, com tolerância para floats,
    recursão para listas/tuplas e tratamento correto para None e tipos numéricos mistos.
    """
    # 1. Trata os casos com 'None' primeiro.
    # Se ambos são None, são iguais. Se apenas um é None, são diferentes.
    if val1 is None and val2 is None:
        return True
    if val1 is None or val2 is None:
        return False

    # 2. Compara listas/tuplas recursivamente.
    if isinstance(val1, (list, tuple)):
        # Garante que o outro valor também seja uma lista/tupla do mesmo tamanho.
        if not isinstance(val2, (list, tuple)) or len(val1) != len(val2):
            return False
        # Compara cada item da lista recursivamente.
        return all(are_values_equal(i1, i2, tolerance) for i1, i2 in zip(val1, val2))

    # 3. Trata números (int, float) com tolerância.
    # Tenta converter ambos para float para uma comparação justa.
    try:
        num1 = float(val1)
        num2 = float(val2)
        return math.isclose(num1, num2, rel_tol=tolerance)
    except (ValueError, TypeError):
        # Se a conversão para float falhar, significa que não são números.
        # Prossegue para a comparação final.
        pass

    # 4. Para todos os outros tipos (bool, string, etc.), usa a comparação padrão.
    return val1 == val2


def compare_settings(current, preset):
    """
    Returns a dict of settings that differ between current scene state and the preset.

    Args:
        current: Dict of {path: value} for the active scene.
        preset:  Dict of {path: value} from the preset file.

    Returns:
        Dict of {path: {"current": value, "preset": value}} for each differing key.
    """
    if not preset:
        return {}

    return {
        key: {"current": current.get(key), "preset": preset_value}
        for key, preset_value in preset.items()
        if current.get(key) != preset_value
    }


def build_comparison_list(context, preset_data, load_engine, label_map):
    """
    Builds a structured list of setting differences for the preview dialog.

    Each entry is a 5-tuple:
        (setting_path, friendly_name, current_str, preset_str, raw_preset_value)

    Args:
        context:      Active Blender context.
        preset_data:  Parsed preset JSON dict.
        load_engine:  Category key to filter by, or "ALL" for all categories.
        label_map:    Dict mapping setting paths to human-readable labels.

    Returns:
        Dict of {engine_name: [tuple, ...]} containing only engines with differences.
    """
    comparison_list = {}
    engines_to_show = (
        [load_engine]
        if load_engine != "ALL"
        else preset_data["render_presets"].keys()
    )

    for engine_name in engines_to_show:
        if engine_name not in preset_data["render_presets"]:
            continue

        engine_settings  = preset_data["render_presets"][engine_name]
        current_settings = utils.get_current_settings(engine_name, context)
        differences      = compare_settings(current_settings, engine_settings)

        if differences:
            comparison_list[engine_name] = [
                (
                    setting,
                    label_map.get(setting, setting.replace("_", " ").title()),
                    utils.format_value_for_preview(diff["current"]),
                    utils.format_value_for_preview(diff["preset"]),
                    diff["preset"],  # Raw preset value, stored as JSON later
                )
                for setting, diff in differences.items()
            ]

    return comparison_list


def build_comparison_list_for_load(context, preset_data, load_engine, label_map):
    """
    Variant of ``build_comparison_list`` used by the direct-load (no dialog) flow.

    Identical structure; kept separate to allow independent evolution.
    """
    comparison_list = {}
    engines_to_show = (
        [load_engine]
        if load_engine != "ALL"
        else preset_data["render_presets"].keys()
    )

    for engine_name in engines_to_show:
        if engine_name not in preset_data["render_presets"]:
            continue

        engine_settings  = preset_data["render_presets"][engine_name]
        current_settings = utils.get_current_settings(engine_name, context)
        differences      = compare_settings(current_settings, engine_settings)

        if differences:
            comparison_list[engine_name] = [
                (
                    setting,
                    label_map.get(setting, setting.replace("_", " ").title()),
                    utils.format_value_for_preview(diff["current"]),
                    utils.format_value_for_preview(diff["preset"]),
                    diff["preset"],
                )
                for setting, diff in differences.items()
            ]

    return comparison_list


# =============================================================================
# Operator: Open File Browser
# =============================================================================

class RENDER_PRESET_OT_load(Operator, ImportHelper):
    """Opens a file browser to select a .json preset file, then triggers the preview dialog."""

    bl_idname     = "render_preset.load"
    bl_label      = "Load Render Preset"
    bl_description = "Load render settings from a preset file"

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={"HIDDEN"})  # type: ignore

    def execute(self, context):
        scene = context.scene


        try:
            with open(self.filepath, "r") as f:
                preset_data = json.load(f)

            # Basic structure validation
            required_keys = ("preset_name", "render_presets")
            if not all(key in preset_data for key in required_keys):
                self.report({"ERROR"}, "Invalid preset file format.")
                return {"CANCELLED"}

            # Cache preset data in scene properties for the preview operator to read
            preset_props = context.scene.render_preset_settings
            preset_props.temp_preset_data   = json.dumps(preset_data)
            preset_props.temp_preset_loaded = True

            scene.render_preset_settings.last_loaded_preset_path = self.filepath

            return bpy.ops.render_preset.load_preview("INVOKE_DEFAULT")

        except Exception as e:
            self.report({"ERROR"}, f"Failed to read preset file: {e}")
            return {"CANCELLED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


# =============================================================================
# Operator: Preview Dialog (diff + per-item checkboxes)
# =============================================================================

class RENDER_PRESET_OT_load_preview(bpy.types.Operator):
    """
    Shows a diff dialog before applying a preset.

    Displays all settings that differ between the active scene and the preset,
    grouped by category, with individual checkboxes to include or exclude each
    change. Supports filtering by render engine category via a dynamic enum.
    """

    bl_idname = "render_preset.load_preview"
    bl_label  = "Load Render Preset"

    # --- Dynamic enum: populated from the categories present in the preset ---
    def _get_available_engines(self, context):
        """Reads the cached preset JSON and builds engine filter enum items."""
        items = [("ALL", "All Available", "Load all properties from the selected preset", "WORLD", 0)]

        # Human-readable labels for each known category key
        category_display = {
            "RENDER_ENGINE":     ("Scene Render Engine", "Load the Scene Render Engine",   "SCENE_DATA"),
            "CYCLES":            ("Cycles Only",         "Load only Cycles settings",       "PMARKER_SEL"),
            "BLENDER_EEVEE":     ("Eevee Only",          "Load only Eevee settings",        "LIGHT_SUN"),
            "BLENDER_WORKBENCH": ("Workbench Only",      "Load only Workbench settings",    "SHADING_SOLID"),
            "BLENDER_OUTPUT":    ("Output Only",         "Load only Output settings",       "OUTPUT"),
            "VIEW_LAYER":        ("View Layer Only",     "Load only View Layer settings",   "RENDERLAYERS"),
            "BLENDER_SCENE":     ("Scene Only",          "Load only Scene settings",        "SCENE_DATA"),
            "OCTANE":            ("Octane Render Settings Only",         "Load only Octane settings",       "PLUGIN"),
            "USER_CUSTOM":       ("User's Custom Settings Only",         "Load only User's settings",       "PLUGIN"),
        }

        try:
            preset_data = json.loads(context.scene.render_preset_settings.temp_preset_data)
            available   = preset_data.get("render_presets", {}).keys()

            for i, cat in enumerate(available, start=1):
                if cat in category_display:
                    name, desc, icon = category_display[cat]
                    items.append((cat, name, desc, icon, i))
                else:
                    # Graceful fallback for unrecognized category keys
                    label = cat.replace("_", " ").title()
                    items.append((cat, label, f"Load {cat} settings", "PREFERENCES", i))

        except Exception:
            pass

        return items

    load_engine: bpy.props.EnumProperty( # type: ignore
        name="Settings",
        description="Choose which render engine settings to preview and load",
        items=_get_available_engines,
    )  # type: ignore

    # Collection of change items populated in invoke()
    changes: bpy.props.CollectionProperty(type=PresetChangeItem)  # type: ignore

    # Per-category collapsible toggles
    show_engine_changes:    bpy.props.BoolProperty(name="Render Engine",          default=False)  # type: ignore
    show_cycles_changes:    bpy.props.BoolProperty(name="Cycles",                 default=False)  # type: ignore
    show_eevee_changes:     bpy.props.BoolProperty(name="Eevee",                  default=False)  # type: ignore
    show_workbench_changes: bpy.props.BoolProperty(name="Workbench",              default=False)  # type: ignore
    show_output_changes:    bpy.props.BoolProperty(name="Output",                 default=False)  # type: ignore
    show_view_layer_changes: bpy.props.BoolProperty(name="View Layer",            default=False)  # type: ignore
    show_scene_changes:     bpy.props.BoolProperty(name="Scene",                  default=False)  # type: ignore
    # Octane-specific toggles
    show_octane_engine:     bpy.props.BoolProperty(name="Octane: Render Properties", default=False)  # type: ignore
    show_octane_view_layer: bpy.props.BoolProperty(name="Octane: View Layer",     default=False)  # type: ignore
    show_octane_imager:     bpy.props.BoolProperty(name="Octane: Imager",         default=False)  # type: ignore
    show_octane_post:       bpy.props.BoolProperty(name="Octane: Postprocessing", default=False)  # type: ignore
    # User's Custom Properties
    show_user_custom:       bpy.props.BoolProperty(name="User Custom Properties", default=False)  # type: ignore

    # ------------------------------------------------------------------
    # Module-inclusion toggles (only active when load_engine == "ALL")
    # Allow the user to disable entire modules before applying the preset.
    # ------------------------------------------------------------------
    include_render_engine: bpy.props.BoolProperty(name="Render Engine", default=True)  # type: ignore
    include_cycles:        bpy.props.BoolProperty(name="Cycles",        default=True)  # type: ignore
    include_eevee:         bpy.props.BoolProperty(name="Eevee",         default=True)  # type: ignore
    include_workbench:     bpy.props.BoolProperty(name="Workbench",     default=True)  # type: ignore
    include_output:        bpy.props.BoolProperty(name="Output",        default=True)  # type: ignore
    include_view_layer:    bpy.props.BoolProperty(name="View Layer",    default=True)  # type: ignore
    include_scene:         bpy.props.BoolProperty(name="Scene",         default=True)  # type: ignore
    include_octane:        bpy.props.BoolProperty(name="Octane",        default=True)  # type: ignore
    include_user_custom:   bpy.props.BoolProperty(name="User Custom",   default=True)  # type: ignore

    # Maps every known category key to its module-inclusion BoolProperty name
    _CATEGORY_TO_INCLUDE_PROP = {
        "RENDER_ENGINE":      "include_render_engine",
        "CYCLES":             "include_cycles",
        "BLENDER_EEVEE":      "include_eevee",
        "BLENDER_WORKBENCH":  "include_workbench",
        "BLENDER_OUTPUT":     "include_output",
        "VIEW_LAYER":         "include_view_layer",
        "BLENDER_VIEW_LAYER": "include_view_layer",
        "BLENDER_SCENE":      "include_scene",
        "OCTANE":             "include_octane",
        "USER_CUSTOM":        "include_user_custom",
    }

    def invoke(self, context, event):
        self.changes.clear()

        preset_data = json.loads(context.scene.render_preset_settings.temp_preset_data)
        label_map   = {
            path: label
            for category in RENDER_SETTINGS.values()
            for path, label in category
        }
        blacklist = utils.get_blacklist_set(context)

        # Populate the changes collection with all differing settings
        for category_name, preset_settings in preset_data.get("render_presets", {}).items():
            for setting_path, preset_value in preset_settings.items():
                current_value = utils.get_nested_attr(context.scene, setting_path)

                if not are_values_equal(current_value, preset_value):
                    item = self.changes.add()
                    item.setting_path       = setting_path
                    item.friendly_name      = label_map.get(setting_path, setting_path)
                    item.category           = category_name
                    item.current_value_str  = utils.format_value_for_preview(current_value)
                    item.preset_value_str   = utils.format_value_for_preview(preset_value)
                    item.preset_value_json  = json.dumps(preset_value)
                    item.apply_change       = True
                    item.is_blacklisted     = setting_path in blacklist

        return context.window_manager.invoke_props_dialog(self, width=700)

    def draw(self, context):
        layout       = self.layout
        preset_props = context.scene.render_preset_settings
        preset_data  = json.loads(preset_props.temp_preset_data)

        # Preset name header
        box = layout.box()
        box.label(text=f"Preset: {preset_data.get('preset_name', 'N/A')}", icon="FILE")
        box.prop(self, "load_engine")

        # ------------------------------------------------------------------
        # Module-selection panel — only when "All Available" is selected.
        # Shows one checkbox per module that is actually present in the preset.
        # ------------------------------------------------------------------
        if self.load_engine == "ALL":
            available_categories = list(preset_data.get("render_presets", {}).keys())

            # Category → display label for the module toggle row
            _MODULE_LABELS = {
                "RENDER_ENGINE":      ("Render Engine", "SCENE_DATA"),
                "CYCLES":             ("Cycles",        "PMARKER_SEL"),
                "BLENDER_EEVEE":      ("Eevee",         "LIGHT_SUN"),
                "BLENDER_WORKBENCH":  ("Workbench",     "SHADING_SOLID"),
                "BLENDER_OUTPUT":     ("Output",        "OUTPUT"),
                "VIEW_LAYER":         ("View Layer",    "RENDERLAYERS"),
                "BLENDER_VIEW_LAYER": ("View Layer",    "RENDERLAYERS"),
                "BLENDER_SCENE":      ("Scene",         "SCENE_DATA"),
                "OCTANE":             ("Octane",        "PLUGIN"),
                "USER_CUSTOM":        ("User Custom",   "PREFERENCES"),
            }

            mod_box = layout.box()
            mod_box.label(text="Modules to Load:", icon="CHECKMARK")

            # Render toggles in pairs for a compact 2-column layout
            col = mod_box.column(align=True)
            # Track which props have already been drawn (VIEW_LAYER aliases)
            _drawn_props = set()

            for cat in available_categories:
                prop_name = self._CATEGORY_TO_INCLUDE_PROP.get(cat)
                if prop_name is None or prop_name in _drawn_props:
                    continue
                _drawn_props.add(prop_name)

                label, icon = _MODULE_LABELS.get(cat, (cat.replace("_", " ").title(), "DOT"))
                row = col.row(align=True)
                row.prop(self, prop_name, text=label, icon=icon)

        layout.separator()

        # Filter changes by selected engine category
        if self.load_engine == "ALL":
            # Further filter by module-inclusion booleans
            visible_changes = [
                item for item in self.changes
                if getattr(self, self._CATEGORY_TO_INCLUDE_PROP.get(item.category, ""), True)
            ]
        else:
            visible_changes = [item for item in self.changes if item.category == self.load_engine]

        # Exclude blacklisted items from the display
        changes_to_display = [item for item in visible_changes if not item.is_blacklisted]

        if not changes_to_display:
            layout.label(
                text="No changes to apply for the selected category (or all items are blacklisted).",
                icon="CHECKMARK",
            )
            return

        utils.draw_comparison_layout(layout, self, changes_to_display, show_checkboxes=True)

    def execute(self, context):
        scene        = context.scene
        preset_props = scene.render_preset_settings
        blacklist    = utils.get_blacklist_set(context)

        # --- Save undo snapshot before applying anything ---
        preset_props.undo_data = json.dumps({
            name: utils.get_current_settings(name, context)
            for name in RENDER_SETTINGS.keys()
        })

        applied_count        = 0
        failed_to_apply      = []
        skipped_on_blacklist = []
        delayed_items        = []

        # Properties that depend on the file format / color management being set first
        DELAYED_PROPERTIES = {
            "render.image_settings.color_management",
            "render.image_settings.view_settings.view_transform",
            "render.image_settings.view_settings.look",
            "render.image_settings.linear_colorspace_settings.name",
            "data.colorspace.working_space",
        }

        load_all = (self.load_engine == "ALL")

        def _module_enabled(category):
            """Returns True if the user has enabled the module for this category.
            Always True when a single engine is selected (load_all is False)."""
            if not load_all:
                return True
            prop_name = self._CATEGORY_TO_INCLUDE_PROP.get(category)
            if prop_name is None:
                return True  # Unknown category → always include (safe default)
            return getattr(self, prop_name, True)

        # --- Pass 1: Apply render engine & initialize Octane kernel if needed ---
        engine_changed      = False
        target_engine_name  = None

        for item in self.changes:
            matches_category = (item.category == self.load_engine)

            if (
                item.setting_path == "render.engine"
                and item.apply_change
                and item.setting_path not in blacklist
                and (load_all and _module_enabled(item.category) or matches_category)
            ):
                try:
                    target_engine_name = json.loads(item.preset_value_json)
                    success, error_msg = utils.set_nested_attr(scene, item.setting_path, target_engine_name)

                    if success:
                        applied_count += 1
                        engine_changed  = True
                        bpy.context.view_layer.update()
                    else:
                        failed_to_apply.append((item.friendly_name, error_msg))
                except Exception as e:
                    failed_to_apply.append((item.friendly_name, str(e)))

                break  # Only one render.engine entry exists; stop searching

        # Initialize Octane kernel node tree if the engine was just switched to Octane
        if engine_changed and target_engine_name and target_engine_name.upper() == "OCTANE":
            if scene.octane.kernel_node_graph_property.node_tree is None:
                try:
                    bpy.ops.octane.quick_add_kernel_nodetree(create_new_window=False)
                except Exception as e:
                    print(f"K-Tools: Failed to create Octane Kernel node tree – {e}")

        # --- Pass 2: Apply standard (non-delayed) properties ---
        for item in self.changes:
            matches_category = (item.category == self.load_engine)

            if item.setting_path in blacklist:
                if item.setting_path != "render.engine":
                    skipped_on_blacklist.append(item.friendly_name)
                continue

            if not item.apply_change:
                continue

            if item.setting_path == "render.engine":
                continue  # Already handled in Pass 1

            if item.setting_path in DELAYED_PROPERTIES:
                if (load_all and _module_enabled(item.category)) or matches_category:
                    delayed_items.append(item)
                continue

            if not ((load_all and _module_enabled(item.category)) or matches_category):
                continue

            original_value = json.loads(item.preset_value_json)
            success, error_msg = utils.set_nested_attr(scene, item.setting_path, original_value)

            if success:
                applied_count += 1
            else:
                failed_to_apply.append((item.friendly_name, error_msg))

        # --- Pass 3: Apply delayed properties (color management, file format, etc.) ---
        if delayed_items:
            # Ensure prerequisites (file format, color management) are committed first
            for item in self.changes:
                if not item.apply_change or item.setting_path in blacklist:
                    continue
                if not ((load_all and _module_enabled(item.category)) or item.category == self.load_engine):
                    continue

                if item.setting_path in {
                    "render.image_settings.color_management",
                    "render.image_settings.file_format",
                }:
                    utils.set_nested_attr(scene, item.setting_path, json.loads(item.preset_value_json))
                    bpy.context.view_layer.update()

            for item in delayed_items:
                try:
                    original_value = json.loads(item.preset_value_json)
                    success, error_msg = utils.set_nested_attr(scene, item.setting_path, original_value)

                    if success:
                        applied_count += 1
                        bpy.context.view_layer.update()
                    else:
                        failed_to_apply.append((item.friendly_name, error_msg))
                except Exception as e:
                    failed_to_apply.append((item.friendly_name, str(e)))

        # --- Pass 4: Verification – re-apply any property that didn't stick ---
        bpy.context.view_layer.update()
        reapplied_count = 0

        for item in self.changes:
            matches_category = (item.category == self.load_engine)

            if item.setting_path in blacklist or not item.apply_change:
                continue
            if not ((load_all and _module_enabled(item.category)) or matches_category):
                continue

            original_value = json.loads(item.preset_value_json)
            current_value  = utils.get_nested_attr(scene, item.setting_path)

            if not are_values_equal(current_value, original_value):
                success, _ = utils.set_nested_attr(scene, item.setting_path, original_value)
                if success:
                    reapplied_count += 1
                    bpy.context.view_layer.update()
                    # Remove from failures list if re-application succeeded
                    failed_to_apply = [f for f in failed_to_apply if f[0] != item.friendly_name]

        # --- Cleanup temporary scene data ---
        preset_data = json.loads(preset_props.temp_preset_data)
        preset_props.loaded_preset_name = preset_data.get("preset_name", "Unknown")
        preset_props.temp_preset_data   = ""
        preset_props.temp_preset_loaded = False

        # --- Final report ---
        has_failures = bool(failed_to_apply)
        has_skips    = bool(skipped_on_blacklist)

        if not has_failures and not has_skips:
            msg = f"Successfully applied {applied_count} settings."
            if reapplied_count > 0:
                msg += f" (Auto-corrected {reapplied_count} properties.)"
            self.report({"INFO"}, msg)
        else:
            parts = []
            if applied_count > 0:
                parts.append(f"Applied {applied_count} settings")
            if has_failures:
                parts.append(f"{len(failed_to_apply)} failed")
            if has_skips:
                parts.append(f"{len(skipped_on_blacklist)} skipped (blacklist)")

            self.report({"WARNING"}, f"{', '.join(parts)}. Check System Console.")

            print("\n--- Render Preset Manager: Load Report ---")
            if applied_count > 0:
                print(f"  Successfully applied {applied_count} settings.")
            if reapplied_count > 0:
                print(f"  -> Verification pass auto-corrected {reapplied_count} properties.")
            if has_skips:
                print(f"\n  {len(skipped_on_blacklist)} properties SKIPPED (blacklisted):")
                for name in skipped_on_blacklist:
                    print(f"    - '{name}'")
            if has_failures:
                print(f"\n  {len(failed_to_apply)} properties FAILED:")
                for name, error in failed_to_apply:
                    print(f"    - '{name}': {error or 'Unknown error'}")
            print("------------------------------------------")

        return {"FINISHED"}


# =============================================================================
# Operator: Direct Confirm (no dialog)
# =============================================================================

class RENDER_PRESET_OT_load_confirm(Operator):
    """
    Applies preset data directly without showing a preview dialog.

    Saves an undo snapshot first, then applies all settings from the preset.
    Used internally and by RENDER_PRESET_OT_load_from_path.
    """

    bl_idname = "render_preset.load_confirm"
    bl_label  = "Confirm Load"

    preset_data: StringProperty()  # type: ignore  – JSON-encoded preset dict
    load_engine: StringProperty()  # type: ignore  – Category key or "ALL"

    def execute(self, context):
        scene        = context.scene
        preset_props = scene.render_preset_settings

        # --- Save undo snapshot ---
        preset_props.undo_data = json.dumps({
            engine: utils.get_current_settings(engine, context)
            for engine in RENDER_SETTINGS.keys()
        })

        try:
            preset_data = json.loads(self.preset_data)
            preset_props.loaded_preset_name = preset_data.get("preset_name", "Unknown")

            engines_to_load = (
                list(preset_data["render_presets"].keys())
                if self.load_engine == "ALL"
                else ([self.load_engine] if self.load_engine in preset_data["render_presets"] else [])
            )

            applied_count = 0

            for engine_name in engines_to_load:
                engine_settings = preset_data["render_presets"][engine_name]

                # Pass 1: Apply render engine first
                if "render.engine" in engine_settings:
                    target_engine = engine_settings["render.engine"]
                    success, _    = utils.set_nested_attr(scene, "render.engine", target_engine)

                    if success:
                        applied_count += 1
                        bpy.context.view_layer.update()

                        # Initialize Octane kernel node tree if needed
                        if target_engine == "OCTANE":
                            if scene.octane.kernel_node_graph_property.node_tree is None:
                                try:
                                    bpy.ops.octane.quick_add_kernel_nodetree(create_new_window=False)
                                except Exception as e:
                                    print(f"K-Tools: Failed to create Octane Kernel – {e}")

                # Pass 2: Apply all remaining properties
                for path, value in engine_settings.items():
                    if path == "render.engine":
                        continue

                    success, _ = utils.set_nested_attr(scene, path, value)
                    if success:
                        applied_count += 1

            self.report({"INFO"}, f"Applied {applied_count} settings from '{preset_props.loaded_preset_name}'.")

        except Exception as e:
            preset_props.undo_data          = ""
            preset_props.loaded_preset_name = ""
            self.report({"ERROR"}, f"Failed to apply preset: {e}")
            return {"CANCELLED"}

        return {"FINISHED"}


# =============================================================================
# Operator: Load from Path (API / external addon use)
# =============================================================================

class RENDER_PRESET_OT_load_from_path(Operator):
    """
    Silently loads a preset from the path stored in ``scene.render_preset_settings.preview_preset_path``.
    Intended for use by external scripts and addons such as K-Tools Render Preview Manager.
    """

    bl_idname = "render_preset.load_from_path"
    bl_label  = "Load Preset From Path (Direct)"

    def execute(self, context):
        preset_props  = context.scene.render_preset_settings
        relative_path = preset_props.preview_preset_path

        if not relative_path:
            self.report({"ERROR"}, "Preview preset path is not set.")
            return {"CANCELLED"}

        absolute_path = bpy.path.abspath(relative_path)
        if not os.path.exists(absolute_path):
            self.report({"ERROR"}, f"Preset file not found at: {absolute_path}")
            return {"CANCELLED"}

        try:
            with open(absolute_path, "r") as f:
                preset_data = json.load(f)
        except Exception as e:
            self.report({"ERROR"}, f"Failed to read preset file: {e}")
            return {"CANCELLED"}

        # --- CORREÇÃO: Grava o caminho na memória para o Update funcionar ---
        preset_props.last_loaded_preset_path = absolute_path

        bpy.ops.render_preset.load_confirm(
            preset_data=json.dumps(preset_data),
            load_engine="ALL",
        )
        return {"FINISHED"}


# =============================================================================
# Operator: Load from UIList Active Index
# =============================================================================

class RENDER_PRESET_OT_load_from_active_index(bpy.types.Operator):
    """Loads the preset currently selected in the user preset UIList."""

    bl_idname     = "render_preset.load_from_list"
    bl_label      = "Load Selected Preset"
    bl_description = "Load the preset selected in the list"

    def execute(self, context):
        props      = context.scene.render_preset_settings
        collection = props.user_presets_collection
        index      = props.active_user_index

        if 0 <= index < len(collection):
            filepath = collection[index].filepath
            absolute_path = bpy.path.abspath(filepath)
            
            # --- CORREÇÃO: Força a gravação do caminho exato selecionado ---
            props.last_loaded_preset_path = absolute_path
            
            # Chama o operador original que invoca o dialog de preview
            bpy.ops.render_preset.load(filepath=absolute_path)
            return {"FINISHED"}

        self.report({"WARNING"}, "No preset selected.")
        return {"CANCELLED"}


# =============================================================================
# Registration
# =============================================================================

classes = (
    RENDER_PRESET_OT_load,
    RENDER_PRESET_OT_load_preview,
    RENDER_PRESET_OT_load_confirm,
    RENDER_PRESET_OT_load_from_path,
    RENDER_PRESET_OT_load_from_active_index,
)