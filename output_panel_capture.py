"""Experimental, read-only capture of properties drawn by Properties Editor panels.

Panels are drawn into a recording layout so that only settings the user can see
in Blender's UI are offered for saving and loading. The legacy property list
stays as the fallback for anything a panel does not draw in the current state.
"""

import bpy
import sys


_VALUE_TYPES = {'BOOLEAN', 'INT', 'FLOAT', 'ENUM', 'STRING'}
ACTIVE_VIEW_LAYER = '<ACTIVE_VIEW_LAYER>'


def _pointer_chains(root_type, target_type, max_depth=3):
    """Yield non-ID pointer property chains from root_type to target_type."""
    pending = [(root_type, ())]
    for _depth in range(max_depth):
        found = []
        for struct_type, chain in pending:
            for prop in struct_type.properties:
                if prop.type != 'POINTER' or prop.identifier == 'rna_type':
                    continue
                fixed = prop.fixed_type
                if fixed is None or fixed.identifier == 'ID' or isinstance(
                        getattr(bpy.types, fixed.identifier, None), type) and issubclass(
                        getattr(bpy.types, fixed.identifier), bpy.types.ID):
                    continue
                next_chain = chain + (prop.identifier,)
                if fixed.identifier == target_type:
                    yield next_chain
                found.append((fixed, next_chain))
        pending = found


class _LayoutRecorder:
    # Attributes panels read or write on a real UILayout.
    property_split_factor = 0.5
    active = True
    active_default = False
    activate_init = False
    alert = False
    enabled = True
    emboss = 'NORMAL'
    alignment = 'EXPAND'
    direction = 'VERTICAL'
    operator_context = 'INVOKE_DEFAULT'
    scale_x = 1.0
    scale_y = 1.0
    ui_units_x = 0.0
    ui_units_y = 0.0
    use_property_split = False
    use_property_decorate = True

    def __init__(self, context):
        self.scene = context.scene
        self.view_layer = context.view_layer
        self.properties = []
        self.skipped = []
        self._paths = set()

    def _prefix_for_owner(self, owner):
        """Find the path of a nested struct whose path_from_id is unsupported.

        Candidate chains are found from RNA type metadata only; the single
        matching chain is then read and checked against the owner. Reading
        unrelated pointers is avoided because some of them crash Blender.
        """
        target_type = owner.bl_rna.identifier
        target = owner.as_pointer()
        for root, prefix in ((self.scene, ''), (self.view_layer, ACTIVE_VIEW_LAYER)):
            if root.as_pointer() == target:
                return prefix
            for chain in _pointer_chains(root.bl_rna, target_type):
                value = root
                try:
                    for identifier in chain:
                        value = getattr(value, identifier)
                except Exception:
                    continue
                if value is not None and value.as_pointer() == target:
                    path = '.'.join(chain)
                    return f'{prefix}.{path}' if prefix else path
        return None

    def _path(self, owner, identifier):
        try:
            path = owner.path_from_id(identifier)
        except ValueError:
            prefix = self._prefix_for_owner(owner)
            if prefix is None:
                raise
            path = f'{prefix}.{identifier}' if prefix else identifier
        # Store view layer settings against whichever layer is active on load.
        layer_path = self.view_layer.path_from_id()
        if path.startswith(layer_path + '.'):
            path = ACTIVE_VIEW_LAYER + path[len(layer_path):]
        return path

    def prop(self, owner, identifier, *args, **kwargs):
        try:
            if getattr(owner, 'id_data', None) != self.scene:
                self.skipped.append(f'{identifier}: property owner is not the active scene')
                return self
            rna_prop = owner.bl_rna.properties.get(identifier)
            if rna_prop is None or rna_prop.is_readonly or rna_prop.type not in _VALUE_TYPES:
                self.skipped.append(f'{identifier}: unsupported or read-only RNA property')
                return self
            path = self._path(owner, identifier)
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
                    'operator_enum', 'menu_contents', 'context_pointer_set',
                    'context_string_set', 'separator_spacer', 'progress', 'prop_decorator'}:
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


class _PropertiesSpace:
    """Stand-in for the Properties Editor that draws the panel."""

    type = 'PROPERTIES'
    pin_id = None
    use_pin_id = False

    def __init__(self, bl_context):
        self.context = bl_context.upper()


class _DrawContext:
    """Context seen by panels: the real one, viewed from the Properties Editor.

    Without this, panels such as Workbench's Lighting would read the shading of
    whatever editor the add-on happens to run in, or fail in background mode.
    """

    def __init__(self, context, bl_context):
        self._context = context
        self.space_data = _PropertiesSpace(bl_context)

    def __getattr__(self, name):
        return getattr(self._context, name)


def _find_method(panel_class, name):
    """Find a draw method defined by the panel or its Python mixins."""
    for base in panel_class.__mro__:
        if base is bpy.types.Panel:
            return None
        method = vars(base).get(name)
        if method is not None:
            return method
    return None


# Panels shared by every engine on the Render tab.
_RENDER_TAB = [
    ('bl_ui.properties_render', 'render', ''),
    ('bl_ui.properties_freestyle', 'render', ''),
]

# Panel sources that can be executed safely, as (module, bl_context, prefix).
# Only panels defined in these modules run, so third-party panels never do.
# An engine category holds everything the Render tab draws for that engine,
# matching what the legacy lists already grouped under each engine.
CAPTURE_SOURCES = {
    'BLENDER_OUTPUT': {
        'label': 'Output',
        'sources': [('bl_ui.properties_output', 'output', '')],
    },
    'CYCLES': {
        'label': 'Cycles',
        'engines': {'CYCLES'},
        # Camera panels share the render mixin but belong to Object Data.
        'sources': [('cycles.ui', 'render', 'CYCLES_RENDER_PT_')] + _RENDER_TAB,
    },
    'BLENDER_EEVEE': {
        'label': 'EEVEE',
        'engines': {'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'},
        'sources': _RENDER_TAB,
    },
    'BLENDER_WORKBENCH': {
        'label': 'Workbench',
        'engines': {'BLENDER_WORKBENCH'},
        'sources': _RENDER_TAB,
    },
    'BLENDER_VIEW_LAYER': {
        'label': 'View Layer',
        'sources': [
            ('bl_ui.properties_view_layer', 'view_layer', ''),
            ('cycles.ui', 'view_layer', 'CYCLES_RENDER_PT_'),
        ],
    },
    'BLENDER_SCENE': {
        'label': 'Scene',
        'sources': [('bl_ui.properties_scene', 'scene', '')],
    },
}

# Paths owned by another category even though these panels draw them.
_EXCLUDED_PATHS = {
    'render.engine',  # RENDER_ENGINE
}


def _panel_order(panel_class, module):
    """Keep panels in their source order so parents come before children."""
    try:
        return list(vars(module)).index(panel_class.__name__)
    except ValueError:
        return 1 << 30


def _is_visible(panel_class, context, cache, errors):
    """A panel shows only when it and every parent panel pass their poll."""
    panel_id = getattr(panel_class, 'bl_idname', None) or panel_class.__name__
    if panel_id in cache:
        return cache[panel_id]
    cache[panel_id] = False
    visible = True
    try:
        poll = getattr(panel_class, 'poll', None)
        visible = poll is None or bool(poll(context))
    except Exception as exc:
        errors.append(f'{panel_id}.poll: {type(exc).__name__}: {exc}')
        visible = False
    parent_id = getattr(panel_class, 'bl_parent_id', '')
    if visible and parent_id:
        parent = getattr(bpy.types, parent_id, None)
        visible = parent is not None and _is_visible(parent, context, cache, errors)
    cache[panel_id] = visible
    return visible


def _source_panels(module_name, bl_context, prefix):
    module = sys.modules.get(module_name)
    if module is None:
        return []
    panels = [
        panel_class for panel_class in bpy.types.Panel.__subclasses__()
        if panel_class.__module__ == module_name
        and getattr(panel_class, 'bl_space_type', None) == 'PROPERTIES'
        and getattr(panel_class, 'bl_context', None) == bl_context
        and panel_class.__name__.startswith(prefix)
        and getattr(module, panel_class.__name__, None) is panel_class
        and getattr(bpy.types, panel_class.__name__, None) is panel_class
    ]
    panels.sort(key=lambda cls: _panel_order(cls, module))
    return panels


def capture_panels(context, category):
    """Return captured properties and explicit gaps for one category's panels.

    Only panels from the category's own modules are executed. Conditional UI
    means the result describes the current scene and render engine, not every
    possible state. Nothing is written to the scene or to a preset.
    """
    result = {'panels': [], 'errors': [], 'skipped': []}
    config = CAPTURE_SOURCES.get(category)
    if config is None:
        result['errors'].append(f'No panel source is defined for {category}')
        return result
    engines = config.get('engines')
    if engines and context.scene.render.engine not in engines:
        result['errors'].append(
            f"{config['label']} panels are only drawn when the render engine is "
            + ' or '.join(sorted(engines)))
        return result

    sources = config['sources']
    if not any(sys.modules.get(module_name) for module_name, _, _ in sources):
        result['errors'].append(f"{config['label']} panel modules are unavailable")
        return result

    visibility = {}
    seen = set()
    for module_name, bl_context, prefix in sources:
        draw_context = _DrawContext(context, bl_context)
        for panel_class in _source_panels(module_name, bl_context, prefix):
            panel_id = getattr(panel_class, 'bl_idname', None) or panel_class.__name__
            if panel_id in seen:
                continue
            seen.add(panel_id)
            if not _is_visible(panel_class, draw_context, visibility, result['errors']):
                continue

            layout = _LayoutRecorder(context)
            instance = _PanelInstance(panel_class, layout)
            for method_name in ('draw_header', 'draw'):
                method = _find_method(panel_class, method_name)
                if method is None:
                    continue
                try:
                    method(instance, draw_context)
                except Exception as exc:
                    result['errors'].append(
                        f'{panel_id}.{method_name}: {type(exc).__name__}: {exc}')

            properties = [item for item in layout.properties
                          if item[0] not in _EXCLUDED_PATHS]
            if properties:
                result['panels'].append({
                    'id': panel_id,
                    'label': getattr(panel_class, 'bl_label', panel_id),
                    'parent_id': getattr(panel_class, 'bl_parent_id', ''),
                    'properties': properties,
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
