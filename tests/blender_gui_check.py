"""Drive the installed extension inside Blender's real UI (GPU, windows) and take screenshots.

Install the extension into a profile first (tests/run_all_builds.sh leaves one per build in
<out_dir>/profile/<build>), open any .blend so the splash is skipped, then run:
  BLENDER_USER_RESOURCES=<profile> blender file.blend --window-geometry 0 0 1600 1000 --python tests/blender_gui_check.py -- <screenshot_dir>
Blender quits by itself; results.json and the PNGs land in <screenshot_dir>.
"""
import bpy, os, sys, json, time, traceback
from importlib import import_module

OUT = sys.argv[sys.argv.index('--') + 1]
os.makedirs(OUT, exist_ok=True)
ADDON = 'bl_ext.user_default.k_tools_render_preset_manager'
EEVEE = 'BLENDER_EEVEE_NEXT' if bpy.app.version < (5, 0, 0) else 'BLENDER_EEVEE'
TOGGLES = ['experimental_output_capture', 'experimental_cycles_capture', 'experimental_eevee_capture',
           'experimental_workbench_capture', 'experimental_view_layer_capture', 'experimental_scene_capture']
results = {'version': bpy.app.version_string, 'checks': [], 'shots': [], 'failures': []}


def log(msg):
    print('GUI_CHECK', msg, flush=True)


def prefs():
    return bpy.context.preferences.addons[ADDON].preferences


def main_window():
    return bpy.context.window_manager.windows[0]


def big_area(window):
    return max(window.screen.areas, key=lambda a: a.width * a.height)


def shot(name):
    window = main_window()
    path = os.path.join(OUT, f'{name}.png')
    with bpy.context.temp_override(window=window, area=big_area(window)):
        bpy.ops.screen.screenshot(filepath=path)
    results['shots'].append(path)
    log(f'shot {path}')


def show_preferences():
    area = big_area(main_window())
    area.type = 'PREFERENCES'
    bpy.context.preferences.active_section = 'ADDONS'
    bpy.context.window_manager.addon_search = 'Render Preset'
    for region in area.regions:
        region.tag_redraw()
    return area


def step_setup():
    p = prefs()
    p.developer_extras = True
    p.show_whitelist = True
    p.panel_location = 'PANEL'
    for attr in TOGGLES:
        setattr(p, attr, True)  # runs the real update callback (cache clear + blacklist sync)
    results['blacklist_items'] = len(p.blacklist_items)
    show_preferences()
    bpy.ops.preferences.addon_expand(module=ADDON)  # toggles, so only once
    log(f'toggles on, blacklist items {len(p.blacklist_items)}')


def step_capture():
    cap = import_module(ADDON + '.output_panel_capture')
    scraper = import_module(ADDON + '.panel_scraper')
    scene = bpy.context.scene
    for category, engine in [('BLENDER_OUTPUT', EEVEE), ('CYCLES', 'CYCLES'), ('BLENDER_EEVEE', EEVEE),
                             ('BLENDER_WORKBENCH', 'BLENDER_WORKBENCH'), ('BLENDER_VIEW_LAYER', 'CYCLES'),
                             ('BLENDER_VIEW_LAYER', EEVEE), ('BLENDER_SCENE', EEVEE)]:
        scene.render.engine = engine
        t = time.perf_counter()
        r = cap.capture_panels(bpy.context, category)
        capture_ms = (time.perf_counter() - t) * 1000
        t = time.perf_counter()
        scraped = scraper.scrape_category_panels(category, bpy.context)
        scrape_ms = (time.perf_counter() - t) * 1000
        props = sum(len(x['properties']) for x in r['panels'])
        check = {'category': category, 'engine': engine, 'panels': len(r['panels']), 'props': props,
                 'errors': r['errors'], 'capture_ms': round(capture_ms, 1), 'scrape_ms': round(scrape_ms, 1),
                 'scraped_panels': len(scraped)}
        results['checks'].append(check)
        if r['errors']:
            results['failures'].append(f'{category}@{engine}: {r["errors"]}')
        log(json.dumps(check))
    for category in ('BLENDER_OUTPUT', 'CYCLES', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH',
                     'BLENDER_VIEW_LAYER', 'BLENDER_SCENE'):
        if bpy.ops.render_preset.audit_output_panels(category=category) != {'FINISHED'}:
            results['failures'].append(f'audit {category}')
    scene.render.engine = 'CYCLES'


def set_tab(tab, search='', engine=None):
    def step():
        if engine:
            bpy.context.scene.render.engine = engine
        p = prefs()
        p.show_whitelist = True
        p.pref_category_tab = tab
        p.search_term = search
        show_preferences()
    return step


def step_dev_tools():
    p = prefs()
    p.show_whitelist = False
    show_preferences()


def step_render_area():
    big_area(main_window()).type = 'PROPERTIES'


def step_render_tab():
    area = big_area(main_window())
    area.spaces.active.context = 'RENDER'
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render_preset_settings.show_main_panel = True
    for region in area.regions:
        region.tag_redraw()


def step_redraw_timing():
    # Time the add-on preferences draw itself, as Blender calls it on each redraw.
    show_preferences()
    p = prefs()
    p.show_whitelist = True
    timings = {}
    for tab, engine in (('CYCLES', 'CYCLES'), ('BLENDER_EEVEE', EEVEE), ('BLENDER_OUTPUT', EEVEE)):
        bpy.context.scene.render.engine = engine
        p.pref_category_tab = tab
        samples = []
        for _ in range(5):
            t = time.perf_counter()
            import_module(ADDON + '.panel_scraper').scrape_category_panels(tab, bpy.context)
            samples.append((time.perf_counter() - t) * 1000)
        timings[tab] = round(sorted(samples)[2], 1)
    results['scrape_per_redraw_ms'] = timings
    log(f'scrape per redraw (median ms) {timings}')


def finish():
    with open(os.path.join(OUT, 'results.json'), 'w') as f:
        json.dump(results, f, indent=1)
    log('DONE ' + ('FAIL ' + str(results['failures']) if results['failures'] else 'OK'))
    bpy.ops.wm.quit_blender()


STEPS = [
    step_setup, step_capture,
    set_tab('CYCLES', engine='CYCLES'), lambda: shot('1_prefs_cycles'),
    set_tab('BLENDER_WORKBENCH', 'shading', 'BLENDER_WORKBENCH'), lambda: shot('2_prefs_workbench_shading'),
    set_tab('BLENDER_VIEW_LAYER', 'pass', 'CYCLES'), lambda: shot('3_prefs_view_layer'),
    set_tab('BLENDER_EEVEE', 'shadow', EEVEE), lambda: shot('4_prefs_eevee_shadow'),
    step_dev_tools, lambda: shot('5_prefs_dev_tools'),
    step_render_area, step_render_tab, lambda: shot('6_render_tab'),
    step_redraw_timing,
    finish,
]


def run_next():
    if not STEPS:
        return None
    step = STEPS.pop(0)
    try:
        step()
    except Exception:
        results['failures'].append(traceback.format_exc())
        log('STEP FAILED ' + traceback.format_exc())
        if step is not finish and finish in STEPS:
            pass
    return 1.0  # let the UI redraw between steps


bpy.app.timers.register(run_next, first_interval=2.0)
