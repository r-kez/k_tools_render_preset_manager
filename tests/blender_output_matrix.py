"""Exercise Output panels and captured paths across available Blender UI states.

Run inside each supported build with --background --factory-startup --python.
All property changes happen on a disposable copy of the active scene.
"""

import json
import os
import sys

import bpy

addon_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(addon_dir))

from k_tools_render_preset_manager import utils
from k_tools_render_preset_manager.output_panel_capture import capture_output_panels
from k_tools_render_preset_manager.properties.function_list import RENDER_SETTINGS


result = {
    'version': bpy.app.version_string,
    'states': 0,
    'paths': 0,
    'capture_errors': [],
    'path_errors': [],
    'unavailable_states': [],
}
probe_scene = bpy.context.scene.copy()
paths = {}

try:
    with bpy.context.temp_override(scene=probe_scene, view_layer=probe_scene.view_layers[0]):
        render = probe_scene.render
        image = render.image_settings

        def scan(label):
            capture = capture_output_panels(bpy.context)
            result['states'] += 1
            result['capture_errors'].extend(f'{label}: {error}' for error in capture['errors'])
            for panel in capture['panels']:
                for path, _ in panel['properties']:
                    paths.setdefault(path, set()).add(panel['id'])

        for item in image.bl_rna.properties['file_format'].enum_items:
            try:
                image.file_format = item.identifier
                scan(f'file_format={item.identifier}')
            except (TypeError, ValueError) as exc:
                result['unavailable_states'].append(f'{item.identifier}: {exc}')

        image.file_format = 'PNG'
        render.use_multiview = True
        scan('PNG + multiview')
        render.use_multiview = False
        for item in image.bl_rna.properties['color_management'].enum_items:
            try:
                image.color_management = item.identifier
                scan(f'PNG + color_management={item.identifier}')
            except (TypeError, ValueError) as exc:
                result['unavailable_states'].append(f'color_management={item.identifier}: {exc}')

        render.fps = 37
        scan('PNG + custom frame rate')
        try:
            render.ppm_base = 0.0123
            scan('PNG + custom pixel density')
        except (AttributeError, TypeError, ValueError) as exc:
            result['unavailable_states'].append(f'custom pixel density: {exc}')

        if 'FFMPEG' in {item.identifier for item in image.bl_rna.properties['file_format'].enum_items}:
            try:
                image.file_format = 'FFMPEG'
            except (TypeError, ValueError) as exc:
                result['unavailable_states'].append(f'FFMPEG: {exc}')
            else:
                for item in render.ffmpeg.bl_rna.properties['format'].enum_items:
                    try:
                        render.ffmpeg.format = item.identifier
                        scan(f'FFMPEG format={item.identifier}')
                    except (TypeError, ValueError) as exc:
                        result['unavailable_states'].append(f'FFMPEG format={item.identifier}: {exc}')
                for item in render.ffmpeg.bl_rna.properties['codec'].enum_items:
                    try:
                        render.ffmpeg.codec = item.identifier
                        scan(f'FFMPEG codec={item.identifier}')
                    except (TypeError, ValueError) as exc:
                        result['unavailable_states'].append(f'FFMPEG codec={item.identifier}: {exc}')

        result['paths'] = len(paths)
        result['duplicate_paths'] = {
            path: sorted(panels) for path, panels in paths.items()
            if len(panels) > 1
        }
        legacy = {path for path, _ in RENDER_SETTINGS['BLENDER_OUTPUT']}
        key = lambda path: tuple(utils.parse_path_to_steps(path))
        legacy_keys = {key(path) for path in legacy}
        captured_keys = {key(path) for path in paths}
        result['legacy_paths'] = len(legacy)
        result['legacy_unaccounted'] = sorted(
            path for path in legacy if key(path) not in captured_keys)
        result['legacy_unaccounted_readable'] = [
            path for path in result['legacy_unaccounted']
            if utils.get_nested_attr(probe_scene, path) is not None
        ]
        result['captured_not_legacy'] = sorted(
            path for path in paths if key(path) not in legacy_keys)
        snapshot = {}
        for path, panels in sorted(paths.items()):
            value = utils.get_nested_attr(probe_scene, path)
            if value is None:
                result['path_errors'].append(f'{path}: unreadable ({sorted(panels)})')
                continue
            snapshot[path] = value
            success, error = utils.set_nested_attr(probe_scene, path, value)
            if not success:
                result['path_errors'].append(f'{path}: {error} ({sorted(panels)})')
        try:
            json.dumps(snapshot)
        except (TypeError, ValueError) as exc:
            result['path_errors'].append(f'JSON serialization: {exc}')

        for path, changed in (
                ('render.resolution_x', 1777),
                ('render.use_file_extension', not render.use_file_extension),
                ('render.filepath', '//output_capture_roundtrip/')):
            if path not in paths:
                result['path_errors'].append(f'{path}: missing from captured paths')
                continue
            original = utils.get_nested_attr(probe_scene, path)
            success, error = utils.set_nested_attr(probe_scene, path, changed)
            if not success or utils.get_nested_attr(probe_scene, path) != changed:
                result['path_errors'].append(f'{path}: change failed: {error}')
                continue
            success, error = utils.set_nested_attr(probe_scene, path, original)
            if not success or utils.get_nested_attr(probe_scene, path) != original:
                result['path_errors'].append(f'{path}: restore failed: {error}')
finally:
    bpy.data.scenes.remove(probe_scene)

print('OUTPUT_MATRIX_RESULT ' + json.dumps(result, sort_keys=True))
assert not result['capture_errors'], result['capture_errors']
assert not result['path_errors'], result['path_errors']
