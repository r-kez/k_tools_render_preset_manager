"""Run against an extension installed into an isolated Blender user profile."""

import json
import os
import tempfile
from importlib import import_module

import bpy


addon_id = 'bl_ext.user_default.k_tools_render_preset_manager'
assert addon_id in bpy.context.preferences.addons, list(bpy.context.preferences.addons.keys())
prefs = bpy.context.preferences.addons[addon_id].preferences
assert not prefs.experimental_output_capture
assert hasattr(bpy.ops.render_preset, 'audit_output_panels')

baseline = {item.path for item in prefs.blacklist_items}
prefs.experimental_output_capture = True
assert prefs.experimental_output_capture
enabled = {item.path for item in prefs.blacklist_items}
assert 'render.resolution_x' in enabled
assert baseline <= enabled
new_path = 'display_settings.display_device'
assert new_path in enabled

props = bpy.context.scene.render_preset_settings
props.preset_name = 'Installed extension audit'
for attribute in ('save_render_engine', 'save_cycles', 'save_eevee',
                  'save_workbench', 'save_view_layer', 'save_scene',
                  'save_octane', 'save_octane_view_layer',
                  'save_octane_imager', 'save_octane_post',
                  'save_user_custom'):
    setattr(props, attribute, False)
props.save_output = True
save_preset_to_file = import_module(addon_id + '.operators.op_save').save_preset_to_file
with tempfile.TemporaryDirectory() as directory:
    filepath = os.path.join(directory, 'installed_output.json')
    success, message = save_preset_to_file(bpy.context, filepath)
    assert success, message
    with open(filepath, encoding='utf-8') as stream:
        preset = json.load(stream)
assert new_path in preset['render_presets']['BLENDER_OUTPUT']
assert any(new_path in panel['properties']
           for panel in preset['categories']['BLENDER_OUTPUT']['panels'].values())

assert bpy.ops.render_preset.audit_output_panels() == {'FINISHED'}
assert bpy.data.texts.get('Render_Preset_Output_Panel_Audit') is not None

prefs.experimental_output_capture = False
assert not prefs.experimental_output_capture
assert enabled <= {item.path for item in prefs.blacklist_items}

item = next(item for item in prefs.blacklist_items if item.path == new_path)
item.is_enabled = False
assert bpy.ops.render_preset.sync_blacklist() == {'FINISHED'}
assert not next(item for item in prefs.blacklist_items
                if item.path == new_path).is_enabled
prefs.experimental_output_capture = True
assert not next(item for item in prefs.blacklist_items
                if item.path == new_path).is_enabled

print('EXTENSION_PROFILE_RESULT ' + json.dumps({
    'version': bpy.app.version_string,
    'addon_id': addon_id,
    'baseline': len(baseline),
    'enabled': len(enabled),
}, sort_keys=True))
