# Render Preset Manager

A comprehensive Blender addon for saving, loading, and managing complete render setting profiles for **Cycles**, **EEVEE**, and **Workbench**.  
This tool is designed to streamline your workflow, allowing for quick, consistent, and reversible changes to your render setup.

**Location:** `Properties > Render Properties > Render Presets Manager`

---
<p align="center">
  <img src="https://public-files.gumroad.com/95q6lpdd3phmljfsl5vxc0bclglq" alt="Render Preset Manager" />
</p>
---

## Features

- **Save & Load Profiles**: Save all important render settings for Cycles, Eevee, and Workbench into a single `.json` file.  
- **Detailed Preview on Load**: Before applying a preset, a detailed, collapsible preview window shows you exactly which settings will change and what their new values will be.  
- **One-Click Undo**: After loading a preset, an "Undo" button appears in the panel, allowing you to instantly revert all settings to their state before the load.  
- **Built-in Default Presets**: Ships with a library of default presets (e.g., for different Blender versions or quality levels), dynamically loaded from a presets folder within the addon.  
- **Custom User Preset Library**: Set your own custom folder in the Addon Preferences to create a personal, organized library of your most-used presets. Listed directly in the UI for quick access.  
- **Quick Save to Library**: Save your current setup directly to your custom user library with a single click, without needing a file browser.  
- **Robust Data Support**: Correctly saves and loads complex data types, including Colors, Vectors, and custom Curves (`CurveMapping` objects for things like Motion Blur).  
- **Automation Ready**: Includes silent operators (`render_preset.load_from_path`, `render_preset.undo_direct`) callable from scripts or addons for automated workflows (e.g., apply a preview preset, render, and revert).  

---

## Installation

1. Download the latest version as a `.zip` file.  
2. In Blender, go to `Edit > Preferences > Add-ons`.  
3. Click **Install from disk...** and select the downloaded `.zip` file.  
4. Enable the addon by checking the box next to its name, **Render Preset Manager**.  
###     Or simply, **drag and drop the `.zip` into Blender**.  

---

## How to Use

### Location
The main panel is located in the **Properties Editor**, under the **Render Properties** tab.

---

### 1. Setting Up (Recommended First Step)

For the best experience, set up your personal presets folder:

1. Go to `Edit > Preferences > Add-ons`.  
2. Find **Render Preset Manager** and expand its options.  
3. In the **User Presets Directory** field, select a folder on your computer where you want to store your personal presets.  

---

### 2. Saving a Preset

1. Configure your render and output settings as desired.  
2. Go to the **Render Preset Manager** panel in the Render Properties tab.  
3. Under **Save Preset**, give your preset a **Name** and an optional **Description**.  
4. Use toggles to select which categories of settings to include.  
5. Choose one of the two save methods:
   - **Save to User Repository (Recommended):** Saves directly into your user presets folder (filename auto-generated).  
   - **Save Preset to File...:** Opens a file browser, allowing you to save anywhere on your computer.  

---

### 3. Loading a Preset

You have three ways to load a preset:

- **Default Presets:** Select a built-in preset from the dropdown and click **Load Selected Default**.  
- **User Presets:** Select a personal preset from the dropdown and click **Load Selected User Preset**.  
- **Load from File:** Click **Load Preset from File**, choose a `.json` preset from your computer.  

After selecting a preset:  
- A **Load Render Preset preview window** will appear, showing all changes.  
- Click **OK** to apply them.  
- An **Undo** button will appear, allowing you to revert changes if needed.  
