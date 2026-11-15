"""Save and load a preset through the add-on's real UI flow, with screenshots.

Saves with "Save to User Repository", changes the scene, then loads through
render_preset.load -> preview dialog -> OK (confirmed with a simulated Return key),
and checks every saved value came back, including settings only panel discovery finds.

Install the extension into a profile first (tests/run_all_builds.sh leaves one per build in
<out_dir>/profile/<build>), open any .blend so the splash is skipped, then run:
  BLENDER_USER_RESOURCES=<profile> blender file.blend --enable-event-simulate
      --window-geometry 0 0 1600 1000 --python tests/blender_gui_save_load.py -- <out_dir>
Blender quits by itself; results.json and the PNGs land in <out_dir>.
"""
import bpy, os, sys, json, traceback
from importlib import import_module

OUT = sys.argv[sys.argv.index('--') + 1]
PRESETS = os.path.join(OUT, 'presets')
os.makedirs(PRESETS, exist_ok=True)
ADDON = 'bl_ext.user_default.k_tools_render_preset_manager'
TOGGLES = ['experimental_output_capture', 'experimental_cycles_capture', 'experimental_eevee_capture',
           'experimental_workbench_capture', 'experimental_view_layer_capture', 'experimental_scene_capture']
SAVED = ('save_render_engine', 'save_cycles', 'save_output', 'save_view_layer', 'save_scene')
results = {'version': bpy.app.version_string, 'failures': [], 'shots': []}
state = {}


def log(msg):
    print('GUI_SAVE_LOAD', msg, flush=True)


def fail(msg):
    results['failures'].append(msg)
    log('FAIL ' + msg)


def window():
    return bpy.context.window_manager.windows[0]


def big_area():
    return max(window().screen.areas, key=lambda a: a.width * a.height)


def override():
    area = big_area()
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return bpy.context.temp_override(window=window(), area=area, region=region)


def shot(name):
    path = os.path.join(OUT, f'{name}.png')
    with override():
        bpy.ops.screen.screenshot(filepath=path)
    results['shots'].append(path)


def simulate(event_type, value='PRESS', **kwargs):
    window().event_simulate(type=event_type, value=value, **kwargs)


def utils():
    return import_module(ADDON + '.utils')


def step_setup():
    prefs = bpy.context.preferences.addons[ADDON].preferences
    for attr in TOGGLES:
        setattr(prefs, attr, True)
    prefs.user_presets_path = PRESETS
    prefs.panel_location = 'HIDE_HEADER'  # expandable through show_main_panel
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    big_area().type = 'PROPERTIES'


def step_scene_values():
    big_area().spaces.active.context = 'RENDER'
    scene = bpy.context.scene
    u = utils()
    legacy = import_module(ADDON + '.properties.function_list').RENDER_SETTINGS
    full = u.get_all_render_settings(bpy.context)
    # Settings only panel discovery finds, so the roundtrip covers them too.
    discovered = []
    for category in ('CYCLES', 'BLENDER_VIEW_LAYER', 'BLENDER_OUTPUT', 'BLENDER_SCENE'):
        known = {path for path, _ in legacy[category]}
        for path, _ in full[category]:
            if path not in known and isinstance(u.get_nested_attr(scene, path), bool):
                discovered.append((category, path))
    state['discovered'] = discovered
    scene.cycles.samples = 123
    scene.render.film_transparent = True
    scene.unit_settings.scale_length = 2.0
    props = scene.render_preset_settings
    props.preset_name = 'GUI Roundtrip'
    props.show_main_panel = True
    for flag in ('save_render_engine', 'save_cycles', 'save_eevee', 'save_workbench', 'save_output',
                 'save_view_layer', 'save_scene', 'save_octane', 'save_octane_view_layer',
                 'save_octane_imager', 'save_octane_post', 'save_user_custom'):
        setattr(props, flag, flag in SAVED)
    log(f'{len(discovered)} discovered toggles in save scope')


def step_save():
    with override():
        result = bpy.ops.render_preset.save_to_user_repo()
    path = os.path.join(PRESETS, 'GUI_Roundtrip.json')
    if result != {'FINISHED'} or not os.path.exists(path):
        fail(f'save_to_user_repo returned {result}, file exists: {os.path.exists(path)}')
        return
    with open(path, encoding='utf-8') as stream:
        preset = json.load(stream)
    state['path'], state['preset'] = path, preset
    # Nothing changed since saving, so the preview must have nothing to show.
    are_values_equal = import_module(ADDON + '.operators.op_load').are_values_equal
    phantom = [p for values in preset['render_presets'].values() for p, v in values.items()
               if not are_values_equal(utils().read_setting_value(bpy.context.scene, p), v)]
    if phantom:
        fail(f'preview would list unchanged settings: {phantom}')
    flat = preset['render_presets']
    for category, discovered_path in state['discovered']:
        if discovered_path not in flat.get(category, {}):
            fail(f'{discovered_path} missing from saved {category}')
    panels = preset['categories']['CYCLES']['panels']
    results['saved'] = {cat: len(values) for cat, values in flat.items()}
    results['cycles_panel_labels'] = [p['label'] for p in panels.values()][:12]
    log(f"saved {results['saved']}")


def step_change_scene():
    scene = bpy.context.scene
    u = utils()
    scene.cycles.samples = 7
    scene.render.film_transparent = False
    scene.unit_settings.scale_length = 1.0
    changed = []
    for category, path in state['discovered']:
        saved = state['preset']['render_presets'][category].get(path)
        if isinstance(saved, bool):
            u.set_nested_attr(scene, path, not saved)
            if u.get_nested_attr(scene, path) != saved:
                changed.append((category, path))
    state['changed'] = changed
    log(f'changed {len(changed)} discovered toggles')


def step_open_preview_from_file():
    # The real "Load Preset" path: read file -> preview dialog.
    simulate('MOUSEMOVE', 'NOTHING', x=800, y=500)
    with override():
        bpy.ops.render_preset.load('EXEC_DEFAULT', filepath=state['path'])


def step_close_dialog():
    simulate('ESC')


def step_open_preview_expanded():
    simulate('MOUSEMOVE', 'NOTHING', x=800, y=500)
    with override():
        bpy.ops.render_preset.load_preview('INVOKE_DEFAULT', load_engine='ALL',
                                           show_cycles_changes=True, show_view_layer_changes=True,
                                           show_scene_changes=True, show_output_changes=True)


def step_confirm():
    simulate('RET')


def step_verify():
    scene = bpy.context.scene
    u = utils()
    expected = {'cycles.samples': 123, 'render.film_transparent': True, 'unit_settings.scale_length': 2.0}
    for path, value in expected.items():
        current = u.get_nested_attr(scene, path)
        if abs(current - value) > 1e-6 if isinstance(value, float) else current != value:
            fail(f'{path} is {current}, expected {value}')
    not_restored = [path for category, path in state['changed']
                    if u.get_nested_attr(scene, path) != state['preset']['render_presets'][category][path]]
    if not_restored:
        fail(f'discovered toggles not restored: {not_restored}')
    results['restored_discovered'] = len(state['changed']) - len(not_restored)
    log(f"restored {results['restored_discovered']}/{len(state['changed'])} discovered toggles")


def finish():
    with open(os.path.join(OUT, 'results.json'), 'w') as stream:
        json.dump(results, stream, indent=1)
    log('DONE ' + ('FAIL' if results['failures'] else 'OK'))
    bpy.ops.wm.quit_blender()


STEPS = [
    step_setup, step_scene_values, lambda: shot('1_render_tab_save'),
    step_save, step_change_scene,
    step_open_preview_from_file, lambda: shot('2_preview_from_file'), step_close_dialog,
    step_open_preview_expanded, lambda: shot('3_preview_expanded'), step_confirm,
    step_verify, lambda: shot('4_after_load'),
    finish,
]


def run_next():
    if not STEPS:
        return None
    step = STEPS.pop(0)
    try:
        step()
    except Exception:
        fail(traceback.format_exc())
        if step is finish:
            return None
    return 1.5


bpy.app.timers.register(run_next, first_interval=2.0)
