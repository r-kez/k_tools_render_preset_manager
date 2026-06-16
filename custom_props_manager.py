import os
import json

def get_custom_props_filepath():
    """Busca o arquivo na raiz do addon de forma segura"""
    # __package__ em um addon Blender costuma ser 'bl_ext.user_default.k_tools_render_preset_manager'
    # Precisamos do caminho físico onde esse pacote está instalado
    addon_id = __package__.split('.')[0] if "." in __package__ else __package__
    
    # Busca o caminho do diretório da extensão/addon
    import addon_utils
    for mod in addon_utils.modules():
        if mod.__name__ == __package__:
            addon_dir = os.path.dirname(mod.__file__)
            return os.path.join(addon_dir, "custom_properties.json")
            
    # Fallback caso o método acima falhe (o método de subir pastas)
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "custom_properties.json")

def load_custom_props():
    """Lê o JSON do disco. Se não existir ou estiver corrompido, cria um novo vazio."""
    filepath = get_custom_props_filepath()
    
    # 1. Se o arquivo não existe, cria um zerado e retorna lista vazia
    if not os.path.exists(filepath):
        _create_empty_json(filepath)
        return []
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # 2. Se o arquivo existe mas está totalmente vazio
            if not content:
                _create_empty_json(filepath)
                return []
                
            data = json.loads(content)
            
        custom_list = []
        for item in data.get("USER_CUSTOM", []):
            custom_list.append((item.get("data_path", ""), item.get("friendly_name", "")))
            
        return custom_list
    except json.JSONDecodeError:
        # 3. Se o JSON estiver quebrado/mal formatado, reseta ele por segurança
        print("K-Tools: Custom properties JSON is corrupted. Recreating empty file.")
        _create_empty_json(filepath)
        return []
    except Exception as e:
        print(f"K-Tools: Error reading custom properties - {e}")
        return []

def _create_empty_json(filepath):
    """Função interna auxiliar para criar a estrutura base do JSON"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"USER_CUSTOM": []}, f, indent=4)
    except Exception as e:
        print(f"K-Tools: Failed to create default JSON - {e}")

def save_custom_props(collection_property):
    """Lê a Collection da UI do Blender e salva no disco"""
    filepath = get_custom_props_filepath()
    
    formatted_data = []
    for item in collection_property:
        # Só salva se os campos não estiverem vazios
        if item.data_path.strip() or item.friendly_name.strip():
            formatted_data.append({
                "data_path": item.data_path.strip(),
                "friendly_name": item.friendly_name.strip()
            })
        
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"USER_CUSTOM": formatted_data}, f, indent=4)
    except Exception as e:
        print(f"K-Tools: Error auto-saving custom properties - {e}")
