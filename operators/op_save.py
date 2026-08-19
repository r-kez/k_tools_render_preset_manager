import bpy
import json
import os
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .. import utils
from ..utils import (
    get_current_settings,
    )

def get_addon_version():
    """Lê a versão do addon dinamicamente direto do blender_manifest.toml"""
    addon_root = os.path.dirname(os.path.dirname(__file__))
    manifest_path = os.path.join(addon_root, "blender_manifest.toml")
    
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                for line in f:
                    # Procura a linha que começa com "version" e limpa as aspas e espaços
                    if line.startswith("version"):
                        return line.split("=")[1].strip().strip('"').strip("'")
        except Exception as e:
            print(f"K-Tools: Failed to read manifest version - {e}")
            
    return "Unknown"

from ..panel_scraper import scrape_category_panels

SCHEMA_VERSION = "2.0.0"
ADDON_VERSION = get_addon_version()

# =============================================================================
# Save Preset
# =============================================================================
def save_preset_to_file(context, filepath):
    """
    Gathers the selected settings and writes them to a JSON file at the given path.
    Saves both v2.0 panel-structured data ('categories') and v1.0 flat data ('render_presets')
    for maximum backwards and cross-version compatibility.
    """
    preset_props = context.scene.render_preset_settings

    # Check if a preset name is provided
    if not preset_props.preset_name:
        print("Preset Name cannot be empty.")
        return False, "Preset Name cannot be empty."

    preset_data = {
        "preset_name": preset_props.preset_name,
        "description": preset_props.preset_description,
        "blender_version": bpy.app.version_string,
        "addon_version": ADDON_VERSION,
        "schema_version": SCHEMA_VERSION,
        "categories": {},
        "render_presets": {}  # Fallback for v1.0 readers
    }

    total_saved = 0
    categories_to_save = {
        "RENDER_ENGINE": preset_props.save_render_engine,
        "CYCLES": preset_props.save_cycles,
        "BLENDER_EEVEE": preset_props.save_eevee,
        "BLENDER_WORKBENCH": preset_props.save_workbench,
        "BLENDER_OUTPUT": preset_props.save_output,
        "BLENDER_VIEW_LAYER": preset_props.save_view_layer,
        "BLENDER_SCENE": preset_props.save_scene,
        # Octane
        "OCTANE": preset_props.save_octane,
        "OCTANE_VIEW_LAYER": preset_props.save_octane_view_layer,
        "OCTANE_IMAGER": preset_props.save_octane_imager,
        "OCTANE_POST": preset_props.save_octane_post,
        # User's Custom
        "USER_CUSTOM": preset_props.save_user_custom,
    }

    for category, should_save in categories_to_save.items():
        if should_save:
            settings = get_current_settings(category, context)
            if settings:
                # Flat save for legacy compatibility
                preset_data["render_presets"][category] = settings
                total_saved += len(settings)
                
                # Panel-structured save for v2.0
                scraped_panels = scrape_category_panels(category, context)
                category_panels_data = {}
                
                for p_info in scraped_panels:
                    p_id = p_info["id"]
                    p_label = p_info["label"]
                    p_props = {}
                    
                    for prop_path, short_name, full_label in p_info["properties"]:
                        if prop_path in settings:
                            p_props[prop_path] = settings[prop_path]
                            
                    if p_props:
                        category_panels_data[p_id] = {
                            "label": p_label,
                            "parent_id": p_info["parent_id"],
                            "properties": p_props
                        }
                        
                preset_data["categories"][category] = {
                    "panels": category_panels_data
                }

    if not preset_data["render_presets"]:
        return False, "No categories selected to save."

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, indent=4)
        return True, f"Preset '{preset_props.preset_name}' saved with {total_saved} settings."
    except Exception as e:
        return False, f"Failed to save preset: {str(e)}"



class RENDER_PRESET_OT_save(Operator, ExportHelper):
    """Save render settings as a preset file"""
    bl_idname = "render_preset.save"
    bl_label = "Save Preset to File..."
    bl_description = "Save current render settings as a preset file"
    
    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'}) # type: ignore
    
    def invoke(self, context, event):
        preset_props = context.scene.render_preset_settings
        preset_name_from_panel = preset_props.preset_name
        if preset_name_from_panel:
            safe_filename = "".join(c for c in preset_name_from_panel if c.isalnum() or c in (' ', '_')).rstrip()
            self.filepath = safe_filename.replace(' ', '_') + self.filename_ext
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        """This method now just calls the shared save function."""
        success, message = save_preset_to_file(context, self.filepath)
        
        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, message)
            return {'CANCELLED'}

# =============================================================================
# Save New file direct into the User Repository defined in the Addon PReferences
# =============================================================================
class RENDER_PRESET_OT_save_to_user_repo(bpy.types.Operator):
    """Saves the current settings directly to the user's defined presets directory."""
    bl_idname = "render_preset.save_to_user_repo"
    bl_label = "Save to User Repository"
    bl_description = "Saves the current preset directly to the folder defined in the addon preferences"

    @classmethod
    def poll(cls, context):
        try:
            prefs = utils.get_addon_preferences(context)
            return prefs and prefs.user_presets_path
        except:
            return False

    def execute(self, context):
        prefs = utils.get_addon_preferences(context)
        preset_props = context.scene.render_preset_settings
        
        if not preset_props.preset_name:
            self.report({'ERROR'}, "Preset Name cannot be empty.")
            return {'CANCELLED'}

        # Constrói o caminho de saída
        safe_filename = "".join(c for c in preset_props.preset_name if c.isalnum() or c in (' ', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_') + ".json"
        output_path = os.path.join(prefs.user_presets_path, safe_filename)

        # --- NOVA LÓGICA DE VERIFICAÇÃO ---
        if os.path.exists(output_path):
            # Se o arquivo JÁ EXISTE, chama o nosso novo operador de confirmação
            bpy.ops.render_preset.save_overwrite_confirm('INVOKE_DEFAULT', filepath=output_path)
            return {'FINISHED'}
        else:
            # Se o arquivo NÃO EXISTE, salva diretamente como antes
            success, message = save_preset_to_file(context, output_path)

            if success:
                self.report({'INFO'}, message)
                utils._user_presets_cache = None
            else:
                self.report({'WARNING'}, message)
            
            bpy.ops.render_preset.refresh_user()
            
            return {'FINISHED'}


# =============================================================================
#
# =============================================================================
class RENDER_PRESET_OT_save_overwrite_confirm(bpy.types.Operator):
    """Asks the user to confirm overwriting an existing preset file."""
    bl_idname = "render_preset.save_overwrite_confirm"
    bl_label = "Confirm Overwrite"

    filepath: bpy.props.StringProperty(options={'SKIP_SAVE'}) # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        filename = os.path.basename(self.filepath)
        
        layout.label(text=f"A preset named '{filename}' already exists.")
        layout.label(text="Do you want to overwrite it?")
        layout.separator()
        layout.label(text="This action cannot be undone.", icon='ERROR')

    def execute(self, context):
        """Executes the save/overwrite if the user clicks OK."""
        # Chama nossa função de salvamento reutilizável com o caminho do arquivo
        success, message = save_preset_to_file(context, self.filepath)

        if success:
            self.report({'INFO'}, message)
            # Força a atualização da lista de presets do usuário
            utils._user_presets_cache = None
        else:
            self.report({'WARNING'}, message)
            
        return {'FINISHED'}
    

classes = (
    RENDER_PRESET_OT_save,
    RENDER_PRESET_OT_save_to_user_repo,
    RENDER_PRESET_OT_save_overwrite_confirm,
)        