import bpy
from bpy.types import AddonPreferences
# ADDON IMPORT
from .properties.properties import BlacklistableProperty
from .properties import function_list
from . import utils
from .ui_custom_props import KTOOLS_CustomPropItem

#########################################################
# UI LIST FOR BLACKLIST
#########################################################
class RENDER_PRESET_UL_blacklist(bpy.types.UIList):
    """UIList with functional text search and tab filtering."""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "is_enabled", text="")
            row.label(text=item.name)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="")

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        
        # 1. Get search term
        query = getattr(data, "search_term", "").lower()
        
        # 2. Get active tab
        blacklist_props = context.scene.blacklist_props 
        active_tab = blacklist_props.engine_blacklist_tab
        
        # 3. Define tab mappings based on RENDER_SETTINGS keys
        BLACKLIST_TABS = {
            'NATIVE': [
                "RENDER_ENGINE",
                "CYCLES", 
                "BLENDER_EEVEE", 
                "BLENDER_WORKBENCH", 
                "BLENDER_OUTPUT", 
                "BLENDER_VIEW_LAYER", 
                "BLENDER_SCENE", 
                "USER_CUSTOM",
                function_list.COMMON_COLOR_MANAGEMENT
            ],
            'OCTANE': [
                "RENDER_ENGINE",
                "OCTANE", 
                "OCTANE_VIEW_LAYER", 
                "OCTANE_IMAGER", 
                "OCTANE_POST",
                "BLENDER_OUTPUT",
                "USER_CUSTOM",
                #function_list.OCTANE_OUTPUT_PROPS
            ]
        }
        
        valid_categories = BLACKLIST_TABS.get(active_tab, [])

        flt_flags = []
        flt_neworder = []
        include_item = self.bitflag_filter_item
        
        for item in items:
            show_item = True
            
            # --- FILTER A: Engine Tab Category ---
            if item.category not in valid_categories:
                show_item = False
                
            # --- FILTER B: Text Search ---
            if show_item and query:
                if query not in item.name.lower():
                    show_item = False
                    
            # --- FINAL DECISION ---
            if show_item:
                flt_flags.append(include_item)
            else:
                flt_flags.append(0)
                
        return flt_flags, flt_neworder


#########################################################
# ADD-ON PREFERENCES
def get_scraper_sources(self, context):
    """Provides the source items for the scraper tool."""
    return [
        ('SCENE', 'Scene', 'General scene properties (render, eevee, cycles)'),
        ('VIEW_LAYER', 'View Layer', 'Active view layer settings'),
        ('WORLD', 'World', 'World shader and lighting settings'),
    ]

class KToolsRenderPresetManagerPreferences(AddonPreferences):
    bl_idname = __package__
    user_presets_path: bpy.props.StringProperty(
        name="User Presets Directory",
        description="Directory where your personal render presets are stored",
        subtype='DIR_PATH',
        default=""
    ) # type: ignore

    show_filename_in_list: bpy.props.BoolProperty(
        name="Display Filename in List",
        description="Show the actual .json filename next to the preset name in the User Presets list",
        default=False
    ) # type: ignore
    dev_show_new_props: bpy.props.BoolProperty(
        name="Show new Props",
        description="",
        default=True
    ) # type: ignore

    show_whitelist: bpy.props.BoolProperty(
        name="Show Whitelist",
        description="",
        default=False
    ) # type: ignore

    show_custom_list: bpy.props.BoolProperty(
        name="Show User's List",
        description="Show User's Custom Property List",
        default=False
    ) # type: ignore

    panel_location: bpy.props.EnumProperty(
        name="Panel Location",
        description="Choose where the main addon panel appears in the UI",
        items=[
            ('PREPEND', "Top of Render Properties", "Injects the panel at the top of the Render tab"),
            ('HIDE_HEADER', "Bottom of Render Properties", "Injects the panel at the bottom of the Render tab"),
            ('PANEL', "Panel", "Shows the addon as its own separate panel")
        ],
        default='HIDE_HEADER'
    ) # type: ignore

    developer_extras: bpy.props.BoolProperty(
        name="Enable Developer Extras",
        description="Show extra tools for addon maintenance and debugging",
        default=False
    ) # type: ignore

    dev_scraper_source_type: bpy.props.EnumProperty(
        name="Source",
        description="Select the data source to scrape",
        items=get_scraper_sources,
        default=0
    ) # type: ignore
    
    dev_scraper_filter_path: bpy.props.StringProperty(
        name="Filter Path",
        description="Sub-path to scrape (e.g., 'cycles', 'eevee', 'render.image_settings')",
        default=""
    ) # type: ignore
    
    dev_scraper_max_depth: bpy.props.IntProperty(
        name="Max Depth",
        description="Recursive depth for scraping",
        default=6, min=1, max=10
    ) # type: ignore

### BLACKLIST SYSTEM
    blacklist_items: bpy.props.CollectionProperty(
        type=BlacklistableProperty
        ) # type: ignore  
    blacklist_active_index: bpy.props.IntProperty(
        
    ) # type: ignore  

    search_term: bpy.props.StringProperty(
        name="Search",
        description="Filter properties by name",
        default=""
    ) # type: ignore 

## Display Mode
    preset_display_style: bpy.props.EnumProperty(
            name="Preset Display Style",
            description="Choose how to display the presets in the main panel",
            items=[
                ('DROPDOWN', "Dropdown Menu", "Compact view (Classic)"),
                ('LIST', "UI List", "Expanded list view (Better for many presets)"),
            ],
            default='DROPDOWN'
        ) # type: ignore 

## User's Custom Strings
    custom_properties: bpy.props.CollectionProperty(type=KTOOLS_CustomPropItem) # type: ignore 
    custom_prop_index: bpy.props.IntProperty() # type: ignore 

    def draw(self, context):
        layout = self.layout
        blacklist_props = context.scene.blacklist_props
        
        # ========== SEÇÃO: CONFIGURAÇÕES GERAIS ==========
        box = layout.box()
        box.label(text="General Settings", icon='PREFERENCES')
        
        # User Presets Path
        col = box.column(align=True)
        col.scale_y = 0.9
        col.label(text="User Presets Path:")
        col.prop(self, "user_presets_path", text='')
        
        # Opções gerais
        col = box.column(align=True)
        col.prop(self, "show_filename_in_list")
        col.prop(self, "panel_location")
        col.prop(self, "preset_display_style")
        
        # ========== SEÇÃO: PROPERTY WHITELIST ==========
        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        ICON = 'TRIA_DOWN' if self.show_whitelist else 'TRIA_RIGHT'
        row.label(text="", icon='FILTER')
        row.prop(self, 'show_whitelist', text="Whitelist", icon=ICON, emboss=False)

        if self.show_whitelist:
            if utils.is_engine_available(context, 'octane'):
                row = box.row(align=True)
                #row.label(text='Engine:', icon='PREFERENCES')
                row.prop(blacklist_props, 'engine_blacklist_tab', expand=True)
                row.scale_x = 1.5
                row.operator("render_preset.sync_blacklist", icon='FILE_REFRESH', text='')

            # Campo de busca
            row = box.row(align=True)
            #row.label(text="Filter:")
            row.prop(self, "search_term", text="", icon='VIEWZOOM')
            
            if self.search_term:
                op = row.operator("wm.context_set_string", text="", icon='X')
                op.data_path = "preferences.addons['bl_ext.vscode_development.k_tools_render_preset_manager'].preferences.search_term"
                op.value = ""
            
            # Lista de propriedades
            box.template_list(
                "RENDER_PRESET_UL_blacklist",
                "",
                self,
                "blacklist_items",
                self,
                "blacklist_active_index",
                rows=10
            )

            # Info helper
            row = box.row()
            row.scale_y = 0.8
            row.alignment = 'RIGHT'
            row.label(text="Items marked as True will be loaded by default", icon='INFO')
        
        # User Custom List and Ops
        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        ICON = 'TRIA_DOWN' if self.show_custom_list else 'TRIA_RIGHT'
        row.label(text="", icon='USER')
        row.prop(self, 'show_custom_list', text="User's Custom List", icon=ICON, emboss=False)

        if self.show_custom_list:
            row = box.row(align=True)
            row.label(text="Property Name:")
            row.label(text="Property Path:")

            row = box.row(align=True)
            # Chama a nossa UIList customizada
            row.template_list("KTOOLS_UL_custom_props", "", self, "custom_properties", self, "custom_prop_index")
            col = row.column(align=True)
            col.operator("render_preset.refresh_custom_props", icon='FILE_REFRESH', text="")
            col.operator("render_preset.add_custom_prop", icon='ADD', text="")
            col.operator("render_preset.remove_custom_prop", icon='REMOVE', text="")
            # --- AVISO PARA O USUÁRIO ---
            row = box.row(align=True)
            col = row.column(align=True)
            col.alert = True
            col.label(text="Tip: For global settings, use 'bpy.data...' or 'bpy.context.preferences...'.", icon='INFO')
            col.label(text="Avoid 'context.active_object' or 'space_data' as they depend on selection or mouse position.", icon='BLANK1')
            col.alert = False


        # ========== SEÇÃO: LINKS E SUPORTE ==========
        box = layout.box()
        box.label(text="Help & Support", icon='QUESTION')
        
        row = box.row(align=True)
        row.operator("wm.url_open", text="Documentation", icon='URL'
                    ).url = "https://github.com/r-kez/k_tools_render_preset_manager/wiki"
        
        row.operator("wm.url_open", text="Report a Bug", icon='URL'
                    ).url = "https://github.com/r-kez/k_tools_render_preset_manager/issues"
        
        # ========== SEÇÃO: FERRAMENTAS DE DESENVOLVEDOR ==========
        box = layout.box()
        
        # Header colapsável com o boolean como parte do header
        row = box.row(align=True)
        row.prop(self, "developer_extras", 
                text="Developer Tools", 
                icon='TRIA_DOWN' if self.developer_extras else 'TRIA_RIGHT',
                emboss=False)
        
        # Conteúdo das ferramentas (só aparece se expandido)
        if self.developer_extras:
            box.separator(factor=0.5)

            box.label(text="Property Auditor")
            
            box.prop(self, "dev_audit_category")

            # Configurações do scraper
            col = box.column(align=True)
            
            split = col.split(factor=0.3, align=True)
            split.label(text="Source:")
            split.prop(self, "dev_scraper_source_type", text="")
            
            split = col.split(factor=0.3, align=True)
            split.label(text="Filter Path:")
            split.prop(self, "dev_scraper_filter_path", text="")
            
            split = col.split(factor=0.3, align=True)
            split.label(text="Depth:")
            split.prop(self, "dev_scraper_max_depth", text="")

            # Botões de ação
            row = box.row(align=True)
            row.operator("render_preset.generate_new_list", 
                        text="Generate List",
                        icon='TEXT')
            row.operator("render_preset.validate_list",
                        text="Validate",
                        icon='FILE_REFRESH')
            
            row.separator()
            row = box.row(align=True)
            row.label(text="Fuzz Test:", icon='GHOST_ENABLED')
            row = box.row(align=True)
            row.operator("render_preset.fuzz_test_scene", icon='GHOST_ENABLED')


classes = (
    RENDER_PRESET_UL_blacklist,
    KToolsRenderPresetManagerPreferences,
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()