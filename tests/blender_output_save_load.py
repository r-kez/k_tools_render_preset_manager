"""Check the existing Output preset save/load path in a disposable scene."""

import json
import os
import sys
import tempfile

import bpy

addon_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(addon_dir))

import k_tools_render_preset_manager as addon
from k_tools_render_preset_manager import utils
from k_tools_render_preset_manager.operators.op_save import save_preset_to_file


addon.register()
assert utils.get_addon_preferences(bpy.context) is None
# This checkout is imported directly rather than enabled through Blender's add-on
# manager, so it has no AddonPreferences entry in the factory-startup process.
utils.ADDON_NAME = ''
original_scene = bpy.context.scene
probe_scene = original_scene.copy()
result = {'version': bpy.app.version_string}
try:
    with bpy.context.temp_override(scene=probe_scene, view_layer=probe_scene.view_layers[0]):
        props = probe_scene.render_preset_settings
        props.preset_name = 'Output roundtrip audit'
        for attribute in ('save_render_engine', 'save_cycles', 'save_eevee',
                          'save_workbench', 'save_view_layer', 'save_scene',
                          'save_octane', 'save_octane_view_layer',
                          'save_octane_imager', 'save_octane_post',
                          'save_user_custom'):
            setattr(props, attribute, False)
        props.save_output = True

        with tempfile.TemporaryDirectory() as directory:
            filepath = os.path.join(directory, 'output.json')
            success, message = save_preset_to_file(bpy.context, filepath)
            assert success, message
            with open(filepath, encoding='utf-8') as stream:
                preset = json.load(stream)

        saved = preset['render_presets']['BLENDER_OUTPUT']
        result['saved'] = len(saved)
        assert preset['categories']['BLENDER_OUTPUT']['panels']
        original_resolution = probe_scene.render.resolution_x
        assert saved['render.resolution_x'] == original_resolution
        probe_scene.render.resolution_x = 1777
        assert probe_scene.render.resolution_x != original_resolution
        operation = bpy.ops.render_preset.load_confirm(
            preset_data=json.dumps(preset), load_engine='BLENDER_OUTPUT')
        result['operation'] = sorted(operation)
        result['restored'] = probe_scene.render.resolution_x == original_resolution
        assert result['restored']
finally:
    bpy.data.scenes.remove(probe_scene)

assert bpy.context.scene == original_scene
print('OUTPUT_SAVE_LOAD_RESULT ' + json.dumps(result, sort_keys=True))
