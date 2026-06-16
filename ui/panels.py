"""
panels.py
---------
Blender UI panel definitions and drawing functions for the Render Preset Manager.

Covers:
    - UIList for displaying user presets
    - Core UI drawing logic (modes: load user, load from file, load default, save)
    - Three panel placement strategies: standard panel, headerless panel, prepend injection
    - Developer Tools sub-panel (visible only when developer_extras is enabled)
    - Class registration / unregistration
"""

import bpy

from ..utils import get_addon_preferences, is_engine_available
from ..operators import (
    op_save,
    op_undo,
    op_load,
    op_delete,
    op_user_presets,
)


# =============================================================================
# UIList: User Preset List
# =============================================================================

class RENDER_PRESET_UL_user_list(bpy.types.UIList):
    """Scrollable list widget for user-created presets."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Factory presets show a lock icon; user presets show the generic preset icon
        custom_icon = "LOCKED" if (hasattr(item, "is_factory") and item.is_factory) else "PRESET"

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.row(align=True).label(text=item.name, icon=custom_icon)
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon=custom_icon)


# =============================================================================
# Main UI Entry Point
# =============================================================================

def draw_main_addon_ui(layout, context):
    """
    Renders the complete addon UI into the given layout.

    Called by both the dedicated panel classes and the prepend/append injection
    functions, so all placement strategies share the same UI logic.
    """
    preset_props = context.scene.render_preset_settings

    # Map each mode enum value to its dedicated draw function
    draw_modes = {
        "LOAD_USER":    _draw_user_presets,
        "LOAD_NEW":     _draw_from_file,
        "LOAD_DEFAULT": _draw_default_presets,
        "SAVE_PRESET":  _draw_save_preset,
    }

    _draw_info_box(layout, preset_props)

    row = layout.row()
    row.scale_y = 1.25
    row.prop(preset_props, "load_mode_enum", expand=True)

    draw_fn = draw_modes.get(preset_props.load_mode_enum)
    if draw_fn:
        draw_fn(layout.box(), preset_props)


# =============================================================================
# Private Helper Drawing Functions
# =============================================================================

def _draw_info_box(layout, props):
    """
    Draws the status box at the top of the panel.

    Shows the currently loaded preset name and an Undo button when a preset
    has been applied; otherwise shows an idle placeholder message.
    """
    box = layout.box()

    if props.undo_data:
        row = box.row(align=True)
        row.label(text="Loaded:", icon="CHECKMARK")
        row.label(text="")
        row.operator(op_undo.RENDER_PRESET_OT_undo.bl_idname, text="Undo", icon="LOOP_BACK")

        row = box.row(align=True)
        row.scale_y = 0.6
        row.alert   = True
        row.label(text=f"{props.loaded_preset_name}")
        row.alert   = True
        row.scale_x = 0.25
    else:
        row = box.row(align=True)
        row.alignment = "LEFT"
        row.label(text="Loaded:", icon="INFO")
        row.label(text="No Preset Loaded yet.")


def _draw_user_presets(layout, props):
    """
    Draws the Load User Presets section.

    Renders either a compact dropdown or a scrollable UIList depending on
    the ``preset_display_style`` addon preference.
    """
    context = bpy.context
    prefs   = get_addon_preferences(context)
    display_style = prefs.preset_display_style if prefs else "DROPDOWN"

    # --- Shared header row ---
    row = layout.row(align=True)
    row.label(text="User Presets", icon="USER")

    if display_style == "LIST":
        row.label(text="")  # Spacer to push buttons to the right

    row.operator(op_user_presets.RENDER_PRESET_OT_refresh_user.bl_idname,       text="", icon="FILE_REFRESH")
    row.operator(op_delete.RENDER_PRESET_OT_remove_user_preset.bl_idname,       text="", icon="TRASH")

    # --- Display style: Dropdown (compact) ---
    if display_style == "DROPDOWN":
        col = layout.column(align=True)
        col.prop(props, "user_preset_enum", text="")
        col.operator(
            op_user_presets.RENDER_PRESET_OT_load_user.bl_idname,
            text="Load Selected User Preset",
            icon="IMPORT",
        )

    # --- Display style: Scrollable UIList ---
    else:
        # Requires 'user_presets_collection' (CollectionProperty) and
        # 'active_user_index' (IntProperty) on the scene PropertyGroup.
        layout.template_list(
            "RENDER_PRESET_UL_user_list",
            "",
            props, "user_presets_collection",
            props, "active_user_index",
            rows=5,
        )

        # Load button reads the active list index instead of the enum value
        layout.row().operator(
            "render_preset.load_from_list",
            text="Load Selected",
            icon="IMPORT",
        )


def _draw_from_file(layout, props):
    """Draws the Load from File section."""
    layout.label(text="Load Preset", icon="IMPORT")
    layout.operator(
        op_load.RENDER_PRESET_OT_load.bl_idname,
        icon="FILE_FOLDER",
        text="Load Preset from File",
    )


def _draw_default_presets(layout, props):
    """Draws the Load Default Presets section."""
    row = layout.row(align=True)
    row.label(text="Default Presets", icon="BLENDER")
    row.operator(
        op_user_presets.RENDER_PRESET_OT_refresh_defaults.bl_idname,
        text="",
        icon="FILE_REFRESH",
    )

    layout.prop(props, "default_preset_enum", text="")
    layout.operator(
        op_user_presets.RENDER_PRESET_OT_load_default.bl_idname,
        text="Load Selected Default",
    )


def _draw_save_preset(layout, props):
    """
    Draws the Save Preset section.

    Highlights the name field in red when a preset with that name already
    exists, and conditionally shows Octane-specific save toggles when the
    Octane render engine is available.
    """
    context = bpy.context
    layout.label(text="Save Preset", icon="EXPORT")

    col = layout.column(align=True)

    # --- Preset name input (with overwrite warning) ---
    split = col.split(factor=0.3, align=True)
    split.label(text="Name:")
    split.alert = props.preset_name_exists
    split.prop(props, "preset_name", text="")
    split.alert = False

    if props.preset_name_exists:
        warning_row       = col.row(align=True)
        warning_row.alert = True
        warning_row.label(
            text="Warning: Preset with this name already exists. Saving will overwrite.",
            icon="ERROR",
        )

    # --- Preset description input ---
    split = col.split(factor=0.3, align=True)
    split.label(text="Description:")
    split.prop(props, "preset_description", text="")

    col.separator(factor=0.5)

    # --- Engine scope toggles ---
    octane_available = is_engine_available(context, "octane")
    engine_label     = "Native Engines:" if octane_available else "Engines:"

    split = col.split(factor=0.3, align=True)
    split.label(text="")
    split.row(align=True).prop(props, "save_render_engine", text="Save Active Render Engine", toggle=True)

    col.separator(factor=1)
    split = col.split(factor=0.3, align=True)
    split.label(text=engine_label)
    row = split.row(align=True)
    row.prop(props, "save_cycles",    text="Cycles",    toggle=True)
    row.prop(props, "save_eevee",     text="EEVEE",     toggle=True)
    row.prop(props, "save_workbench", text="Workbench", toggle=True)

    # --- Octane-specific toggles (only shown when Octane is available) ---
    if octane_available:
        col.row(align=False).separator(factor=1.5)

        split = col.split(factor=0.3, align=True)
        split.label(text="Octane Render:")
        row = split.row(align=True)
        row.prop(props, "save_octane",            text="Render Properties", toggle=True)
        row.prop(props, "save_octane_view_layer", text="View Layer",        toggle=True)

        split = col.split(factor=0.3, align=True)
        split.label(text=" ")
        row = split.row(align=True)
        row.prop(props, "save_octane_imager", text="Imager",      toggle=True)
        row.prop(props, "save_octane_post",   text="Postprocess", toggle=True)

        col.row(align=False).separator(factor=1.5)

    # --- Scene-level toggles ---
    split = col.split(factor=0.3, align=True)
    split.label(text="Scene:")
    row = split.row(align=True)
    row.prop(props, "save_output",     text="Output",     toggle=True)
    row.prop(props, "save_view_layer", text="View Layer", toggle=True)
    row.prop(props, "save_scene",      text="Scene",      toggle=True)

    # --- User Custom Properties toggles ---
    col.row(align=False).separator(factor=1.5)
    split = col.split(factor=0.3, align=True)
    split.label(text="Custom:")
    row = split.row(align=True)
    row.prop(props, "save_user_custom", text="User's Custom Properties", toggle=True)


    col.separator(factor=1.2)

    # --- Action buttons ---
    col.operator(op_save.RENDER_PRESET_OT_save.bl_idname,              text="Save Preset to File...", icon="FILE_TICK")
    col.operator(op_save.RENDER_PRESET_OT_save_to_user_repo.bl_idname, icon="USER")

# =============================================================================
# Panel Option 1: Standard Panel (with header)
# =============================================================================

class RENDER_PRESET_PT_panel_normal(bpy.types.Panel):
    """
    The addon panel rendered as a standard, collapsible Blender panel.
    Visible only when the panel_location preference is set to 'PANEL'.
    """

    bl_label       = "Render Preset Manager"
    bl_idname      = "RENDER_PRESET_PT_panel_normal"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "render"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        prefs = get_addon_preferences(context)
        return prefs and prefs.panel_location == "PANEL"

    def draw_header(self, context):
        self.layout.label(text="", icon="FILE_TICK")

    def draw(self, context):
        draw_main_addon_ui(self.layout, context)


# =============================================================================
# Panel Option 2: Headerless Panel (HIDE_HEADER with built-in toggle)
# =============================================================================

class RENDER_PRESET_PT_panel_no_header(bpy.types.Panel):
    """
    The addon panel rendered without a Blender header, using a custom
    collapse toggle drawn inside a box instead.
    Visible only when the panel_location preference is set to 'HIDE_HEADER'.
    """

    bl_label       = "Render Preset Manager"
    bl_idname      = "RENDER_PRESET_PT_panel_no_header"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "render"
    bl_options     = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        prefs = get_addon_preferences(context)
        return prefs and prefs.panel_location == "HIDE_HEADER"

    def draw(self, context):
        preset_props = context.scene.render_preset_settings

        main_box = self.layout.box()

        # Custom collapsible header drawn inside the box
        row           = main_box.row()
        row.alignment = "LEFT"
        row.label(text="", icon="FILE_TICK")
        icon = "TRIA_DOWN" if preset_props.show_main_panel else "TRIA_RIGHT"
        row.prop(preset_props, "show_main_panel", text="Render Preset Manager", icon=icon, emboss=False)

        if preset_props.show_main_panel:
            draw_main_addon_ui(main_box, context)


# =============================================================================
# Panel Option 3: Prepend Injection
# =============================================================================

def draw_prepended_ui(self, context):
    """
    Injected via bpy.types.PROPERTIES_PT_*.prepend() to insert the addon UI
    above existing content in the Render Properties tab.
    Renders only when panel_location preference is set to 'PREPEND'.
    """
    prefs = get_addon_preferences(context)
    if not prefs or prefs.panel_location != "PREPEND":
        return

    preset_props = context.scene.render_preset_settings

    main_box      = self.layout.box()
    row           = main_box.row()
    row.alignment = "LEFT"
    row.label(text="", icon="FILE_TICK")
    icon = "TRIA_DOWN" if preset_props.show_main_panel else "TRIA_RIGHT"
    row.prop(preset_props, "show_main_panel", text="Render Preset Manager", icon=icon, emboss=False)

    if preset_props.show_main_panel:
        draw_main_addon_ui(main_box, context)


# =============================================================================
# Developer Tools Sub-Panel (Preferences)
# =============================================================================

class PREFERENCES_PT_developer_extras(bpy.types.Panel):
    """
    Sub-panel shown inside the addon preferences when developer_extras is enabled.
    Provides tools for validating and regenerating the manual render settings list.
    """

    bl_label      = "Developer Tools"
    bl_idname     = "PREFERENCES_PT_developer_extras"
    bl_space_type  = "PREFERENCES"
    bl_region_type = "WINDOW"
    bl_parent_id  = "k_tools_render_preset_manager_preferences"

    @classmethod
    def poll(cls, context):
        prefs = get_addon_preferences(context)
        return prefs and prefs.developer_extras

    def draw(self, context):
        layout = self.layout
        prefs  = get_addon_preferences(context)

        # --- Validation Tool ---
        box = layout.box()
        box.label(text="Validate Manual List:", icon="SHADERFX")
        box.operator("render_preset.validate_list", icon="FILE_REFRESH")

        # --- List Generator (Scraper) ---
        box = layout.box()
        box.label(text="Generate New List:", icon="LINENUMBERS_ON")

        split = box.split(factor=0.3)
        col_label  = split.column()
        col_widget = split.column()

        col_label.label(text="Source:")
        col_widget.prop(prefs, "dev_scraper_source_type", text="")

        col_label.label(text="Filter Path:")
        col_widget.prop(prefs, "dev_scraper_filter_path", text="")

        col_label.label(text="Depth:")
        col_widget.prop(prefs, "dev_scraper_max_depth", text="")

        box.operator("render_preset.generate_new_list", icon="TEXT")


# =============================================================================
# Registration
# =============================================================================

classes = (
    RENDER_PRESET_UL_user_list,
    RENDER_PRESET_PT_panel_normal,
    RENDER_PRESET_PT_panel_no_header,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)