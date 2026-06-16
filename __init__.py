import bpy
from .operators.op_user_presets import classes as ops_cls
from .operators.op_save import classes as save_ops
from .operators.op_undo import classes as undo_ops
from .operators.op_load import classes as load_cls
from .operators.op_delete import classes as delete_cls
from .operators.op_drag_n_drop import classes as drag_drop_cls
from .operators.op_black_list import classes as black_list_cls
from .ui_custom_props import classes as user_custom
from .ui import panels
from . import utils
from .operators import op_dev
from . import preferences
from .properties import properties

def _run_startup_sync():
    """Refresh Whitelist on Start after registration"""
    try:
        if hasattr(bpy.ops.render_preset, 'sync_blacklist'):
            bpy.ops.render_preset.sync_blacklist('EXEC_DEFAULT')
            bpy.ops.render_preset.refresh_user() # Refresh User's List | Prevents it to be empty while starting
            bpy.ops.render_preset.refresh_custom_props() # Refresh User's Custom List | Prevents it to be empty while starting

    except Exception as e:
        print(f"Render Preset Manager: Failed to auto-sync property list on startup: {e}")

    return None

classes = (
    *ops_cls,
    *save_ops,
    *undo_ops,    *load_cls,
    *drag_drop_cls,
    *delete_cls,
    *black_list_cls,
    *user_custom,
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    properties.register()    
    preferences.register()    
    panels.register()    
    op_dev.register()    

    bpy.types.RENDER_PT_context.prepend(panels.draw_prepended_ui)
    
    utils.ADDON_NAME = __package__

    if not bpy.app.background:
        bpy.app.timers.register(_run_startup_sync, first_interval=1)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.RENDER_PT_context.remove(panels.draw_prepended_ui)

    op_dev.unregister() 
    panels.unregister() 
    preferences.unregister() 
    properties.unregister() 


if __name__ == "__main__":
    register()