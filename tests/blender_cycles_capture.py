"""Run with: blender --background --factory-startup --python tests/blender_cycles_capture.py"""

import os
import sys
from types import SimpleNamespace

import bpy

addon_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(addon_dir))

import k_tools_render_preset_manager as addon
from k_tools_render_preset_manager import output_panel_capture, panel_scraper, utils
from k_tools_render_preset_manager.properties.function_list import RENDER_SETTINGS

scene = bpy.context.scene

# Cycles panels are only captured while Cycles is the active engine.
scene.render.engine = 'BLENDER_WORKBENCH'
idle = output_panel_capture.capture_panels(bpy.context, 'CYCLES')
assert not idle['panels'] and idle['errors'], idle

scene.render.engine = 'CYCLES'
before = utils.get_current_settings('CYCLES', bpy.context)
capture = output_panel_capture.capture_panels(bpy.context, 'CYCLES')
assert utils.get_current_settings('CYCLES', bpy.context) == before, 'Capture changed the scene'
assert not capture['errors'], capture['errors']

by_id = {panel['id']: {path for path, _ in panel['properties']}
         for panel in capture['panels']}
assert all(panel_id.startswith('CYCLES_RENDER_PT_') for panel_id in by_id), by_id.keys()
assert 'cycles.samples' in by_id['CYCLES_RENDER_PT_sampling_render']
assert 'cycles.preview_samples' in by_id['CYCLES_RENDER_PT_sampling_viewport']
assert 'cycles.max_bounces' in by_id['CYCLES_RENDER_PT_light_paths_max_bounces']
assert any('template_curve_mapping' in reason for reason in capture['skipped'])

# Parent panels are listed before their children, as in Blender's UI.
order = [panel['id'] for panel in capture['panels']]
for panel in capture['panels']:
    if panel['parent_id'] in order:
        assert order.index(panel['parent_id']) < order.index(panel['id']), panel['id']

# The save list keeps every legacy path and adds drawn ones only once.
prefs = SimpleNamespace(experimental_output_capture=False,
                        experimental_cycles_capture=True, blacklist_items=[])
original_get_prefs = utils.get_addon_preferences
utils.get_addon_preferences = lambda context: prefs
try:
    full = utils.get_all_render_settings(bpy.context)
    paths = [path for path, _ in full['CYCLES']]
    assert {path for path, _ in RENDER_SETTINGS['CYCLES']} <= set(paths)
    cycles_keys = [tuple(utils.parse_path_to_steps(path)) for path in paths]
    added = [path for path in paths
             if path not in {p for p, _ in RENDER_SETTINGS['CYCLES']}]
    for path in added:
        assert cycles_keys.count(tuple(utils.parse_path_to_steps(path))) == 1, path
    # Settings Cycles draws are saved with Cycles even if another category lists them.
    assert 'render.use_motion_blur' in paths

    panel_scraper.clear_scraper_cache()
    scraped = panel_scraper.scrape_category_panels('CYCLES', bpy.context)
    scraped_by_id = {panel['id']: {item[0] for item in panel['properties']}
                     for panel in scraped}
    assert 'cycles.samples' in scraped_by_id['CYCLES_RENDER_PT_sampling_render']
    scraped_keys = [tuple(utils.parse_path_to_steps(item[0]))
                    for panel in scraped for item in panel['properties']]
    assert len(scraped_keys) == len(set(scraped_keys)), 'Path shown in two panels'
finally:
    utils.get_addon_preferences = original_get_prefs
    panel_scraper.clear_scraper_cache()

addon.register()
assert bpy.ops.render_preset.audit_output_panels(category='CYCLES') == {'FINISHED'}
report = bpy.data.texts['Render_Preset_Cycles_Panel_Audit'].as_string()
assert 'CYCLES_RENDER_PT_sampling_render' in report
assert 'UI state audit' not in report

print(f"CYCLES_CAPTURE_OK {bpy.app.version_string} {len(capture['panels'])} panels "
      f"{sum(len(p['properties']) for p in capture['panels'])} properties "
      f"{len(added)} added to save list")
