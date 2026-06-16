import bpy
from .. import utils

RENDER_SETTINGS = utils.get_all_render_settings()

class RENDER_PRESET_OT_sync_blacklist(bpy.types.Operator):
    """
    Scans RENDER_SETTINGS and updates the user's blacklist collection,
    preserving existing user choices.
    """
    bl_idname = "render_preset.sync_blacklist"
    bl_label = "Sync Property List"
    
    def execute(self, context):        
        prefs = utils.get_addon_preferences(context)
        
        # 1. Guarda as escolhas atuais para não resetar os checkboxes do usuário
        existing_choices = {item.path: item.is_enabled for item in prefs.blacklist_items}
        
        # 2. Limpa a lista defasada da memória
        prefs.blacklist_items.clear()
        
        # 3. Puxa a lista 100% atualizada (Nativas + O JSON Customizado que acabou de ser salvo)
        # Importe a função de onde você a colocou (provavelmente no utils ou custom_props_manager)
        latest_settings = utils.get_all_render_settings()
        
        # 4. Repopula a coleção
        for category_name, properties in latest_settings.items():
            for path, friendly_name in properties:
                new_item = prefs.blacklist_items.add()
                
                new_item.name = friendly_name 
                new_item.path = path
                new_item.category = category_name
                new_item.is_enabled = existing_choices.get(path, True)

        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type in {'PREFERENCES', 'PROPERTIES'}:
                    area.tag_redraw()
                    
        return {'FINISHED'}
    
classes = (
    RENDER_PRESET_OT_sync_blacklist,
)