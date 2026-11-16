"""Check that syncing settings keeps disabled paths from older presets."""

import os
import sys
from types import SimpleNamespace

import bpy

addon_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(addon_dir))

import k_tools_render_preset_manager as addon
from k_tools_render_preset_manager import utils


class Items(list):
    def add(self):
        item = SimpleNamespace(path='', name='', category='', is_enabled=True)
        self.append(item)
        return item


addon.register()
items = Items([
    SimpleNamespace(path='render.use_lock_interface',
                    name='Output: Lock Interface',
                    category='BLENDER_OUTPUT', is_enabled=False),
])
prefs = SimpleNamespace(blacklist_items=items)
utils.get_addon_preferences = lambda context: prefs
settings = {'BLENDER_OUTPUT': [('render.resolution_x', 'Format: Resolution X')]}
utils.get_all_render_settings = lambda context=None: settings

assert bpy.ops.render_preset.sync_blacklist() == {'FINISHED'}
assert {item.path: item.is_enabled for item in items} == {
    'render.resolution_x': True,
    'render.use_lock_interface': False,
}

settings['BLENDER_OUTPUT'].append(
    ('render.use_lock_interface', 'Output: Lock Interface'))
assert bpy.ops.render_preset.sync_blacklist() == {'FINISHED'}
assert len(items) == 2
assert {item.path: item.is_enabled for item in items} == {
    'render.resolution_x': True,
    'render.use_lock_interface': False,
}
print('BLACKLIST_SYNC_OK ' + bpy.app.version_string)
