"""
op_user_presets.py
------------------
Operators and helpers for managing user and default preset lists.

Covers:
    - Scanning and caching the built-in /presets folder (default presets).
    - Scanning and caching the user-defined presets directory.
    - Fixed-width column formatting for dropdown enum labels.
    - Refreshing and loading presets from both sources.
    - Populating the public API preset list for use by external addons.

Operators defined here:
    - RENDER_PRESET_OT_refresh_defaults         Clears the default presets cache.
    - RENDER_PRESET_OT_load_default             Loads a selected built-in preset.
    - RENDER_PRESET_OT_refresh_user             Rescans and repopulates the user list.
    - RENDER_PRESET_OT_load_user                Loads a selected user preset.
    - RENDER_PRESET_OT_update_preset_api_list   Rebuilds the public API preset list.
"""

import bpy
import json
import os

from .. import utils
from ..utils import (
    PresetChangeItem,
    get_addon_preferences,
)


# =============================================================================
# Column Formatting Helper
# =============================================================================

def _format_column(text, width, padding_char="⠀"):
    """
    Returns a string padded or truncated to exactly ``width`` characters.

    Uses ``padding_char`` (a zero-width Braille space by default) so Blender's
    enum dropdown renders visually aligned columns without affecting search.

    Args:
        text:         The source string to format.
        width:        The exact character width to target.
        padding_char: Character used for right-padding (default: Braille space U+2800).

    Returns:
        A string of exactly ``width`` characters.
    """
    text_len = len(text)

    if text_len > width:
        # Truncate with an ellipsis, ensuring the result is still exactly `width` chars
        truncated = (text[:width - 3] + "...") if width > 3 else text[:width]
        # Safety padding in case the truncated string is somehow shorter than expected
        if len(truncated) < width:
            truncated += padding_char * (width - len(truncated))
        return truncated

    return text + padding_char * (width - text_len)


# =============================================================================
# Default Presets  (built-in /presets folder)
# =============================================================================

_default_presets_cache = None


def get_default_presets(self, context):
    """
    Scans the addon's built-in ``/presets`` subdirectory and returns enum items.

    Results are cached after the first scan; call
    ``RENDER_PRESET_OT_refresh_defaults`` to invalidate the cache.

    Returns:
        List of (identifier, label, description) tuples for use in an EnumProperty.
    """
    global _default_presets_cache
    if _default_presets_cache is not None:
        return _default_presets_cache

    presets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "presets")

    if not os.path.isdir(presets_dir):
        _default_presets_cache = [("NONE", "No Presets Found", "The 'presets' folder is missing.")]
        return _default_presets_cache

    # --- Pass 1: Collect raw data from each .json file ---
    temp_items = []
    for filename in sorted(os.listdir(presets_dir)):
        if not filename.lower().endswith(".json"):
            continue

        filepath = os.path.join(presets_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            blender_version = data.get("blender_version", "N/A")
            temp_items.append({
                "id":      filepath,
                "name":    data.get("preset_name", os.path.splitext(filename)[0]),
                "version": f"(Blender {blender_version})",
                "desc":    data.get("description", f"Preset for Blender {blender_version}"),
            })
        except Exception as e:
            print(f"Render Preset Manager: Error reading default preset '{filename}': {e}")

    if not temp_items:
        _default_presets_cache = [("NONE", "No Presets Found", "The 'presets' folder is empty.")]
        return _default_presets_cache

    # --- Pass 2: Compute balanced column widths (mirrors get_user_presets logic) ---
    MIN_COL_WIDTH  = 15
    MAX_COL_WIDTH  = 40
    SEPARATOR_SIZE = 3

    max_name_len    = max(len(item["name"])    for item in temp_items)
    max_version_len = max(len(item["version"]) for item in temp_items)

    col1_width = max(MIN_COL_WIDTH, min(max_name_len + 2, MAX_COL_WIDTH))
    col2_width = max_version_len  # Version column always fits its content
    separator  = "⠀" * SEPARATOR_SIZE

    # --- Pass 3: Build formatted enum labels ---
    # Version column is RIGHT-aligned: Braille-space prefix fills the gap.
    items = []
    for item in temp_items:
        col1         = _format_column(item["name"], col1_width)
        version_text = item["version"]
        col2         = "⠀" * (col2_width - len(version_text)) + version_text
        label        = f"{col1}{separator}{col2}"
        items.append((item["id"], label, item["desc"]))

    _default_presets_cache = items
    return _default_presets_cache


class RENDER_PRESET_OT_refresh_defaults(bpy.types.Operator):
    """Clears the default presets cache to force a re-scan of the built-in presets folder."""

    bl_idname  = "render_preset.refresh_defaults"
    bl_label   = "Refresh Default Presets"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        global _default_presets_cache
        _default_presets_cache = None
        self.report({"INFO"}, "Default presets list refreshed.")
        return {"FINISHED"}


class RENDER_PRESET_OT_load_default(bpy.types.Operator):
    """Loads the selected built-in preset and opens the preview dialog."""

    bl_idname  = "render_preset.load_default"
    bl_label   = "Load Selected Default"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        preset_props = context.scene.render_preset_settings
        filepath     = preset_props.default_preset_enum

        if not filepath or filepath == "NONE":
            self.report({"WARNING"}, "No default preset selected.")
            return {"CANCELLED"}

        try:
            with open(filepath, "r") as f:
                preset_data = json.load(f)

            preset_props.temp_preset_data   = json.dumps(preset_data)
            preset_props.temp_preset_loaded = True
            bpy.ops.render_preset.load_preview("INVOKE_DEFAULT")

        except Exception as e:
            self.report({"ERROR"}, f"Failed to load default preset file: {e}")
            return {"CANCELLED"}

        return {"FINISHED"}


# =============================================================================
# User Presets  (user-defined directory from addon preferences)
# =============================================================================

_user_presets_cache = None


def get_user_presets(self, context):
    """
    Scans the user-defined preset directory and returns enum items with
    aligned, fixed-width columns.

    Supports an optional filename column controlled by the
    ``show_filename_in_list`` addon preference.

    Columns rendered:
        - 2-column mode: ``Preset Name  |  Blender Version``
        - 3-column mode: ``Preset Name  |  [filename]  |  Blender Version``

    Results are cached; call ``RENDER_PRESET_OT_refresh_user`` to invalidate.

    Returns:
        List of (identifier, label, description) tuples for use in an EnumProperty.
    """
    global _user_presets_cache
    if _user_presets_cache is not None:
        return _user_presets_cache

    prefs = get_addon_preferences(context)
    show_filename = prefs.show_filename_in_list if prefs else False

    if not prefs or not prefs.user_presets_path:
        _user_presets_cache = [("NONE", "Set a directory in Addon Preferences", "")]
        return _user_presets_cache

    user_dir = prefs.user_presets_path
    if not os.path.isdir(user_dir):
        _user_presets_cache = [("NONE", "Invalid Directory in Preferences", "")]
        return _user_presets_cache

    # --- Pass 1: Collect raw data from each .json file ---
    temp_items = []
    for filename in sorted(os.listdir(user_dir)):
        if not filename.lower().endswith(".json"):
            continue

        filepath = os.path.join(user_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            blender_version = data.get("blender_version", "N/A")
            temp_items.append({
                "id":       filepath,
                "name":     data.get("preset_name", os.path.splitext(filename)[0].replace("_", "⠀").title()),
                "version":  f"(Blender {blender_version})",
                "desc":     data.get("description", f"Preset for Blender {blender_version}"),
                "filename": filename,
            })
        except Exception as e:
            print(f"Render Preset Manager: Error reading user preset '{filename}': {e}")

    if not temp_items:
        _user_presets_cache = [("NONE", "No Presets Found in User Directory", "")]
        return _user_presets_cache

    # --- Pass 2: Compute balanced column widths ---
    MIN_COL_WIDTH  = 15
    MAX_COL_WIDTH  = 40
    SEPARATOR_SIZE = 3  # Number of padding chars between columns

    max_name_len    = max(len(item["name"])    for item in temp_items)
    max_version_len = max(len(item["version"]) for item in temp_items)

    col1_width = max(MIN_COL_WIDTH, min(max_name_len + 2,    MAX_COL_WIDTH))
    col3_width = max_version_len  # Version column always fits its content

    if show_filename:
        max_filename_len = max(len(os.path.splitext(item["filename"])[0]) + 2 for item in temp_items)
        col2_width = max(MIN_COL_WIDTH, min(max_filename_len + 2, MAX_COL_WIDTH))
    else:
        col2_width = 0

    # --- Pass 3: Build formatted enum labels ---
    separator = "⠀" * SEPARATOR_SIZE
    items     = []

    # Version column is RIGHT-aligned: Braille-space prefix fills the gap.
    for item in temp_items:
        col1         = _format_column(item["name"], col1_width)
        version_text = item["version"]
        col3         = "⠀" * (col3_width - len(version_text)) + version_text

        if show_filename:
            filename_no_ext = os.path.splitext(item["filename"])[0]
            col2  = _format_column(f"[{filename_no_ext}]", col2_width)
            label = f"{col1}{separator}{col2}{separator}{col3}"
        else:
            label = f"{col1}{separator}{col3}"

        items.append((item["id"], label, item["desc"]))

    _user_presets_cache = items
    return _user_presets_cache


class RENDER_PRESET_OT_refresh_user(bpy.types.Operator):
    """Clears the dropdown cache and repopulates the UIList collection from the user presets folder."""

    bl_idname     = "render_preset.refresh_user"
    bl_label      = "Update User Presets"
    bl_description = "Re-scans the user presets folder"
    bl_options    = {"INTERNAL"}

    def execute(self, context):
        # --- Part 1: Invalidate the dropdown enum cache ---
        global _user_presets_cache
        _user_presets_cache = None

        # --- Part 2: Repopulate the UIList CollectionProperty ---
        prefs = utils.get_addon_preferences(context)
        if not prefs or not prefs.user_presets_path:
            self.report({"WARNING"}, "User presets path not defined in preferences.")
            return {"CANCELLED"}

        props      = context.scene.render_preset_settings
        collection = props.user_presets_collection
        collection.clear()

        directory = prefs.user_presets_path
        if not os.path.isdir(directory):
            self.report({"WARNING"}, f"Directory not found: {directory}")
            return {"CANCELLED"}

        try:
            json_files = sorted(f for f in os.listdir(directory) if f.lower().endswith(".json"))
            for filename in json_files:
                item          = collection.add()
                item.name     = os.path.splitext(filename)[0]
                item.filepath = os.path.join(directory, filename)
        except Exception as e:
            self.report({"ERROR"}, f"Error reading presets folder: {e}")
            return {"CANCELLED"}

        self.report({"INFO"}, "User preset list updated.")
        return {"FINISHED"}


class RENDER_PRESET_OT_load_user(bpy.types.Operator):
    """Loads the selected user preset and opens the preview dialog."""

    bl_idname     = "render_preset.load_user"
    bl_label      = "Load User Preset"
    bl_description = "Load the selected preset from the user's preset directory."

    def execute(self, context):
        preset_props = context.scene.render_preset_settings
        filepath     = preset_props.user_preset_enum

        if not filepath or filepath == "NONE":
            self.report({"WARNING"}, "No preset selected.")
            return {"CANCELLED"}

        try:
            with open(filepath, "r") as f:
                preset_data = json.load(f)

            preset_props.temp_preset_data   = json.dumps(preset_data)
            preset_props.temp_preset_loaded = True
            bpy.ops.render_preset.load_preview("INVOKE_DEFAULT")

        except Exception as e:
            self.report({"ERROR"}, f"Failed to load preset: {e}")
            return {"CANCELLED"}

        return {"FINISHED"}


# =============================================================================
# API Preset List  (for external addon integration)
# =============================================================================

class RENDER_PRESET_OT_update_preset_api_list(bpy.types.Operator):
    """
    Scans the user presets folder and populates the public API preset list.

    Intended to be called by external addons that need to enumerate available
    presets without depending on the internal enum cache. Writes results to
    ``scene.render_preset_api.presets``.
    """

    bl_idname  = "render_preset.update_preset_api_list"
    bl_label   = "Update Preset API List"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        prefs = utils.get_addon_preferences(context)
        if not prefs or not prefs.user_presets_path:
            return {"CANCELLED"}

        user_dir = prefs.user_presets_path
        if not os.path.isdir(user_dir):
            return {"CANCELLED"}

        api_props = context.scene.render_preset_api
        api_props.presets.clear()

        for filename in sorted(os.listdir(user_dir)):
            if not filename.lower().endswith(".json"):
                continue

            filepath = os.path.join(user_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                item          = api_props.presets.add()
                item.name     = data.get("preset_name", os.path.splitext(filename)[0])
                item.filepath = filepath

            except Exception as e:
                print(f"Render Preset Manager: Error reading '{filename}' for API list: {e}")

        return {"FINISHED"}


# =============================================================================
# Registration
# =============================================================================

classes = (
    PresetChangeItem,
    RENDER_PRESET_OT_refresh_defaults,
    RENDER_PRESET_OT_load_default,
    RENDER_PRESET_OT_refresh_user,
    RENDER_PRESET_OT_load_user,
    RENDER_PRESET_OT_update_preset_api_list,
)