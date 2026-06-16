import bpy
from .custom_props_manager import load_custom_props, save_custom_props
ADDON_ID = __package__

# 1. Função isolada que vai rodar FORA do loop da interface
def delayed_sync():
    try:
        # Roda o seu operador em paz, com o contexto correto
        bpy.ops.render_preset.sync_blacklist('EXEC_DEFAULT')
        
        # Opcional: Força a interface de Propriedades a atualizar para mostrar o novo item
        if bpy.context.screen:
            for area in bpy.context.screen.areas:
                if area.type == 'PROPERTIES':
                    area.tag_redraw()
    except Exception as e:
        print(f"K-Tools Sync Error: {e}")
        
    return None # Retorna None para o timer não se repetir infinitamente

# --- 1. FUNÇÃO DE AUTO-SAVE (CALLBACK) ---
def on_prop_update(self, context):
    """É chamada automaticamente sempre que o usuário edita um campo de texto"""
    try:
        prefs = context.preferences.addons[ADDON_ID].preferences
        save_custom_props(prefs.custom_properties)
        
        # SISTEMA DE DEBOUNCE (Prevenção de Lag)
        # Se o usuário ainda estiver digitando (timer já existe), cancela o antigo
        if bpy.app.timers.is_registered(delayed_sync):
            bpy.app.timers.unregister(delayed_sync)
            
        # Agenda o sync para 0.5 segundos APÓS ele parar de digitar
        bpy.app.timers.register(delayed_sync, first_interval=0.5)
        
    except Exception as e:
        print(f"K-Tools Auto-Save Error: {e}")

# --- 2. O ITEM DA LISTA ---
class KTOOLS_CustomPropItem(bpy.types.PropertyGroup):
    data_path: bpy.props.StringProperty(
        name="", 
        description="RNA Data Path (e.g. scene.luxcore.light)", 
        update=on_prop_update # Engatilha o Auto-Save
    ) # type: ignore
    friendly_name: bpy.props.StringProperty(
        name="", 
        description="Display Name (e.g. LuxCore Light)", 
        update=on_prop_update # Engatilha o Auto-Save
    ) # type: ignore

# --- 3. A UILIST CUSTOMIZADA ---
class KTOOLS_UL_custom_props(bpy.types.UIList):
    """Desenha os campos editáveis diretamente na linha da lista"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Divide a linha em duas colunas para Nome e Path ficarem lado a lado
        row = layout.row(align=True)
        # 40% do espaço para o nome, 60% para o caminho real
        #split.label(text=f"{index + 1:02d}")
        split = row.split(factor=0.4) 
        split.prop(item, "friendly_name", text="", icon='EVENT_N', emboss=False)
        split.prop(item, "data_path", text="", icon='EVENT_P', emboss=False)

# --- 4. OPERADORES (ADD, REMOVE, REFRESH) ---
class KTOOLS_OT_add_custom_prop(bpy.types.Operator):
    """Adiciona uma nova propriedade customizada em branco"""
    bl_idname = "render_preset.add_custom_prop"
    bl_label = "Add Custom Property"

    def execute(self, context):
        prefs = context.preferences.addons[ADDON_ID].preferences
        prefs.custom_properties.add()
        prefs.custom_prop_index = len(prefs.custom_properties) - 1
        
        # Salva no disco imediatamente
        save_custom_props(prefs.custom_properties)
        return {'FINISHED'}

class KTOOLS_OT_remove_custom_prop(bpy.types.Operator):
    """Remove a propriedade selecionada"""
    bl_idname = "render_preset.remove_custom_prop"
    bl_label = "Remove Custom Property"

    def execute(self, context):
        prefs = context.preferences.addons[ADDON_ID].preferences
        idx = prefs.custom_prop_index
        
        if 0 <= idx < len(prefs.custom_properties):
            prefs.custom_properties.remove(idx)
            # Ajusta o índice para não dar erro na UI
            prefs.custom_prop_index = min(idx, len(prefs.custom_properties) - 1)
            
            # Salva no disco imediatamente
            save_custom_props(prefs.custom_properties)
            
        return {'FINISHED'}

class KTOOLS_OT_refresh_custom_props(bpy.types.Operator):
    """Força a sincronização da UI com o JSON físico no disco"""
    bl_idname = "render_preset.refresh_custom_props"
    bl_label = "Refresh from File"
    bl_description = "Reload custom properties from the JSON file"

    def execute(self, context):
        prefs = context.preferences.addons[ADDON_ID].preferences
        prefs.custom_properties.clear()
        
        saved_items = load_custom_props()
        for path, name in saved_items:
            item = prefs.custom_properties.add()
            item.data_path = path
            item.friendly_name = name
            
        self.report({'INFO'}, "Custom properties reloaded from JSON.")
        return {'FINISHED'}


classes = (
    KTOOLS_CustomPropItem,
    KTOOLS_UL_custom_props,
    KTOOLS_OT_add_custom_prop,
    KTOOLS_OT_remove_custom_prop,
    KTOOLS_OT_refresh_custom_props,

)