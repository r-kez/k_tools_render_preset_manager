import bpy
from bpy.props import (
    StringProperty, 
    EnumProperty, 
    BoolProperty,
    PointerProperty
)
from bpy.props import CollectionProperty
from bpy.types import PropertyGroup
from ..operators.op_user_presets import get_default_presets, get_user_presets
from ..utils import get_addon_preferences
import os

class UserPresetItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty() # type: ignore
    filepath: bpy.props.StringProperty() # type: ignore

class BlacklistableProperty(bpy.types.PropertyGroup):
    """ 'Molde' para um item na nossa UIList de blacklist """

    # Renomeie 'friendly_name' para 'name'
    name: bpy.props.StringProperty(name="Property Name") # type: ignore
    
    path: bpy.props.StringProperty() # type: ignore
    category: bpy.props.StringProperty() # type: ignore
    
    is_enabled: bpy.props.BoolProperty(
        name="",
        description="Allow this property to be saved or loaded by the addon",
        default=True
    ) # type: ignore

    engine_blacklist_tab: bpy.props.EnumProperty(
        name="Engine Tab",
        items=[
            ('NATIVE', "Native Engines", "Native Blender settings"),
            ('OCTANE', "Octane", "Octane Render settings")
        ],
        default='NATIVE'
    ) # type: ignore

def check_for_duplicate_name_callback(self, context):
    """
    Called every time 'preset_name' is changed.
    Checks if a file with the same name already exists in the user directory.
    """
    # Pega as preferências para encontrar a pasta do usuário
    prefs = get_addon_preferences(context)
    if not prefs or not prefs.user_presets_path:
        self.preset_name_exists = False
        return

    # Pega o nome que o usuário está digitando
    preset_name = self.preset_name
    if not preset_name:
        self.preset_name_exists = False
        return

    # Gera o nome de arquivo correspondente, da mesma forma que o operador de salvar
    safe_filename = "".join(c for c in preset_name if c.isalnum() or c in (' ', '_')).rstrip()
    safe_filename = safe_filename.replace(' ', '_') + ".json"
    
    # Constrói o caminho completo e verifica se ele existe
    potential_filepath = os.path.join(prefs.user_presets_path, safe_filename)
    
    # Atualiza a flag. O painel lerá esta flag para mostrar/esconder o aviso.
    self.preset_name_exists = os.path.exists(potential_filepath)

# =============================================================================
# PROPERTY GROUPS
# =============================================================================
class RenderPresetSettings(PropertyGroup):
    preset_name: StringProperty(
        name="Preset Name",
        description="Name for the render preset",
        default="New Preset",
        update=check_for_duplicate_name_callback
    ) # type: ignore
    
    preset_description: StringProperty(        name="Description",
        description="Optional description for the preset",
        default=""
    ) # type: ignore
    
    save_cycles: BoolProperty(
        name="Save Cycles Settings",
        description="Include Cycles render settings in the preset",
        default=True
    ) # type: ignore
    
    save_eevee: BoolProperty(
        name="Save Eevee Settings",
        description="Include Eevee render settings in the preset",
        default=True
    ) # type: ignore
    
    save_workbench: BoolProperty(
        name="Save Workbench Settings",
        description="Include Workbench render settings in the preset",
        default=True
    ) # type: ignore

    save_output: BoolProperty(
        name="Save Output Settings",
        description="Include Output render settings in the preset",
        default=False
    ) # type: ignore
    
    save_view_layer: BoolProperty(
        name="Save View Layer Settings",
        description="Include View Layer settings in the preset",
        default=False
    ) # type: ignore

    save_scene: BoolProperty(
        name="Save Scene Settings",
        description="Include Scene settings in the preset",
        default=False
    ) # type: ignore    

    save_render_engine: BoolProperty(
        name="Save Render Engine",
        description="Include the current Render Engine in the Scene",
        default=True
    ) # type: ignore

    save_octane: bpy.props.BoolProperty(
        name="Octane Render Properties",
        description="Save Octane Render settings",
        default=False
    ) # type: ignore

    save_octane_view_layer: bpy.props.BoolProperty(
        name="Octane View Layer",
        description="Save Octane Render settings",
        default=False
    ) # type: ignore

    save_octane_imager: bpy.props.BoolProperty(
        name="Octane Imager",
        description="Save Octane Imager settings",
        default=False
    ) # type: ignore

    save_octane_post: bpy.props.BoolProperty(
        name="Octane Postprocess",
        description="Save Octane Postprocess settings",
        default=False
    ) # type: ignore

    save_user_custom: bpy.props.BoolProperty(
        name="User Custom Properties",
        description="Save the user-defined custom properties",
        default=True
    ) # type: ignore

    # Properties for temporary data and undo state
    temp_preset_data: StringProperty(default="") # type: ignore
    temp_preset_loaded: BoolProperty(default=False) # type: ignore

    undo_data: StringProperty(description="Stores the previous settings state for undo", default="") # type: ignore
    loaded_preset_name: StringProperty(description="Name of the currently loaded preset", default="") # type: ignore

    preview_preset_path: StringProperty(
        name="Preview Preset Path",
        description="Path to the preset file used for automated previews",
        subtype='FILE_PATH',
        default=""
    ) # type: ignore

    default_preset_enum: EnumProperty(
        name="Default Presets",
        description="Select a built-in default preset to load",
        items=get_default_presets
    ) # type: ignore

    user_preset_enum: EnumProperty(
        name="User Presets",
        description="Selecionar um preset do seu diretório customizado",
        items=get_user_presets
    ) # type: ignore

    load_mode_enum: EnumProperty(
        name="Load Mode",
        description="Choose which mode the user will be able to load",
        items=[
            ('LOAD_USER',       "User Presets",     "Load from a pre determined directory set in the Add-on's Preferences."),
            ('LOAD_NEW',        "From File",        "Load a new file from a custom directory."),
            ('LOAD_DEFAULT',    "Default",          "Load Blender's default settings."),
            ('SAVE_PRESET',     "Save Preset",      "Save Preset from Scene."),
        ],
        default='LOAD_USER'
    ) # type: ignore    
    last_loaded_preset_path: StringProperty(
        name="Last Loaded Preset Path",
        description="Internal property to store the path of the last loaded preset for the update function",
        default=""
    ) # type: ignore

    show_main_panel: BoolProperty(
        name="Expand Main Panel",
        description="Show or collapse the main Render Preset Manager panel in the Render Properties tab",
        default=False
    ) # type: ignore

    preset_name_exists: BoolProperty(
        name="Preset Name Exists",
        description="Internal flag to check if a preset with the current name already exists",
        default=False
    ) # type: ignore    

## For UI List Mode
    user_presets_collection: bpy.props.CollectionProperty(type=UserPresetItem) # type: ignore   
    active_user_index: bpy.props.IntProperty(default=0) # type: ignore   


class PresetAPIEntry(PropertyGroup):
    """Armazena os dados limpos de um único preset para acesso externo."""
    name: StringProperty(name="Preset Name") # type: ignore   
    filepath: StringProperty(name="File Path") # type: ignore   

class RenderPresetAPI(PropertyGroup):
    """O 'ponto de acesso' principal que conterá a lista de presets."""
    presets: CollectionProperty(type=PresetAPIEntry) # type: ignore 

classes = (
    UserPresetItem,
    BlacklistableProperty,
    RenderPresetSettings,
    PresetAPIEntry, 
    RenderPresetAPI,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.render_preset_settings = PointerProperty(type=RenderPresetSettings)
    bpy.types.Scene.render_preset_api = PointerProperty(type=RenderPresetAPI)
    bpy.types.Scene.blacklist_props = PointerProperty(type=BlacklistableProperty)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.blacklist_props
    del bpy.types.Scene.render_preset_api
    del bpy.types.Scene.render_preset_settings


if __name__ == "__main__":
    register()