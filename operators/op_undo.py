import bpy
import json
from bpy.types import Operator
from ..utils import (
    set_nested_attr,
    )

# =============================================================================
# Undo Changes
# =============================================================================
class RENDER_PRESET_OT_undo(Operator):
    """Revert to the settings before the last preset was loaded"""
    bl_idname = "render_preset.undo"
    bl_label = "Undo Preset Load"
    bl_description = "Revert to the previous settings. This action cannot be undone"
    

    @classmethod
    def poll(cls, context):
        return context.scene.render_preset_settings.undo_data != ""

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        preset_props = context.scene.render_preset_settings
        
        previous_settings = json.loads(preset_props.undo_data)
        applied_count = 0

        for engine_name, settings in previous_settings.items():
            for path, value in settings.items():
                success, _ = set_nested_attr(context.scene, path, value)
                if success:
                    applied_count += 1

        preset_props.undo_data = ""
        preset_props.loaded_preset_name = ""
        preset_props.last_loaded_preset_path = ""     

        self.report({'INFO'}, f"Undo successful. Restored {applied_count} settings.")
        return {'FINISHED'}


classes = (
    RENDER_PRESET_OT_undo,
)    