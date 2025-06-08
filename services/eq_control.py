import subprocess
import os
import json

# Path where EasyEffects stores its presets
EASYEFFECTS_PRESETS_PATH = os.path.expanduser("~/.config/easyeffects/output/")

def get_available_presets():
    """
    Get a list of available EasyEffects presets.
    """
    if not os.path.exists(EASYEFFECTS_PRESETS_PATH):
        print(f"EasyEffects presets directory not found: {EASYEFFECTS_PRESETS_PATH}")
        return []
        
    try:
        # List all .json files in the presets directory
        presets = [f.replace('.json', '') for f in os.listdir(EASYEFFECTS_PRESETS_PATH) 
                  if f.endswith('.json')]
        return presets
    except Exception as e:
        print(f"Error listing EasyEffects presets: {e}")
        return []

def apply_eq_preset(preset_name):
    """
    Apply an EasyEffects preset by name.
    Uses DBus to communicate with EasyEffects.
    """
    # Validate preset exists
    available_presets = get_available_presets()
    if preset_name not in available_presets:
        print(f"Preset '{preset_name}' not found. Available presets: {available_presets}")
        return False
    
    try:
        # Using dbus-send to communicate with EasyEffects
        cmd = [
            "dbus-send", "--session", "--print-reply", "--dest=com.github.wwmm.easyeffects",
            "/com/github/wwmm/easyeffects", "com.github.wwmm.easyeffects.LoadPreset",
            "string:output", f"string:{preset_name}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully applied EasyEffects preset: {preset_name}")
            return True
        else:
            print(f"Failed to apply preset. Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error applying preset '{preset_name}': {e}")
        return False
