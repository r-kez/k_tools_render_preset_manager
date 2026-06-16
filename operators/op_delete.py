import bpy
import json
import os
# =============================================================================
# 
# =============================================================================
class RENDER_PRESET_OT_remove_user_preset(bpy.types.Operator):
    """Removes the selected user preset from the disk permanently."""
    bl_idname = "render_preset.remove_user_preset"
    # O bl_label agora será o título da janela de confirmação.
    bl_label = "Confirm Preset Deletion"
    bl_description = "Permanently deletes the selected preset file from your user library"

    # Property to store the file path between invoke() and execute()
    filepath_to_remove: bpy.props.StringProperty() # type: ignore

    @classmethod
    def poll(cls, context):
        """Enables the button only if a valid user preset is selected."""
        preset_props = context.scene.render_preset_settings
        return preset_props.user_preset_enum and preset_props.user_preset_enum != 'NONE'

    def invoke(self, context, event):
        """Opens the CUSTOM confirmation dialog before executing."""
        self.filepath_to_remove = context.scene.render_preset_settings.user_preset_enum

        return context.window_manager.invoke_props_dialog(self, width=350, cancel_default=True, confirm_text='Delete')

    def draw(self, context):
        """Draws a standard confirmation dialog layout."""
        layout = self.layout
        
        preset_name_internal = "N/A"
        try:
            with open(self.filepath_to_remove, 'r', encoding='utf-8') as f:
                data = json.load(f)
            preset_name_internal = data.get("preset_name", "Not Found")
        except Exception as e:
            print(f"Could not read preset name from file: {e}")
        
        filename_on_disk = os.path.basename(self.filepath_to_remove)

        # Pergunta principal
        layout.label(text="Are you sure you want to remove this preset?")
        layout.separator()

        # Caixa para agrupar as informações
        box = layout.box()
        
        # Mostra o nome do preset
        row = box.row()
        row.label(text="Preset Name:")
        row.label(text=preset_name_internal)

        # Mostra o nome do arquivo
        row = box.row()
        row.label(text="File to be Deleted:")
        row.label(text=filename_on_disk)

        layout.separator()

        # Mensagem final de aviso com um ícone de tamanho normal
        row = layout.row(align=True)
        row.alert = True
        row.alignment = 'CENTER'
        row.label(text="This action is permanent and cannot be undone.", icon='ERROR')
        row.alert = False

    def execute(self, context):
        """Executes the deletion if the user confirms."""
        if not self.filepath_to_remove or not os.path.exists(self.filepath_to_remove):
            self.report({'WARNING'}, "Preset file not found or invalid.")
            return {'CANCELLED'}

        try:
            filename = os.path.basename(self.filepath_to_remove)
            os.remove(self.filepath_to_remove)
            
            global _user_presets_cache
            _user_presets_cache = None
            
            self.report({'INFO'}, f"Preset '{filename}' was successfully removed.")

            bpy.ops.render_preset.refresh_user()

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to remove preset: {str(e)}")
            return {'CANCELLED'}
        

classes = (
    RENDER_PRESET_OT_remove_user_preset,
)        