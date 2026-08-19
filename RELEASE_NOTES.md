# Release Notes - v2.0.0

## 🚀 Major Update: Panel-Based Dynamic Scraping Engine & Schema v2.0

### Highlights & Key Features:
- **Dynamic Panel Scraper (`bpy.types.Panel`)**:
  - Replaced the legacy static property list with an automated UI Panel scraping engine.
  - Automatically groups settings into their exact Blender UI panels (*Sampling*, *Light Paths*, *Color Management*, *Passes*, *Format*, etc.) under category tabs (*Cycles*, *EEVEE*, *Workbench*, *Output*, *View Layer*, *Scene*, *Octane*).
  - **Future-Proof**: Automatically detects newly added Blender features (like new Data Passes in Blender 5.2/5.3) without needing manual addon updates.

- **Dual Schema Architecture (`schema_version 2.0.0`)**:
  - Presets are saved with structured panel hierarchies (`"categories"`) for v2.0 UI while preserving flat fallback dictionaries (`"render_presets"`) for complete cross-version compatibility.

- **100% Backward Compatibility**:
  - Automatically loads and converts legacy v1.x preset `.json` files into the panel hierarchy in memory with zero data loss.

- **Redesigned Preferences & Load Dialog UI**:
  - **Preferences**: Interactive panel hierarchy viewer with category tabs, search filtering, and per-property whitelist toggles.
  - **Load Preview Dialog**: Compact, 3-column grid layout (`grid_flow`) with toggle buttons for selecting modules to load.

- **Security & Extensions Compliance**:
  - 100% clean codebase using official Blender Python API introspection (`bpy.types.Panel.__subclasses__()` and `getattr()`). Zero `eval()`, `exec()`, or dynamic string execution.

---

# Release Notes - v1.3.1

## Security & Compatibility Improvements
- **Unsafe Execution Cleanup**: Completely audited all code files and eliminated references to dynamic code execution methods (`exec()` / `eval()`).
- **Safe Property Resolution**: Replaced dynamic lookup expressions with native, safe attribute-traversal logic (`getattr()` / `setattr()` and custom string parsers).
- **Extension Platform Alignment**: Updated the addon's manifest version to `1.3.1` and ensured strict compliance with Blender Extensions Platform guidelines for automated validator review.
