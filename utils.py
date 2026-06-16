"""
utils.py
--------
Shared utility functions and base types for the Render Preset Manager addon.

Covers:
    - Addon preference access
    - Nested attribute get/set with K-Tools/Octane interception
    - Curve Mapping serialization and deserialization
    - Render settings collection
    - UI comparison layout drawing
    - Blacklist system
    - Engine availability checks
"""

import bpy
from mathutils import Color, Vector
from collections import defaultdict
import random
from .properties.function_list import (
    CURVE_MAPPING_PATHS,
    RENDER_SETTINGS,
)


# =============================================================================
# Addon Globals
# =============================================================================

# Must be set at registration time by the addon's __init__.py
ADDON_NAME = ""


# =============================================================================
# Preference Access
# =============================================================================

def get_addon_preferences(context):
    """
    Safely retrieves the addon preferences using the registered package name.

    Returns None if ADDON_NAME has not been initialized yet.
    """
    if not ADDON_NAME:
        return None
    return bpy.context.preferences.addons[ADDON_NAME].preferences

# =============================================================================
#
#
# =============================================================================

def get_all_render_settings():
    """
    Junta a lista nativa do function_list.py com o JSON externo do usuário.
    USE ESTA FUNÇÃO em vez de importar RENDER_SETTINGS diretamente!
    """
    from .custom_props_manager import load_custom_props
    import copy
    
    # Criamos uma cópia para não mexer no arquivo original em memória
    full_list = copy.deepcopy(RENDER_SETTINGS)
    
    # Carregamos do JSON físico
    custom_entries = load_custom_props() # Deve retornar [(path, name), ...]
    
    # Adicionamos a chave que o seu save_preset_to_file está procurando
    if custom_entries:
        full_list["USER_CUSTOM"] = custom_entries
        
    return full_list

# =============================================================================
# UI Category Registry
# Maps internal category keys to their collapsible toggle property names.
# =============================================================================

CATEGORIES = {
    "RENDER_ENGINE":      "show_engine_changes",
    "CYCLES":             "show_cycles_changes",
    "BLENDER_EEVEE":      "show_eevee_changes",
    "BLENDER_WORKBENCH":  "show_workbench_changes",
    "BLENDER_OUTPUT":     "show_output_changes",
    "BLENDER_VIEW_LAYER": "show_view_layer_changes",
    "BLENDER_SCENE":      "show_scene_changes",
    # Octane Render
    "OCTANE":             "show_octane_engine",
    "OCTANE_VIEW_LAYER":  "show_octane_view_layer",
    "OCTANE_IMAGER":      "show_octane_imager",
    "OCTANE_POST":        "show_octane_post",
    # User's Custom Strings
    "USER_CUSTOM":        "show_user_custom",
}


# =============================================================================
# Comparison Layout
# =============================================================================

def draw_comparison_layout(layout, operator, changes_collection, show_checkboxes=False):
    """
    Draws a collapsible, categorized list of setting changes in the given layout.

    Each category is rendered as a box with a toggle header. Inside, settings
    are split into two columns and grouped by sub-category prefix.

    Args:
        layout:             The Blender UI layout to draw into.
        operator:           The operator instance holding the toggle properties.
        changes_collection: An iterable of PresetChangeItem entries to display.
        show_checkboxes:    Whether to render per-item apply checkboxes.
    """
    for category_key, toggle_prop in CATEGORIES.items():
        category_items = [item for item in changes_collection if item.category == category_key]

        if not category_items:
            continue

        box = layout.box()
        is_expanded = getattr(operator, toggle_prop)
        icon = "TRIA_DOWN" if is_expanded else "TRIA_RIGHT"

        # Convert "BLENDER_VIEW_LAYER" → "View Layer", etc.
        display_name = category_key.replace("BLENDER_", "").replace("_", " ").title()
        header_text = f"{display_name} ({len(category_items)} changes)"

        box.prop(operator, toggle_prop, text=header_text, icon=icon, emboss=False)

        if not is_expanded:
            continue

        # Group items by their sub-category prefix ("SubGroup: setting name")
        sub_groups = defaultdict(list)
        for item in category_items:
            parts = item.friendly_name.split(":", 1)
            if len(parts) == 2:
                sub_group = parts[0].strip()
                short_name = parts[1].strip()
            else:
                sub_group = "General"
                short_name = item.friendly_name
            sub_groups[sub_group].append((item, short_name))

        for sub_group_name, sub_items in sorted(sub_groups.items()):
            col = box.column()
            col.label(text=sub_group_name)

            # Split items evenly across two columns
            midpoint = (len(sub_items) + 1) // 2
            left_items  = sub_items[:midpoint]
            right_items = sub_items[midpoint:]

            main_row = col.row()

            col_left = main_row.column()
            for item, short_name in left_items:
                row = col_left.row(align=True)
                if show_checkboxes:
                    row.prop(item, "apply_change", text="")
                row.label(text=f"{short_name}: {item.current_value_str} → {item.preset_value_str}")

            col_right = main_row.column()
            for item, short_name in right_items:
                row = col_right.row(align=True)
                if show_checkboxes:
                    row.prop(item, "apply_change", text="")
                row.label(text=f"{short_name}: {item.current_value_str} → {item.preset_value_str}")


# =============================================================================
# Nested Attribute Access
# =============================================================================
def _resolve_path(scene, path):
    """
    Descobre quem é o objeto pai e qual é o nome do atributo final.
    Suporta caminhos relativos à cena (ex: 'render.resolution_x') 
    e caminhos absolutos (ex: 'bpy.context.preferences...').
    """
    # Se for um caminho absoluto global do Blender
    if path.startswith("bpy."):
        last_dot = path.rfind('.')
        if last_dot == -1: return None, None
        
        parent_path = path[:last_dot]
        attr_name = path[last_dot+1:]
        
        try:
            # Transforma a string do caminho no objeto real do Blender na memória
            parent_obj = eval(parent_path)
            return parent_obj, attr_name
        except Exception:
            return None, None

    # Se for o caminho padrão relativo à Scene
    else:
        attrs = path.split('.')
        current_obj = scene
        try:
            for attr in attrs[:-1]:
                current_obj = getattr(current_obj, attr)
            return current_obj, attrs[-1]
        except Exception:
            return None, None
        
def get_nested_attr(obj, path):
    """
    Retrieves a nested attribute from a Blender object by dotted path string.

    Supports:
        - ``KTOOLS_SPECIAL.octane_active_kernel``    reads the active Octane kernel type.
        - ``KTOOLS_SPECIAL.octane_kernel_input|X``   reads input X from the active kernel.
        - ``<ACTIVE_VIEW_LAYER>.some.prop``           resolves against the active view layer.
        - ``bpy.data.*`` / ``bpy.context.*``          evaluated directly via ``eval()``.
        - Standard dot-separated attribute paths.

    Returns None if the attribute cannot be resolved.
    """
    # --- K-Tools interception: read active Octane kernel type ---
    if path == "KTOOLS_SPECIAL.octane_active_kernel":
        try:
            tree = bpy.context.scene.octane.kernel_node_graph_property.node_tree
            if tree:
                for node in tree.nodes:
                    if "Kernel" in node.inputs and node.inputs["Kernel"].is_linked:
                        return node.inputs["Kernel"].links[0].from_node.bl_idname
            return "OctaneDirectLightingKernel"
        except AttributeError:
            return None

    # --- K-Tools interception: read an input value from the active Octane kernel ---
    if path.startswith("KTOOLS_SPECIAL.octane_kernel_input|"):
        input_name = path.split("|")[1]
        try:
            tree = bpy.context.scene.octane.kernel_node_graph_property.node_tree
            if tree:
                for node in tree.nodes:
                    if "Kernel" in node.inputs and node.inputs["Kernel"].is_linked:
                        active_kernel = node.inputs["Kernel"].links[0].from_node
                        if input_name in active_kernel.inputs:
                            return active_kernel.inputs[input_name].default_value
        except AttributeError:
            pass
        return None

    # --- Active View Layer shorthand ---
    if path.startswith("<ACTIVE_VIEW_LAYER>"):
        obj  = bpy.context.view_layer
        path = path.replace("<ACTIVE_VIEW_LAYER>.", "")

    # --- Direct bpy.data / bpy.context eval paths ---
    if path.startswith("bpy.data.") or path.startswith("bpy.context."):
        try:
            value = eval(path)
            if hasattr(value, "__len__") and not isinstance(value, (str, dict)):
                return list(value)
            return value
        except Exception:
            return None

    # --- bpy.* shorthand (strips leading "bpy.") ---
    if path.startswith("bpy."):
        obj  = bpy
        path = path[4:]

    # --- Standard dotted attribute traversal ---
    for attr in path.split("."):
        if hasattr(obj, attr):
            obj = getattr(obj, attr)
        else:
            return None

    if hasattr(obj, "__len__") and not isinstance(obj, (str, dict)):
        try:
            return list(obj)
        except Exception:
            pass

    return obj


# =============================================================================
# OCIO / Property Name Translation
# =============================================================================

# Maps engine-specific color-space names to their Blender-native equivalents.
# Populate this dict when a mismatch is detected between render engines.
OCIO_TRANSLATION_MAP = {
    # "Engine_Specific_Name": "Blender_Native_Name"
}


# =============================================================================
# Nested Attribute Setter
# =============================================================================

def set_nested_attr(obj, path, value):
    """
    Sets a nested attribute on a Blender object by dotted path string.

    Handles RNA type introspection to ensure type correctness, and includes
    special-case logic for Octane kernel nodes, curve mappings, OCIO names,
    and read-only properties.

    Returns:
        (True,  None)          on success.
        (False, error_message) on failure.
    """
    prop_path = path

    # --- K-Tools interception: switch the active Octane kernel node ---
    if path == "KTOOLS_SPECIAL.octane_active_kernel":
        target_kernel_idname = value
        try:
            tree = bpy.context.scene.octane.kernel_node_graph_property.node_tree
            if not tree:
                return False, "No Octane Kernel tree found"
        except AttributeError:
            return False, "Octane is not active or missing kernel property"

        # Locate the output node that accepts the Kernel socket
        out_node = next(
            (n for n in tree.nodes if "Kernel" in n.inputs),
            None
        )
        if not out_node:
            return False, "Kernel Output node not found"

        kernel_socket  = out_node.inputs["Kernel"]
        current_kernel = kernel_socket.links[0].from_node if kernel_socket.is_linked else None

        # No-op if the desired kernel is already active
        if current_kernel and current_kernel.bl_idname == target_kernel_idname:
            return True, None

        # Preserve spatial position before replacing the node
        if current_kernel:
            loc_x = current_kernel.location.x
            loc_y = current_kernel.location.y
            tree.nodes.remove(current_kernel)
        else:
            loc_x = out_node.location.x - 250
            loc_y = out_node.location.y

        try:
            new_kernel          = tree.nodes.new(target_kernel_idname)
            new_kernel.location = (loc_x, loc_y)
            tree.links.new(new_kernel.outputs[0], kernel_socket)
            return True, None
        except Exception as e:
            return False, f"Failed to switch kernel node: {e}"

    # --- K-Tools interception: set an input value on the active Octane kernel ---
    if path.startswith("KTOOLS_SPECIAL.octane_kernel_input|"):
        input_name = path.split("|")[1]
        try:
            tree = bpy.context.scene.octane.kernel_node_graph_property.node_tree
            if not tree:
                return False, "No Octane Kernel tree found"

            for node in tree.nodes:
                if "Kernel" in node.inputs and node.inputs["Kernel"].is_linked:
                    active_kernel = node.inputs["Kernel"].links[0].from_node
                    if input_name in active_kernel.inputs:
                        active_kernel.inputs[input_name].default_value = value
                    # Input not present on this kernel type – silently skip
                    return True, None

            return False, "Active kernel node not found"
        except Exception as e:
            return False, f"Failed to set kernel input '{input_name}': {e}"

    # --- Resolve the parent object and final attribute name ---
    if path.startswith("bpy.data.") or path.startswith("bpy.context."):
        last_dot    = path.rfind(".")
        if last_dot == -1:
            return False, "Invalid bpy path format"

        parent_path = path[:last_dot]
        last_attr   = path[last_dot + 1:]

        try:
            current_obj = eval(parent_path)
        except Exception as e:
            return False, f"Path evaluation failed: {e}"
    else:
        if path.startswith("<ACTIVE_VIEW_LAYER>"):
            base_obj  = bpy.context.view_layer
            prop_path = path.replace("<ACTIVE_VIEW_LAYER>.", "")
        elif path.startswith("bpy."):
            base_obj  = bpy
            prop_path = path[4:]
        else:
            base_obj = obj

        attrs       = prop_path.split(".")
        current_obj = base_obj

        try:
            for attr in attrs[:-1]:
                if hasattr(current_obj, attr):
                    current_obj = getattr(current_obj, attr)
                else:
                    return False, f"Attribute '{attr}' not found in path: {prop_path}"
            last_attr = attrs[-1]
        except AttributeError as e:
            return False, f"Attribute error in path '{prop_path}': {e}"

    # --- Special case: working color space must use an operator ---
    if prop_path == "data.colorspace.working_space":
        try:
            bpy.ops.wm.set_working_color_space(working_space=value)
            return True, None
        except Exception as e:
            return False, f"Operator error on path '{prop_path}': {e}"

    # --- Special case: curve mapping deserialization ---
    if prop_path in CURVE_MAPPING_PATHS:
        target_curve = get_nested_attr(obj, path)
        if target_curve:
            deserialize_curve_mapping(target_curve, value)
            return True, None
        return False, f"CurveMapping object not found for path: {prop_path}"

    # --- Standard RNA property assignment ---
    try:
        if not hasattr(current_obj, last_attr):
            return False, f"Property '{last_attr}' not found"

        rna_prop = current_obj.bl_rna.properties.get(last_attr)

        # Validate array type match
        if rna_prop and hasattr(rna_prop, "is_array") and rna_prop.is_array:
            if not isinstance(value, (list, tuple)):
                return False, "Mismatched type for array property."

        # Skip read-only properties silently (not an error – e.g. computed props)
        if rna_prop and rna_prop.is_readonly:
            return True, None

        # Fallback: OPEN_EXR_MULTILAYER → OPEN_EXR when unsupported
        if last_attr == "file_format" and value == "OPEN_EXR_MULTILAYER":
            if hasattr(rna_prop, "enum_items"):
                valid_formats = [item.identifier for item in rna_prop.enum_items]
                if "OPEN_EXR_MULTILAYER" not in valid_formats and "OPEN_EXR" in valid_formats:
                    value = "OPEN_EXR"

        # Apply OCIO name translation for color-management string properties
        if last_attr in ("name", "view_transform", "look") and isinstance(value, str):
            value = OCIO_TRANSLATION_MAP.get(value, value)

        setattr(current_obj, last_attr, value)

        # Force a view-layer update for properties known to require it
        if last_attr in ("color_management", "file_format", "engine"):
            bpy.context.view_layer.update()

        # Verify the assignment took effect; retry once with a forced update
        if isinstance(value, str):
            applied_value = getattr(current_obj, last_attr, None)
            if applied_value != value:
                bpy.context.view_layer.update()
                try:
                    setattr(current_obj, last_attr, value)
                except Exception:
                    pass

        return True, None

    except TypeError as e:
        return False, f"Type error setting '{prop_path}': {e}"
    except Exception as e:
        return False, f"Unexpected error on path '{prop_path}': {e}"


# =============================================================================
# Value Formatting (for UI display)
# =============================================================================

def format_value_for_preview(value):
    """
    Converts a raw setting value into a human-readable string for the UI.

    - None          → "Not Set"
    - bool          → "On" / "Off"
    - float         → 3 decimal places
    - int           → plain string
    - list          → numeric items rounded to 2 decimal places
    - dict (curve)  → "Curve Mapping (N curves)"
    - anything else → str()
    """
    if value is None:
        return "Not Set"

    if isinstance(value, bool):
        return "On" if value else "Off"

    if isinstance(value, float):
        return f"{value:.3f}"

    if isinstance(value, int):
        return str(value)

    if isinstance(value, list):
        if not value:
            return "[]"
        try:
            rounded = [
                round(float(item), 2) if isinstance(item, (int, float)) else item
                for item in value
            ]
            return str(rounded)
        except (TypeError, ValueError):
            return str(value)

    if isinstance(value, dict):
        if "curves" in value:
            return f"Curve Mapping ({len(value['curves'])} curves)"
        return str(value)

    return str(value)


# =============================================================================
# Curve Mapping Serialization
# =============================================================================

def serialize_curve_mapping(curve_mapping):
    """
    Serializes a Blender CurveMapping object into a JSON-compatible dictionary.

    Returns None if the object is invalid or has no curves.
    """
    if not curve_mapping or not hasattr(curve_mapping, "curves"):
        return None

    data = {"curves": []}

    for i, curve in enumerate(curve_mapping.curves):
        if not hasattr(curve, "points"):
            continue

        points_data = [
            {
                "x":           float(point.location[0]),
                "y":           float(point.location[1]),
                "handle_type": getattr(point, "handle_type", "AUTO"),
            }
            for point in curve.points
        ]

        data["curves"].append({"index": i, "points": points_data})

    return data


def deserialize_curve_mapping(target_curve_mapping, data):
    """
    Applies a previously serialized dictionary back onto a CurveMapping object.

    Returns True on success, False on failure or invalid input.
    """
    if not data or not target_curve_mapping or not hasattr(target_curve_mapping, "curves"):
        return False

    try:
        for curve_data in data.get("curves", []):
            curve_index = curve_data.get("index", 0)
            points_data = curve_data.get("points", [])

            if curve_index >= len(target_curve_mapping.curves):
                continue

            curve = target_curve_mapping.curves[curve_index]

            # Remove excess points (back-to-front to avoid index shifting)
            while len(curve.points) > len(points_data):
                try:
                    curve.points.remove(curve.points[-1])
                except Exception:
                    break

            # Apply point data, adding new points as needed
            for i, point_data in enumerate(points_data):
                x            = float(point_data["x"])
                y            = float(point_data["y"])
                handle_type  = point_data.get("handle_type", "AUTO")

                if i < len(curve.points):
                    pt = curve.points[i]
                    pt.location = (x, y)
                    if hasattr(pt, "handle_type"):
                        pt.handle_type = handle_type
                else:
                    new_pt = curve.points.new(x, y)
                    if hasattr(new_pt, "handle_type"):
                        new_pt.handle_type = handle_type

        target_curve_mapping.update()
        return True

    except Exception as e:
        print(f"Error deserializing curve mapping: {e}")
        return False


def safe_clear_curve_points(curve):
    """
    Removes all points from a curve safely, iterating back-to-front
    to avoid index-shifting issues. Falls back to front removal on failure.
    """
    while len(curve.points) > 0:
        try:
            curve.points.remove(curve.points[-1])
        except Exception:
            try:
                curve.points.remove(curve.points[0])
            except Exception:
                break


def test_curve_precision():
    """
    Developer utility: verifies round-trip fidelity of curve serialization.

    Serializes the scene's motion-blur shutter curve, prints the result,
    and immediately deserializes it back. Returns the serialized data dict.
    """
    import json

    original_curve = bpy.context.scene.render.motion_blur_shutter_curve
    data           = serialize_curve_mapping(original_curve)

    print("Serialized data:", json.dumps(data, indent=2))

    success = deserialize_curve_mapping(original_curve, data)
    print(f"Deserialization: {'OK' if success else 'FAIL'}")

    return data


# =============================================================================
# Render Settings Collection
# =============================================================================

def get_current_settings(category_name, context):
    """
    Collects the current values of all properties defined in RENDER_SETTINGS
    for the given category.

    Properties present in the user's blacklist are skipped.
    Curve mappings are serialized; Color/Vector/array types are cast to list.

    Args:
        category_name: One of the keys in RENDER_SETTINGS or "USER_CUSTOM".
        context:       The Blender context to read scene data from.

    Returns:
        A dict mapping setting_path → value for each readable property.
    """
    settings  = {}
    scene     = context.scene
    blacklist = get_blacklist_set(context)

    # Puxa a lista completa (Nativas + Customizadas do usuário)
    all_settings = get_all_render_settings()

    # Verifica na nova lista dinâmica em vez da estática
    if category_name not in all_settings:
        return settings

    # Itera sobre a nova lista dinâmica
    for setting_path, friendly_name in all_settings.get(category_name, []):
        if setting_path in blacklist:
            continue

        try:
            value = get_nested_attr(scene, setting_path)

            if setting_path in CURVE_MAPPING_PATHS:
                value = serialize_curve_mapping(value)
            elif isinstance(value, (Color, Vector, bpy.types.bpy_prop_array)):
                value = list(value)

            if value is not None:
                settings[setting_path] = value

        except Exception as e:
            print(f"Render Preset Manager Warning: Could not get property '{setting_path}': {e}")

    return settings


# =============================================================================
# PropertyGroup: Preset Change Item
# =============================================================================

class PresetChangeItem(bpy.types.PropertyGroup):
    """
    Represents a single setting difference between the active scene and a preset.
    Used to populate the preview and comparison UI lists.
    """

    # Internal data
    setting_path:     bpy.props.StringProperty()  # type: ignore
    preset_value_json: bpy.props.StringProperty()  # type: ignore  # JSON-encoded preset value
    category:         bpy.props.StringProperty()  # type: ignore

    # Display strings
    friendly_name:      bpy.props.StringProperty()  # type: ignore
    current_value_str:  bpy.props.StringProperty()  # type: ignore
    preset_value_str:   bpy.props.StringProperty()  # type: ignore

    # Per-item apply toggle (shown as a checkbox in the UI)
    apply_change: bpy.props.BoolProperty(
        name="Apply",
        description="Apply this specific setting change",
        default=True,
    )  # type: ignore

    is_blacklisted: bpy.props.BoolProperty(default=False)  # type: ignore


# =============================================================================
# Blacklist System
# =============================================================================

def get_blacklist_set(context):
    """
    Returns a set of setting paths that are currently disabled in the blacklist.

    Disabled paths are excluded from preset capture and application.
    Returns an empty set if preferences are unavailable.
    """
    prefs = get_addon_preferences(context)
    if not prefs:
        return set()

    return {item.path for item in prefs.blacklist_items if not item.is_enabled}


# =============================================================================
# Engine Availability
# =============================================================================

def is_engine_available(context, engine_identifier: str) -> bool:
    """
    Checks whether a given render engine is installed and available.

    Uses data-pointer presence on bpy.types.Scene rather than querying the
    dynamic enum, which is unreliable from Python.

    Args:
        context:           Blender context (unused currently, reserved for future use).
        engine_identifier: Case-insensitive engine name (e.g. "octane", "cycles").

    Returns:
        True if the engine appears to be available, False otherwise.
    """
    engine_name = engine_identifier.lower()

    if engine_name == "octane":
        return hasattr(bpy.types.Scene, "octane")
    if engine_name == "cycles":
        return hasattr(bpy.types.Scene, "cycles")

    return False

# =============================================================================
# Properties Test
# =============================================================================


def get_random_valid_value(obj, attr_name):
    """
    Inspeciona a propriedade RNA do Blender e gera um valor aleatório válido.
    """
    try:
        # Se não tiver RNA (ex: dicts comuns), ignoramos
        if not hasattr(obj, "bl_rna"): return None
        
        rna_prop = obj.bl_rna.properties.get(attr_name)
        if not rna_prop or rna_prop.is_readonly:
            return None

        # 1. BOOLEANOS (True ou False)
        if rna_prop.type == 'BOOLEAN':
            if getattr(rna_prop, 'is_array', False):
                return [random.choice([True, False]) for _ in range(rna_prop.array_length)]
            return random.choice([True, False])

        # 2. INTEIROS (Sorteia entre o mínimo e máximo permitido pelo Blender)
        elif rna_prop.type == 'INT':
            # Evita números absurdamente gigantes que o Blender permite teoricamente
            min_val = max(rna_prop.hard_min, -1000)
            max_val = min(rna_prop.hard_max, 1000)
            if getattr(rna_prop, 'is_array', False):
                return [random.randint(min_val, max_val) for _ in range(rna_prop.array_length)]
            return random.randint(min_val, max_val)

        # 3. FLOAT / DECIMAIS
        elif rna_prop.type == 'FLOAT':
            min_val = max(rna_prop.hard_min, -1000.0)
            max_val = min(rna_prop.hard_max, 1000.0)
            if getattr(rna_prop, 'is_array', False):
                return [random.uniform(min_val, max_val) for _ in range(rna_prop.array_length)]
            return round(random.uniform(min_val, max_val), 3)

        # 4. ENUMLIST (O pulo do gato: extrai apenas os 'identifiers' válidos)
        elif rna_prop.type == 'ENUM':
            valid_items = [item.identifier for item in rna_prop.enum_items]
            # Algumas propriedades têm formatos inválidos dependendo do SO, evitamos falhas
            if attr_name == "file_format" and "OPEN_EXR_MULTILAYER" in valid_items:
                valid_items.remove("OPEN_EXR_MULTILAYER") 
            return random.choice(valid_items)

    except Exception as e:
        print(f"Erro ao introspectar {attr_name}: {e}")
        return None