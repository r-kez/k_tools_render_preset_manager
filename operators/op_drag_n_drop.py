import bpy
import json

# =============================================================================
# DRAG AND DROP
# =============================================================================
def is_valid_preset_file(filepath):
    """
    Checks if a file is a valid preset for this addon by loading
    the JSON and checking for the essential 'render_presets' key.
    """
    if not filepath or not filepath.lower().endswith('.json'):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # A verificação mais confiável: o objeto foi carregado como um dicionário
        # e contém a nossa chave principal?
        if isinstance(data, dict) and "render_presets" in data:
            return True
            
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        # Captura erros específicos de leitura de arquivo ou JSON inválido
        return False
    
    return False

# =============================================================================
#
# =============================================================================
class RENDER_PRESET_OT_load_from_dragged_filepath(bpy.types.Operator):
    """
    Takes a filepath and initiates the load preview process.
    This is called by the FileHandler.
    """
    bl_idname = "render_preset.load_from_filepath"
    bl_label = "Load Preset from Filepath"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH", options={'SKIP_SAVE'}) # type: ignore

    def execute(self, context):
        if not self.filepath or not is_valid_preset_file(self.filepath):
            self.report({'WARNING'}, "The dropped file is not a valid preset file.")
            return {'CANCELLED'}
            
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            preset_props = context.scene.render_preset_settings
            preset_props.temp_preset_data = json.dumps(preset_data)
            preset_props.temp_preset_loaded = True

            bpy.ops.render_preset.load_preview('INVOKE_DEFAULT')

        except Exception as e:
            self.report({'ERROR'}, f"Failed to load preset file: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

# =============================================================================
#
# =============================================================================
class RENDER_PRESET_FH_drop_handler(bpy.types.FileHandler):
    """File handler for drag-and-dropping preset files."""
    bl_idname = "RENDER_PRESET_FH_drop_handler"
    bl_label = "Render Preset File Handler"
    bl_file_extensions = ".json"
    

    bl_import_operator = "render_preset.load_from_filepath"

    @classmethod
    def poll_drop(cls, context):
        return (context.area and context.area.type in {'PROPERTIES', 'VIEW_3D'})


classes = (
    RENDER_PRESET_OT_load_from_dragged_filepath,
    RENDER_PRESET_FH_drop_handler,
)