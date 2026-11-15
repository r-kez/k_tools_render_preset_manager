"""Panel discovery for EEVEE, Workbench, View Layer and Scene, with a save/load roundtrip.

Run with: blender --background --factory-startup --python tests/blender_native_capture.py
"""

import json
import os
import sys
import tempfile
from types import SimpleNamespace

import bpy

addon_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(addon_dir))

import k_tools_render_preset_manager as addon
from k_tools_render_preset_manager import output_panel_capture, panel_scraper, utils
from k_tools_render_preset_manager.operators.op_save import save_preset_to_file
from k_tools_render_preset_manager.properties.function_list import RENDER_SETTINGS

EEVEE = 'BLENDER_EEVEE_NEXT' if bpy.app.version < (5, 0, 0) else 'BLENDER_EEVEE'
SAVE_FLAGS = {
    'CYCLES': 'save_cycles',
    'BLENDER_EEVEE': 'save_eevee',
    'BLENDER_WORKBENCH': 'save_workbench',
    'BLENDER_VIEW_LAYER': 'save_view_layer',
    'BLENDER_SCENE': 'save_scene',
}
# (category, engine, paths that must be captured in every supported version)
CASES = [
    ('BLENDER_EEVEE', EEVEE, {'render.film_transparent', 'view_settings.view_transform'}),
    ('BLENDER_WORKBENCH', 'BLENDER_WORKBENCH',
     {'display.shading.light', 'display.shading.show_cavity', 'display.render_aa'}),
    ('BLENDER_VIEW_LAYER', 'CYCLES',
     {'<ACTIVE_VIEW_LAYER>.use_pass_z', '<ACTIVE_VIEW_LAYER>.cycles.denoising_store_passes'}),
    ('BLENDER_VIEW_LAYER', EEVEE, {'<ACTIVE_VIEW_LAYER>.use_pass_z'}),
    ('BLENDER_SCENE', EEVEE, {'unit_settings.system', 'use_gravity'}),
    ('CYCLES', 'CYCLES', {'cycles.samples', 'cycles.device', 'render.use_simplify'}),
]
# Panels that need a GPU context only exist as errors in background mode.
BACKGROUND_ONLY_ERRORS = ('not available in background mode',)

addon.register()
prefs = SimpleNamespace(blacklist_items=[], **{attr: False for attr in utils.PANEL_CAPTURE_PREFS.values()})
utils.get_addon_preferences = lambda context: prefs
probe_scene = bpy.context.scene.copy()
report = []

try:
    with bpy.context.temp_override(scene=probe_scene, view_layer=probe_scene.view_layers[0]):
        props = probe_scene.render_preset_settings
        for category, engine, required in CASES:
            probe_scene.render.engine = engine
            before = {cat: utils.get_current_settings(cat, bpy.context) for cat in SAVE_FLAGS}
            capture = output_panel_capture.capture_panels(bpy.context, category)
            after = {cat: utils.get_current_settings(cat, bpy.context) for cat in SAVE_FLAGS}
            assert before == after, f'{category}: capture changed the scene'
            errors = [e for e in capture['errors']
                      if not any(marker in e for marker in BACKGROUND_ONLY_ERRORS)]
            assert not errors, (category, engine, errors)

            captured = {path for panel in capture['panels'] for path, _ in panel['properties']}
            assert required <= captured, (category, engine, required - captured)
            assert 'render.engine' not in captured, 'render.engine belongs to RENDER_ENGINE'
            assert not any(path.startswith('view_layers[') for path in captured), captured

            # A child panel is only captured when its parent panel is visible.
            ids = {panel['id'] for panel in capture['panels']}
            for panel in capture['panels']:
                parent = panel['parent_id']
                if parent and parent not in ids:
                    parent_cls = getattr(bpy.types, parent)
                    poll = getattr(parent_cls, 'poll', None)
                    ctx = output_panel_capture._DrawContext(bpy.context, parent_cls.bl_context)
                    assert poll is None or poll(ctx), f'{panel["id"]} shown under hidden {parent}'

            # Save with discovery on, change every captured toggle, load it back.
            setattr(prefs, utils.PANEL_CAPTURE_PREFS[category], True)
            panel_scraper.clear_scraper_cache()
            for flag in ('save_render_engine', 'save_output', 'save_octane',
                         'save_octane_view_layer', 'save_octane_imager', 'save_octane_post',
                         'save_user_custom', *SAVE_FLAGS.values()):
                setattr(props, flag, False)
            setattr(props, SAVE_FLAGS[category], True)
            props.preset_name = f'{category} roundtrip'
            with tempfile.TemporaryDirectory() as directory:
                filepath = os.path.join(directory, 'preset.json')
                success, message = save_preset_to_file(bpy.context, filepath)
                assert success, message
                with open(filepath, encoding='utf-8') as stream:
                    preset = json.load(stream)
            saved = preset['render_presets'][category]
            legacy = {path for path, _ in RENDER_SETTINGS[category]}
            assert legacy & set(before[category]) <= set(saved), 'Discovery lost legacy values'
            assert captured <= set(saved), (category, captured - set(saved))

            toggles = [path for path in sorted(captured) if isinstance(saved[path], bool)]
            changed = []
            for path in toggles:
                try:
                    utils.set_nested_attr(probe_scene, path, not saved[path])
                    if utils.get_nested_attr(probe_scene, path) != saved[path]:
                        changed.append(path)
                except Exception:
                    pass
            assert changed, f'{category}: no captured toggle could be changed'
            result = bpy.ops.render_preset.load_confirm(
                preset_data=json.dumps(preset), load_engine=category)
            assert result == {'FINISHED'}
            not_restored = [path for path in changed
                            if utils.get_nested_attr(probe_scene, path) != saved[path]]
            assert not not_restored, (category, engine, not_restored)

            setattr(prefs, utils.PANEL_CAPTURE_PREFS[category], False)
            report.append(f'{category}@{engine}: {len(capture["panels"])} panels '
                          f'{len(captured)} props {len(changed)} toggles restored')

        # Presets saved by older versions still contain eevee.use_bloom. In 4.2
        # setting it also cleared Shadows and other flags, so it must be ignored.
        probe_scene.render.engine = EEVEE
        probe_scene.eevee.use_shadows = True
        probe_scene.eevee.use_taa_reprojection = True
        old_preset = {'preset_name': 'old', 'render_presets': {'BLENDER_EEVEE': {
            'eevee.use_shadows': True, 'eevee.use_taa_reprojection': True,
            'eevee.use_bloom': False, 'eevee.bloom_intensity': 0.5}}}
        assert bpy.ops.render_preset.load_confirm(
            preset_data=json.dumps(old_preset), load_engine='BLENDER_EEVEE') == {'FINISHED'}
        assert probe_scene.eevee.use_shadows and probe_scene.eevee.use_taa_reprojection
        from k_tools_render_preset_manager.operators.op_load import compare_settings
        assert 'eevee.use_bloom' not in compare_settings({}, old_preset['render_presets']['BLENDER_EEVEE'])

        # Each category's audit report is written.
        for category in SAVE_FLAGS:
            assert bpy.ops.render_preset.audit_output_panels(category=category) == {'FINISHED'}
finally:
    bpy.data.scenes.remove(probe_scene)
    panel_scraper.clear_scraper_cache()

print(f'NATIVE_CAPTURE_OK {bpy.app.version_string} | ' + ' | '.join(report))
