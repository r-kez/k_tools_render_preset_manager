import bpy
from bpy.types import Operator
from .. import utils
import random
from ..properties.function_list import (
    RENDER_SETTINGS, 
)


def _check_property_exists(context, prop_path):
    """Verifica se um caminho de propriedade da RENDER_SETTINGS ainda existe no Blender."""
    # Determina o objeto base
    if prop_path.startswith("<ACTIVE_VIEW_LAYER>"):
        base_obj = context.view_layer
        prop_path = prop_path.replace("<ACTIVE_VIEW_LAYER>.", "", 1)
    elif prop_path.startswith("world."):
        base_obj = context.scene.world
        prop_path = prop_path.replace("world.", "", 1)
    else:
        base_obj = context.scene
        if prop_path.startswith("scene."):
            prop_path = prop_path.replace("scene.", "", 1)
            
    if not base_obj: return False
    
    # Tenta acessar a propriedade
    try:
        parts = prop_path.split('.')
        current_obj = base_obj
        for part in parts:
            if '[' in part: return True # Não podemos validar caminhos de array
            current_obj = getattr(current_obj, part)
        return True
    except (AttributeError, KeyError):
        return False

# --- FUNÇÃO 2: O "SCRAPER" (Do seu scraper.py) ---
def _scrape_properties_for_audit(context, source_type, filter_path, max_depth):
    """Scrapeia propriedades do Blender baseado nas configurações da UI."""
    scraped_props = {}
    
    # Pega o objeto base (Scene, View Layer, etc.)
    if source_type == 'SCENE': base_obj = context.scene
    elif source_type == 'VIEW_LAYER': base_obj = context.view_layer
    elif source_type == 'WORLD': base_obj = context.scene.world
    elif source_type == 'CAMERA': base_obj = context.scene.camera.data if context.scene.camera else None
    else: base_obj = None
    
    if not base_obj:
        return {} # Retorna um dicionário vazio se a fonte for inválida
        
    start_obj = base_obj
    
    # Aplica o filtro de caminho (ex: "cycles", "render.image_settings")
    if filter_path:
        try:
            for part in filter_path.split('.'):
                start_obj = getattr(start_obj, part)
        except AttributeError:
            return {} # Caminho de filtro inválido

    # --- Lógica de Scrape (do seu scraper.py) ---
    def _capture(obj, result, prefix, current_depth):
        if current_depth >= max_depth: return
        ignore_attrs = {'__', 'bl_rna', 'rna_type', 'name', 'bl_idname', 'bl_label'}
        try: attrs = dir(obj)
        except: return
        
        for attr in attrs:
            if attr.startswith('_') or any(ig in attr for ig in ignore_attrs):
                continue
            try:
                value = getattr(obj, attr)
                if callable(value): continue
                full_path = f"{prefix}.{attr}" if prefix else attr
                
                # Aplica filtros de propriedade
                if hasattr(value, 'is_readonly') and value.is_readonly: continue
                if hasattr(value, 'is_registered_by_script') and value.is_registered_by_script: continue
                
                if isinstance(value, (int, float, str, bool, type(None), tuple, list)):
                    # Normaliza o caminho para o formato da RENDER_SETTINGS
                    key = full_path
                    if source_type == 'SCENE' and key.startswith('scene.'):
                        key = key.replace('scene.', '', 1)
                    elif source_type == 'VIEW_LAYER' and key.startswith('view_layer.'):
                        key = key.replace('view_layer.', '<ACTIVE_VIEW_LAYER>.', 1)
                    
                    result[key] = True
                elif hasattr(value, 'bl_rna'):
                    _capture(value, result, full_path, current_depth + 1)
            except: continue
    
    _capture(start_obj, scraped_props, filter_path, 0)
    return scraped_props

class RENDER_PRESET_OT_validate_list(Operator):
    """
    Roda uma auditoria completa:
    1. Encontra propriedades OBSOLETAS em TODA a RENDER_SETTINGS.
    2. Encontra propriedades NOVAS na área de scrape selecionada.
    """
    bl_idname = "render_preset.validate_list"
    bl_label = "Run Full Property Audit"
    bl_description = "Finds new and obsolete properties and writes a report to the Text Editor"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        prefs = utils.get_addon_preferences(context)
        if not prefs:
            self.report({'ERROR'}, "Could not access addon preferences.")
            return {'CANCELLED'}

        # Pega as configurações da UI do Scraper (como você pediu)
        source_type = prefs.dev_scraper_source_type
        filter_path = prefs.dev_scraper_filter_path
        max_depth = prefs.dev_scraper_max_depth

        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append(f"AUDIT REPORT")
        report_lines.append("=" * 80)

        # --- TAREFA 1: Encontrar propriedades OBSOLETAS (em TODA a RENDER_SETTINGS) ---
        report_lines.append("\n--- Checking for Obsolete Properties (in all categories) ---")
        manual_paths = {path: category for category, props in RENDER_SETTINGS.items() for path, label in props}
        obsolete_properties = []
        
        for path in manual_paths.keys():
            if not _check_property_exists(context, path):
                obsolete_properties.append( (path, manual_paths[path]) )

        report_lines.append(f"✗ {len(obsolete_properties)} obsolete properties found (in your list, not in Blender).")
        if obsolete_properties:
            report_lines.append("-" * 30)
            report_lines.append("OBSOLETE PROPERTIES (Remove these from RENDER_SETTINGS):")
            report_lines.append("-" * 30)
            for prop, cat in sorted(obsolete_properties):
                report_lines.append(f"    - \"{prop}\" (from category '{cat}')")
        
        # --- TAREFA 2: Encontrar propriedades NOVAS (na área de Scrape selecionada) ---
        report_lines.append("\n" + "="*80)
        report_lines.append(f"--- Checking for New Properties ---")
        report_lines.append(f"Scraping Source: '{source_type}' | Filter Path: '{filter_path or 'None'}'")
        
        # Converte o 'manual_paths' de dict para set para comparação
        manual_paths_set = set(manual_paths.keys())
        scraped_paths = set(_scrape_properties_for_audit(context, source_type, filter_path, max_depth).keys())
        
        new_properties = scraped_paths - manual_paths_set
        
        if prefs.dev_show_new_props:
            report_lines.append(f"[+] {len(new_properties)} new properties found (in Blender, not in your list).")
            if new_properties:
                report_lines.append("\n" + "-"*30)
                report_lines.append(f"NEW PROPERTIES (Found in '{source_type}' -> '{filter_path}'):")
                report_lines.append("Add these to your RENDER_SETTINGS list:")
                report_lines.append("-" * 30)
                for prop in sorted(list(new_properties)):
                    report_lines.append(f'    ("{prop}", "Subgroup: Name"),')
        else:
            report_lines.append("[ ] 'Check for New Properties' is disabled.")

        report_lines.append("\n" + "="*80)
        report_lines.append("AUDIT COMPLETE")
        report_lines.append("=" * 80)
        
        report_text = "\n".join(report_lines)

        # 6. Save report to Text Editor
        text_name = f"Preset_Audit_Report"
        text_block = bpy.data.texts.new(text_name) if text_name not in bpy.data.texts else bpy.data.texts[text_name]
        text_block.clear()
        text_block.write(report_text)
        
        self.report({'INFO'}, f"Audit complete. Report saved to Text Editor: '{text_name}'")
        return {'FINISHED'}

# --- OPERADOR 2: GENERATE (Baseado no seu 'generate_clean_list') ---
class RENDER_PRESET_OT_generate_new_list(Operator):
    """Scrapes properties and generates a new, clean list in the Text Editor."""
    bl_idname = "render_preset.generate_new_list"
    bl_label = "Generate New List from Scraper"
    bl_description = "Scrapes Blender properties and generates a new list in the Text Editor"

    def execute(self, context):
        prefs = utils.get_addon_preferences(context)
        
        source_type = prefs.dev_scraper_source_type
        filter_path = prefs.dev_scraper_filter_path
        max_depth = prefs.dev_scraper_max_depth
        
        if source_type == 'SCENE': base_obj = context.scene
        elif source_type == 'VIEW_LAYER': base_obj = context.view_layer
        elif source_type == 'WORLD': base_obj = context.scene.world
        elif source_type == 'CAMERA': base_obj = context.scene.camera.data if context.scene.camera else None
        else: base_obj = None
        
        if not base_obj:
            self.report({'ERROR'}, f"Invalid source or no active {source_type}")
            return {'CANCELLED'}
        
        if filter_path:
            try:
                for part in filter_path.split('.'):
                    base_obj = getattr(base_obj, part)
            except AttributeError:
                self.report({'ERROR'}, f"Invalid Filter Path: {filter_path}")
                return {'CANCELLED'}
        
        properties_dict = {}
        self._capture_for_clean_list(base_obj, properties_dict, filter_path, max_depth, 0)
        
        clean_list = self._format_clean_list(properties_dict, source_type, filter_path, source_type == 'VIEW_LAYER')
        
        text_name = f"Scraper_Generated_List_{source_type}"
        if filter_path: text_name += f"_{filter_path.replace('.', '_')}"
        
        text_block = bpy.data.texts.new(text_name) if text_name not in bpy.data.texts else bpy.data.texts[text_name]
        text_block.clear()
        text_block.write(clean_list)
        
        self.report({'INFO'}, f"Generated list in Text Editor: '{text_name}'")
        return {'FINISHED'}

    def _capture_for_clean_list(self, obj, result, prefix, max_depth, current_depth):
        # Lógica do seu scraper
        if current_depth >= max_depth: return
        ignore_attrs = {'__', 'bl_rna', 'rna_type', 'name', 'bl_idname', 'bl_label'}
        try: attrs = dir(obj)
        except: return
        
        for attr in attrs:
            if attr.startswith('_') or any(ig in attr for ig in ignore_attrs):
                continue
            try:
                value = getattr(obj, attr)
                if callable(value): continue
                full_path = f"{prefix}.{attr}" if prefix else attr
                
                if isinstance(value, (int, float, str, bool, type(None))):
                    result[full_path] = type(value).__name__
                elif isinstance(value, (tuple, list)):
                    if len(value) > 0: result[full_path] = f"list[{type(value[0]).__name__}]"
                elif hasattr(value, 'bl_rna'):
                    result[full_path] = "object"
                    self._capture_for_clean_list(value, result, full_path, max_depth, current_depth + 1)
            except: continue
    
    def _format_clean_list(self, properties_dict, source_name, filter_prefix, is_view_layer):
        # Lógica do seu scraper
        lines = []
        category_name = filter_prefix.upper().replace('.', '_') if filter_prefix else source_name.upper()
        lines.append(f'"{category_name}": [')
        
        for prop_path, prop_type in sorted(properties_dict.items()):
            clean_path = prop_path
            if clean_path.startswith('scene.'):
                clean_path = clean_path[6:]
            
            if is_view_layer:
                if clean_path.startswith('view_layer.'):
                    clean_path = clean_path.replace('view_layer.', '<ACTIVE_VIEW_LAYER>.', 1)
                else:
                    clean_path = f"<ACTIVE_VIEW_LAYER>.{clean_path}"
            
            display_name = self._generate_display_name(clean_path)
            lines.append(f'    ("{clean_path}", "{display_name}"),')
        
        lines.append('],')
        return '\n'.join(lines)
    
    def _generate_display_name(self, prop_path):
        # Lógica do seu scraper
        clean = prop_path.replace('<ACTIVE_VIEW_LAYER>.', '')
        parts = clean.split('.')
        if len(parts) > 1:
            category = parts[-2].replace('_', ' ').title()
            property_name = parts[-1].replace('_', ' ').title()
            return f"{category}: {property_name}"
        else:
            return parts[0].replace('_', ' ').title()


# --- OPERADOR 3: O POP-UP DE CONFIRMAÇÃO ---
class RENDER_PRESET_OT_validation_report_popup(Operator):
    """Shows a simple 'OK' dialog with the validation result."""
    bl_idname = "render_preset.validation_report_popup"
    bl_label = "Validation Report"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Validation complete!")
        layout.label(text="Check the System Console and Text Editor for the full report.")



class RENDER_PRESET_OT_fuzz_test_scene(bpy.types.Operator):
    """Randomly scrambles all supported render properties in the scene for testing."""
    bl_idname = "render_preset.fuzz_test_scene"
    bl_label = "Fuzz Test Scene (Monkey Test)"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        # Chama um diálogo de confirmação com a nossa interface customizada no método draw
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.alert = True
        layout.label(text="WARNING: DESTRUCTIVE ACTION!", icon='ERROR')
        layout.alert = False
        layout.separator()
        layout.label(text="This will randomly scramble ALL properties")
        layout.label(text="mapped in your function_list.py.")
        layout.label(text="Only use this in a test scene!")

    def get_random_valid_value(self, scene, path):
        """Introspecta o Blender ou o Octane e retorna um valor aleatório válido."""
        
        # --- OCTANE KERNEL SWITCH ---
        if path == "KTOOLS_SPECIAL.octane_active_kernel":
            return random.choice([
                'OctaneDirectLightingKernel', 'OctanePathTracingKernel', 
                'OctanePMCKernel', 'OctanePhotonTracingKernel', 'OctaneInfoChannelsKernel'
            ])
            
        # --- OCTANE KERNEL INPUTS ---
        if path.startswith("KTOOLS_SPECIAL.octane_kernel_input|"):
            input_name = path.split("|")[1]
            try:
                tree = scene.octane.kernel_node_graph_property.node_tree
                if tree:
                    for n in tree.nodes:
                        if "Kernel" in n.inputs and n.inputs["Kernel"].is_linked:
                            active_node = n.inputs["Kernel"].links[0].from_node
                            if input_name in active_node.inputs:
                                socket = active_node.inputs[input_name]
                                socket_type = type(socket).__name__
                                
                                if socket_type == 'NodeSocketFloat':
                                    return round(random.uniform(0.0, 1.0), 3)
                                elif socket_type == 'NodeSocketInt':
                                    return random.randint(0, 100)
                                elif socket_type == 'NodeSocketBool':
                                    return random.choice([True, False])
                                elif socket_type == 'NodeSocketColor':
                                    return (random.random(), random.random(), random.random(), 1.0)
            except Exception:
                pass
            return None

        # --- STANDARD RNA RESOLUTION ---
        current_obj, last_type, last_attr = utils.resolve_path_to_target(scene, path)
        if current_obj is None or last_type != 'attr':
            return None
                
        # --- RNA INTROSPECTION ---
        if not hasattr(current_obj, "bl_rna"): return None
        rna_prop = current_obj.bl_rna.properties.get(last_attr)
        
        if not rna_prop or rna_prop.is_readonly: return None
        
        try:
            if rna_prop.type == 'BOOLEAN':
                if getattr(rna_prop, 'is_array', False):
                    return [random.choice([True, False]) for _ in range(rna_prop.array_length)]
                return random.choice([True, False])

            elif rna_prop.type == 'INT':
                min_val = max(rna_prop.hard_min, -100)
                max_val = min(rna_prop.hard_max, 1000)
                if getattr(rna_prop, 'is_array', False):
                    return [random.randint(min_val, max_val) for _ in range(rna_prop.array_length)]
                return random.randint(min_val, max_val)

            elif rna_prop.type == 'FLOAT':
                min_val = max(rna_prop.hard_min, -100.0)
                max_val = min(rna_prop.hard_max, 100.0)
                if getattr(rna_prop, 'is_array', False):
                    return [round(random.uniform(min_val, max_val), 3) for _ in range(rna_prop.array_length)]
                return round(random.uniform(min_val, max_val), 3)

            elif rna_prop.type == 'ENUM':
                valid_items = [item.identifier for item in rna_prop.enum_items]
                if not valid_items: return None
                
                # PREVENÇÃO DE CRASH: Não fuzza a engine atual para não corromper a memória do Blender
                if last_attr == "engine":
                    return current_obj.engine
                    
                if last_attr == "file_format" and "OPEN_EXR_MULTILAYER" in valid_items:
                    valid_items.remove("OPEN_EXR_MULTILAYER")
                    
                return random.choice(valid_items)
        except Exception:
            pass
            
        return None

    def execute(self, context):
        scene = context.scene
        applied_count = 0
        
        active_engine = scene.render.engine.upper()
        if active_engine == 'BLENDER_EEVEE_NEXT':
            active_engine = 'BLENDER_EEVEE'
            
        # Lista expansiva com as chaves exatas do seu function_list
        allowed_categories = [
            "RENDER_ENGINE", 
            "BLENDER_OUTPUT", 
            "BLENDER_VIEW_LAYER", 
            "VIEW_LAYER", 
            "BLENDER_SCENE", 
            "USER_CUSTOM",
            active_engine
        ]
        
        # Se a engine for Octane, libera as categorias exclusivas dele
        if active_engine == 'OCTANE':
            allowed_categories.extend([
                "OCTANE_VIEW_LAYER", 
                "OCTANE_IMAGER", 
                "OCTANE_POST"
            ])

        for category, settings_list in RENDER_SETTINGS.items():
            if category not in allowed_categories:
                continue
                
            for path, label in settings_list:
                random_val = self.get_random_valid_value(scene, path)
                
                if random_val is not None:
                    # Injeta o valor na cena usando seu utilitário seguro
                    success, _ = utils.set_nested_attr(scene, path, random_val)
                    if success:
                        applied_count += 1
                        
        bpy.context.view_layer.update()
        self.report({'WARNING'}, f"Fuzz Test complete! Randomized {applied_count} properties.")
        return {'FINISHED'}\

# --- REGISTRO DAS CLASSES ---
classes = (
    RENDER_PRESET_OT_validate_list,
    RENDER_PRESET_OT_generate_new_list,
    RENDER_PRESET_OT_validation_report_popup,
    RENDER_PRESET_OT_fuzz_test_scene,

)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)