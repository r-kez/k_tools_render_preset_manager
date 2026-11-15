"""Experimental, read-only capture of properties drawn by Properties Editor panels.

Panels are drawn into a recording layout so that only settings the user can see
in Blender's UI are offered for saving and loading. The legacy property list
stays as the fallback for anything a panel does not draw in the current state.
"""

import bpy
import sys


_VALUE_TYPES = {'BOOLEAN', 'INT', 'FLOAT', 'ENUM', 'STRING'}


class _LayoutRecorder:
    property_split_factor = 0.5

    def __init__(self, scene):
        self.scene = scene
        self.properties = []
        self.skipped = []
        self._paths = set()

    def prop(self, owner, identifier, *args, **kwargs):
        try:
            if getattr(owner, 'id_data', None) != self.scene:
                self.skipped.append(f'{identifier}: property owner is not the active scene')
                return self
            rna_prop = owner.bl_rna.properties.get(identifier)
            if rna_prop is None or rna_prop.is_readonly or rna_prop.type not in _VALUE_TYPES:
                self.skipped.append(f'{identifier}: unsupported or read-only RNA property')
                return self
            path = owner.path_from_id(identifier)
            if path not in self._paths:
                label = kwargs.get('text') or rna_prop.name
                self.properties.append((path, label))
                self._paths.add(path)
        except Exception as exc:
            self.skipped.append(f'{identifier}: {type(exc).__name__}: {exc}')
        return self

    def prop_enum(self, owner, identifier, *args, **kwargs):
        return self.prop(owner, identifier, **kwargs)

    def prop_search(self, owner, identifier, *args, **kwargs):
        return self.prop(owner, identifier, **kwargs)

    def textbox(self, owner, identifier, *args, **kwargs):
        return self.prop(owner, identifier, **kwargs)

    def prop_with_menu(self, owner, identifier, *args, **kwargs):
        return self.prop(owner, identifier, **kwargs)

    def prop_menu_enum(self, owner, identifier, *args, **kwargs):
        return self.prop(owner, identifier, **kwargs)

    def prop_tabs_enum(self, owner, identifier, *args, **kwargs):
        return self.prop(owner, identifier, **kwargs)

    def row(self, *args, **kwargs):
        return self

    column = row
    box = row
    split = row
    grid_flow = row
    column_flow = row

    def panel(self, *args, **kwargs):
        return self, self

    panel_prop = panel

    def operator(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        if name.startswith('template_'):
            def record_template(*args, **kwargs):
                self.skipped.append(f'{name}: template properties are not captured')
                return self
            return record_template
        if name in {'label', 'separator', 'menu', 'popover', 'operator_menu_enum',
                    'context_pointer_set', 'separator_spacer'}:
            return lambda *args, **kwargs: self
        raise AttributeError(name)


class _PanelInstance:
    """Provide a recording layout to a Python Panel.draw implementation."""

    def __init__(self, panel_class, layout):
        self._panel_class = panel_class
        self.layout = layout

    def __getattr__(self, name):
        for base in self._panel_class.__mro__:
            if name in vars(base):
                value = vars(base)[name]
                getter = getattr(value, '__get__', None)
                return getter(self, self._panel_class) if getter else value
        raise AttributeError(name)


def _find_method(panel_class, name):
    """Find a draw method defined by the panel or its Python mixins."""
    for base in panel_class.__mro__:
        if base is bpy.types.Panel:
            return None
        method = vars(base).get(name)
        if method is not None:
            return method
    return None


# Panel sources that can be executed safely. Each category only reads panels
# from the module that owns them, so third-party panels are never executed.
CAPTURE_SOURCES = {
    'BLENDER_OUTPUT': {
        'module': 'bl_ui.properties_output',
        'context': 'output',
        'label': 'Output',
    },
    'CYCLES': {
        'module': 'cycles.ui',
        'context': 'render',
        'label': 'Cycles',
        'engine': 'CYCLES',
        # Camera panels share the render mixin but belong to Object Data.
        'prefix': 'CYCLES_RENDER_PT_',
    },
}


def _panel_order(panel_class, module):
    """Keep panels in their source order so parents come before children."""
    try:
        return list(vars(module)).index(panel_class.__name__)
    except ValueError:
        return 1 << 30


def capture_panels(context, category):
    """Return captured properties and explicit gaps for one category's panels.

    Only panels defined in the category's own module are executed. Conditional
    UI means the result describes the current scene and render engine, not every
    possible state. Nothing is written to the scene or to a preset.
    """
    result = {'panels': [], 'errors': [], 'skipped': []}
    source = CAPTURE_SOURCES.get(category)
    if source is None:
        result['errors'].append(f'No panel source is defined for {category}')
        return result
    module_name = source['module']
    module = sys.modules.get(module_name)
    if module is None:
        result['errors'].append(f"{source['label']} panel module is unavailable")
        return result
    engine = source.get('engine')
    if engine and context.scene.render.engine != engine:
        result['errors'].append(
            f"{source['label']} panels are only drawn when the render engine is {engine}")
        return result

    panel_classes = [
        panel_class for panel_class in bpy.types.Panel.__subclasses__()
        if panel_class.__module__ == module_name
        and getattr(panel_class, 'bl_space_type', None) == 'PROPERTIES'
        and getattr(panel_class, 'bl_context', None) == source['context']
        and panel_class.__name__.startswith(source.get('prefix', ''))
        and getattr(module, panel_class.__name__, None) is panel_class
        and getattr(bpy.types, panel_class.__name__, None) is panel_class
    ]
    panel_classes.sort(key=lambda cls: _panel_order(cls, module))

    for panel_class in panel_classes:
        panel_id = getattr(panel_class, 'bl_idname', None) or panel_class.__name__
        try:
            poll = getattr(panel_class, 'poll', None)
            if poll is not None and not poll(context):
                continue
        except Exception as exc:
            result['errors'].append(f'{panel_id}.poll: {type(exc).__name__}: {exc}')
            continue

        layout = _LayoutRecorder(context.scene)
        instance = _PanelInstance(panel_class, layout)
        for method_name in ('draw_header', 'draw'):
            method = _find_method(panel_class, method_name)
            if method is None:
                continue
            try:
                method(instance, context)
            except Exception as exc:
                result['errors'].append(f'{panel_id}.{method_name}: {type(exc).__name__}: {exc}')

        if layout.properties:
            result['panels'].append({
                'id': panel_id,
                'label': getattr(panel_class, 'bl_label', panel_id),
                'parent_id': getattr(panel_class, 'bl_parent_id', ''),
                'properties': layout.properties,
            })
        result['skipped'].extend(f'{panel_id}: {reason}' for reason in layout.skipped)
    return result


def capture_output_panels(context):
    """Capture Blender's built-in Output panels (kept for existing callers)."""
    return capture_panels(context, 'BLENDER_OUTPUT')


def capture_output_states(context):
    """Audit selected Output UI branches in a disposable copy of the scene."""
    states = []
    errors = []
    probe_scene = context.scene.copy()
    try:
        image_settings = probe_scene.render.image_settings
        original_format = image_settings.file_format
        original_management = image_settings.color_management
        original_multiview = probe_scene.render.use_multiview
        configurations = [
            ('Current format', original_format, original_management, original_multiview),
            ('PNG', 'PNG', original_management, False),
            ('OpenEXR', 'OPEN_EXR', original_management, False),
            ('Movie', 'FFMPEG', original_management, False),
            ('PNG with color override', 'PNG', 'OVERRIDE', False),
            ('PNG with multiple views', 'PNG', original_management, True),
        ]
        with context.temp_override(scene=probe_scene, view_layer=probe_scene.view_layers[0]):
            for label, file_format, management, multiview in configurations:
                try:
                    image_settings.file_format = file_format
                    image_settings.color_management = management
                    probe_scene.render.use_multiview = multiview
                    states.append({
                        'label': label,
                        'file_format': file_format,
                        'capture': capture_output_panels(bpy.context),
                    })
                except Exception as exc:
                    errors.append(f'{label}: {type(exc).__name__}: {exc}')
            for label, attribute, value in (
                    ('Custom frame rate', 'fps', 37),
                    ('Custom pixel density', 'ppm_base', 0.0123)):
                try:
                    image_settings.file_format = 'PNG'
                    setattr(probe_scene.render, attribute, value)
                    states.append({
                        'label': label,
                        'file_format': 'PNG',
                        'capture': capture_output_panels(bpy.context),
                    })
                except Exception as exc:
                    errors.append(f'{label}: {type(exc).__name__}: {exc}')
    finally:
        bpy.data.scenes.remove(probe_scene)
    return {'states': states, 'errors': errors}
