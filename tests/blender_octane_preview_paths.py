"""Octane preview imager/postprocess presets: every saved path is read and restored.

Run with: blender --background --factory-startup --python tests/blender_octane_preview_paths.py
Builds without the Octane add-on print OCTANE_PREVIEW_PATHS_SKIP and pass.

Regression: since v2.0.0, "oct_view_cam." paths were resolved against
scene.camera.data, but oct_view_cam is scene.oct_view_cam, so OCTANE_IMAGER
presets kept 2 of 35 settings and OCTANE_POST 1 of 26.
"""

import json
import os
import sys
import tempfile
from types import SimpleNamespace

import bpy

addon_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(addon_dir))

if 'octane' not in bpy.context.preferences.addons:
    print(f'OCTANE_PREVIEW_PATHS_SKIP {bpy.app.version_string}: Octane add-on not available')
    sys.exit(0)

import k_tools_render_preset_manager as addon
from k_tools_render_preset_manager import utils
from k_tools_render_preset_manager.operators.op_load import are_values_equal
from k_tools_render_preset_manager.operators.op_save import save_preset_to_file
from k_tools_render_preset_manager.properties.function_list import RENDER_SETTINGS

addon.register()
prefs = SimpleNamespace(blacklist_items=[], **{attr: True for attr in utils.PANEL_CAPTURE_PREFS.values()})
utils.get_addon_preferences = lambda context: prefs
probe_scene = bpy.context.scene.copy()
report = {}

try:
    with bpy.context.temp_override(scene=probe_scene, view_layer=probe_scene.view_layers[0]):
        probe_scene.render.engine = 'octane'
        props = probe_scene.render_preset_settings
        props.preset_name = 'Octane preview paths'
        for category, flag in (('OCTANE_IMAGER', 'save_octane_imager'), ('OCTANE_POST', 'save_octane_post')):
            legacy = {path for path, _ in RENDER_SETTINGS[category]}
            readable = utils.get_current_settings(category, bpy.context)
            assert legacy <= set(readable), (category, sorted(legacy - set(readable)))

            for name in ('save_render_engine', 'save_cycles', 'save_eevee', 'save_workbench',
                         'save_output', 'save_view_layer', 'save_scene', 'save_octane',
                         'save_octane_view_layer', 'save_octane_imager', 'save_octane_post',
                         'save_user_custom'):
                setattr(props, name, name == flag)
            with tempfile.TemporaryDirectory() as directory:
                filepath = os.path.join(directory, 'preview.json')
                success, message = save_preset_to_file(bpy.context, filepath)
                assert success, message
                with open(filepath, encoding='utf-8') as stream:
                    preset = json.load(stream)
            saved = preset['render_presets'][category]
            assert legacy <= set(saved), (category, sorted(legacy - set(saved)))

            changed = []
            for path in sorted(p for p in legacy if p.startswith('oct_view_cam.')):
                value = saved[path]
                if isinstance(value, bool):
                    new_value = not value
                elif isinstance(value, (int, float)):
                    new_value = value + 1 if isinstance(value, int) else value * 0.5 + 0.25
                else:
                    continue
                utils.set_nested_attr(probe_scene, path, new_value)
                if utils.read_setting_value(probe_scene, path) != value:
                    changed.append(path)
            assert len(changed) >= 10, (category, changed)
            assert bpy.ops.render_preset.load_confirm(
                preset_data=json.dumps(preset), load_engine=category) == {'FINISHED'}
            not_restored = [path for path in changed
                            if not are_values_equal(utils.read_setting_value(probe_scene, path), saved[path])]
            assert not not_restored, (category, not_restored)
            report[category] = f'{len(saved)} saved, {len(changed)} restored'
finally:
    bpy.data.scenes.remove(probe_scene)

print(f'OCTANE_PREVIEW_PATHS_OK {bpy.app.version_string} {report}')
