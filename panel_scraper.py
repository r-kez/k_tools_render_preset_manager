"""
panel_scraper.py
----------------
Module for dynamically scraping Blender UI Panels (bpy.types.Panel)
and extracting properties organized by Category and Panel (Sub-category).
"""

import bpy
from collections import defaultdict
from .properties.function_list import RENDER_SETTINGS, COMMON_COLOR_MANAGEMENT

# Cache to avoid re-scanning panel subclasses repeatedly during UI draw
_SCRAPED_PANELS_CACHE = {}

CATEGORY_CONTEXT_MAP = {
    "RENDER_ENGINE": {
        "context": "render",
        "prefix": "render.engine",
    },
    "CYCLES": {
        "context": "render",
        "panel_prefix": "CYCLES_RENDER_PT_",
        "target_prefix": "cycles.",
    },
    "BLENDER_EEVEE": {
        "context": "render",
        "panel_prefix": "EEVEE_PT_",
        "target_prefix": "eevee.",
    },
    "BLENDER_WORKBENCH": {
        "context": "render",
        "panel_prefix": "WORKBENCH_PT_",
        "target_prefix": "display.",
    },
    "BLENDER_OUTPUT": {
        "context": "output",
        "panel_prefix": "RENDER_PT_",
        "target_prefix": "render.",
    },
    "BLENDER_VIEW_LAYER": {
        "context": "view_layer",
        "panel_prefix": "VIEWLAYER_PT_",
        "target_prefix": "<ACTIVE_VIEW_LAYER>.",
    },
    "BLENDER_SCENE": {
        "context": "scene",
        "panel_prefix": "SCENE_PT_",
        "target_prefix": "scene.",
    },
    "OCTANE": {
        "context": "render",
        "panel_prefix": "OCTANE_",
        "target_prefix": "octane.",
    },
    "OCTANE_VIEW_LAYER": {
        "context": "view_layer",
        "panel_prefix": "OCTANE_",
        "target_prefix": "octane.",
    },
    "OCTANE_IMAGER": {
        "context": "render",
        "panel_prefix": "OCTANE_",
        "target_prefix": "octane.",
    },
    "OCTANE_POST": {
        "context": "render",
        "panel_prefix": "OCTANE_",
        "target_prefix": "octane.",
    },
}


def clear_scraper_cache():
    """Clears the scraped panels cache, forcing a rescrape on next query."""
    global _SCRAPED_PANELS_CACHE
    _SCRAPED_PANELS_CACHE.clear()


def get_all_registered_panels(context=None):
    """
    Returns a dictionary of all registered properties panels grouped by bl_context.
    """
    panels_by_context = defaultdict(list)
    
    for cls in bpy.types.Panel.__subclasses__():
        space = getattr(cls, "bl_space_type", "")
        if space != 'PROPERTIES':
            continue
        
        ctx = getattr(cls, "bl_context", "")
        label = getattr(cls, "bl_label", "")
        idname = getattr(cls, "bl_idname", cls.__name__)
        parent_id = getattr(cls, "bl_parent_id", "")
        
        if label and idname:
            panels_by_context[ctx].append({
                "id": idname,
                "label": label,
                "parent_id": parent_id,
                "cls": cls,
            })
            
    return panels_by_context


def scrape_category_panels(category_key, context=None):
    """
    Scrapes panels and properties for a given category key (e.g. 'CYCLES', 'BLENDER_OUTPUT').
    Returns a list of panel data dicts:
    [
        {
            "id": "CYCLES_RENDER_PT_sampling",
            "label": "Sampling",
            "parent_id": "",
            "properties": [
                ("cycles.samples", "Render: Samples", "Full Display Label"), ...
            ]
        }, ...
    ]
    """
    global _SCRAPED_PANELS_CACHE
    
    # Check cache first
    cache_key = f"{category_key}_{bpy.app.version_string}"
    if cache_key in _SCRAPED_PANELS_CACHE:
        return _SCRAPED_PANELS_CACHE[cache_key]
        
    config = CATEGORY_CONTEXT_MAP.get(category_key, {})
    target_ctx = config.get("context", "")
    panel_prefix = config.get("panel_prefix", "")
    
    panels_by_ctx = get_all_registered_panels(context)
    candidate_panels = panels_by_ctx.get(target_ctx, [])
    
    # Get known settings list as base reference for clean labels and accuracy
    baseline_props = RENDER_SETTINGS.get(category_key, [])
    if category_key == "BLENDER_SCENE":
        baseline_props = baseline_props + COMMON_COLOR_MANAGEMENT
        
    panel_dict = {}
    
    # Process matching registered panels
    for p in candidate_panels:
        p_id = p["id"]
        p_label = p["label"]
        if panel_prefix and not p_id.startswith(panel_prefix) and category_key not in ("BLENDER_SCENE", "BLENDER_OUTPUT"):
            continue
            
        panel_dict[p_id] = {
            "id": p_id,
            "label": p_label,
            "parent_id": p["parent_id"],
            "properties": []
        }
        
    # Assign baseline properties to panels based on sub-group name
    unassigned_props = []
    for path, label in baseline_props:
        parts = label.split(":", 1)
        subgroup = parts[0].strip() if len(parts) > 1 else "General"
        short_name = parts[1].strip() if len(parts) > 1 else label
        
        matched = False
        for p_id, p_data in panel_dict.items():
            if p_data["label"].lower() == subgroup.lower() or subgroup.lower() in p_data["label"].lower():
                p_data["properties"].append((path, short_name, label))
                matched = True
                break
                
        if not matched:
            unassigned_props.append((path, short_name, label, subgroup))
            
    # Group unassigned properties into panels by subgroup name
    subgroup_panels = defaultdict(list)
    for path, short_name, label, subgroup in unassigned_props:
        subgroup_panels[subgroup].append((path, short_name, label))
        
    for subgroup, props in subgroup_panels.items():
        p_id = f"DYNAMIC_PT_{category_key.lower()}_{subgroup.lower().replace(' ', '_')}"
        if p_id not in panel_dict:
            panel_dict[p_id] = {
                "id": p_id,
                "label": subgroup,
                "parent_id": "",
                "properties": []
            }
        panel_dict[p_id]["properties"].extend(props)
        
    # Filter out empty panels
    result_panels = [p for p in panel_dict.values() if p["properties"]]
    
    # Store in cache
    _SCRAPED_PANELS_CACHE[cache_key] = result_panels
    return result_panels
