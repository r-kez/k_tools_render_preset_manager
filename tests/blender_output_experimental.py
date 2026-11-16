"""Test opt-in Output discovery, preset roundtrip, and blacklist behavior."""

import json
import os
import sys
import tempfile
from types import SimpleNamespace

import bpy

addon_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(addon_dir))

import k_tools_render_preset_manager as addon
from k_tools_render_preset_manager import utils
from k_tools_render_preset_manager.operators.op_load import get_preset_label_map
from k_tools_render_preset_manager.operators.op_save import save_preset_to_file


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
addon.register()
bpy.utils.register_class(RENDER_PT_capture_future_setting)
prefs = SimpleNamespace(experimental_output_capture=True, blacklist_items=[])
utils.get_addon_preferences = lambda context: prefs
original_scene = bpy.context.scene
probe_scene = original_scene.copy()
new_path = 'render.use_lock_interface'

try:
    with bpy.context.temp_override(scene=probe_scene, view_layer=probe_scene.view_layers[0]):
        props = probe_scene.render_preset_settings
        props.preset_name = 'Experimental Output audit'
        for attribute in ('save_render_engine', 'save_cycles', 'save_eevee',
                          'save_workbench', 'save_view_layer', 'save_scene',
                          'save_octane', 'save_octane_view_layer',
                          'save_octane_imager', 'save_octane_post',
                          'save_user_custom'):
            setattr(props, attribute, False)
        props.save_output = True

        with tempfile.TemporaryDirectory() as directory:
            prefs.experimental_output_capture = False
            baseline_path = os.path.join(directory, 'output_baseline.json')
            success, message = save_preset_to_file(bpy.context, baseline_path)
            assert success, message
            with open(baseline_path, encoding='utf-8') as stream:
                baseline = json.load(stream)

            prefs.experimental_output_capture = True
            filepath = os.path.join(directory, 'output_experimental.json')
            success, message = save_preset_to_file(bpy.context, filepath)
            assert success, message
            with open(filepath, encoding='utf-8') as stream:
                preset = json.load(stream)

        saved = preset['render_presets']['BLENDER_OUTPUT']
        baseline_saved = baseline['render_presets']['BLENDER_OUTPUT']
        assert all(saved.get(path) == value for path, value in baseline_saved.items()), (
            'Experimental save lost legacy values')
        assert 'render.image_settings.file_format' in baseline_saved
        assert 'render.image_settings.file_format' in saved
        assert new_path in saved
        assert 'render.resolution_x' in saved
        panels = preset['categories']['BLENDER_OUTPUT']['panels']
        assert set(saved) == {
            path for panel in panels.values() for path in panel['properties']
        }
        assert new_path in panels['RENDER_PT_capture_future_setting']['properties']
        saved_label = panels['RENDER_PT_capture_future_setting']['property_labels'][new_path]
        assert saved_label.startswith('Future Output Setting:')
        assert new_path in dict(utils.get_all_render_settings(bpy.context)['BLENDER_OUTPUT'])
        prefs.experimental_output_capture = False
        assert get_preset_label_map(preset, bpy.context)[new_path] == saved_label
        prefs.experimental_output_capture = True

        original = probe_scene.render.use_lock_interface
        probe_scene.render.use_lock_interface = not original
        operation = bpy.ops.render_preset.load_confirm(
            preset_data=json.dumps(preset), load_engine='BLENDER_OUTPUT')
        assert operation == {'FINISHED'}
        assert probe_scene.render.use_lock_interface == original

        category_only = dict(preset)
        category_only.pop('render_presets')
        probe_scene.render.use_lock_interface = not original
        operation = bpy.ops.render_preset.load_confirm(
            preset_data=json.dumps(category_only), load_engine='BLENDER_OUTPUT')
        assert operation == {'FINISHED'}
        assert probe_scene.render.use_lock_interface == original

        prefs.blacklist_items.append(SimpleNamespace(path=new_path, is_enabled=False))
        probe_scene.render.use_lock_interface = not original
        operation = bpy.ops.render_preset.load_confirm(
            preset_data=json.dumps(preset), load_engine='BLENDER_OUTPUT')
        assert operation == {'FINISHED'}
        assert probe_scene.render.use_lock_interface != original, 'Direct load ignored blacklist'
finally:
    bpy.data.scenes.remove(probe_scene)
    bpy.utils.unregister_class(RENDER_PT_capture_future_setting)
    delattr(output_module, RENDER_PT_capture_future_setting.__name__)

print('OUTPUT_EXPERIMENTAL_OK ' + bpy.app.version_string)
