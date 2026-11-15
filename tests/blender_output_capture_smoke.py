"""Run with: blender --background --factory-startup --python tests/blender_output_capture_smoke.py"""

import os
import sys

import bpy

addon_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(addon_dir))

import k_tools_render_preset_manager as addon
from k_tools_render_preset_manager import output_panel_capture, utils
from k_tools_render_preset_manager.properties.function_list import RENDER_SETTINGS


before_capture = utils.get_current_settings('BLENDER_OUTPUT', bpy.context)
capture = output_panel_capture.capture_output_panels(bpy.context)
assert utils.get_current_settings('BLENDER_OUTPUT', bpy.context) == before_capture
assert not capture['errors'], capture['errors']
by_id = {panel['id']: {path for path, _ in panel['properties']}
         for panel in capture['panels']}
assert 'render.resolution_x' in by_id['RENDER_PT_format']
assert 'render.filepath' in by_id['RENDER_PT_output']
assert not any('render.image_settings.file_format' in paths
               for paths in by_id.values())
assert any('template_image_settings' in reason
           for reason in capture['skipped'])

unlisted_path = 'render.use_lock_interface'
assert unlisted_path not in {path for path, _ in RENDER_SETTINGS['BLENDER_OUTPUT']}


class RENDER_PT_capture_future_setting(bpy.types.Panel):
    bl_label = 'Future Output Setting'
    bl_idname = 'RENDER_PT_capture_future_setting'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    def draw(self, context):
        self.layout.prop(context.scene.render, 'use_lock_interface')


RENDER_PT_capture_future_setting.__module__ = 'bl_ui.properties_output'
output_module = sys.modules['bl_ui.properties_output']
setattr(output_module, RENDER_PT_capture_future_setting.__name__,
        RENDER_PT_capture_future_setting)
bpy.utils.register_class(RENDER_PT_capture_future_setting)
try:
    future_capture = output_panel_capture.capture_output_panels(bpy.context)
    future_panel = next(panel for panel in future_capture['panels']
                        if panel['id'] == 'RENDER_PT_capture_future_setting')
    assert unlisted_path in {path for path, _ in future_panel['properties']}
finally:
    bpy.utils.unregister_class(RENDER_PT_capture_future_setting)
    delattr(output_module, RENDER_PT_capture_future_setting.__name__)
assert not any(panel['id'] == 'RENDER_PT_capture_future_setting'
               for panel in output_panel_capture.capture_output_panels(bpy.context)['panels'])

original_scene = bpy.context.scene
original_format = original_scene.render.image_settings.file_format
variants = output_panel_capture.capture_output_states(bpy.context)
assert bpy.context.scene == original_scene
assert original_scene.render.image_settings.file_format == original_format
assert utils.get_current_settings('BLENDER_OUTPUT', bpy.context) == before_capture
assert {'PNG', 'OpenEXR'} <= {state['label'] for state in variants['states']}
assert all(not state['capture']['errors'] for state in variants['states']), variants
multiview = next(state for state in variants['states']
                 if state['label'] == 'PNG with multiple views')
assert any('template_image_views' in reason
           for reason in multiview['capture']['skipped'])

addon.register()
assert bpy.ops.render_preset.audit_output_panels() == {'FINISHED'}
report = bpy.data.texts['Render_Preset_Output_Panel_Audit'].as_string()
assert 'RENDER_PT_format' in report
assert 'render.resolution_x' in report
assert 'Capture errors\n\nTemplate calls' in report
assert 'UI state audit' in report

across_states = {path for state in variants['states']
                 for panel in state['capture']['panels']
                 for path, _ in panel['properties']}
print(f"OUTPUT_CAPTURE_SMOKE_OK {bpy.app.version_string} "
      f"{len(capture['panels'])} panels "
      f"{sum(len(panel['properties']) for panel in capture['panels'])} properties "
      f"{len(across_states)} across states "
      f"{len(capture['skipped'])} explicit gaps")
