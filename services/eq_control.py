import subprocess
import os
import json

# Path where EasyEffects stores its presets
EASYEFFECTS_PRESETS_PATH = os.path.expanduser("~/.config/easyeffects/output/")

def get_available_presets():
    """
    Get a list of available EasyEffects presets.
    """
    # First check system-wide presets
    system_presets_path = "/usr/share/easyeffects/output"
    
    # Start with user presets
    if not os.path.exists(EASYEFFECTS_PRESETS_PATH):
        print(f"User EasyEffects presets directory not found: {EASYEFFECTS_PRESETS_PATH}")
        
        # If user presets don't exist, try system presets
        if os.path.exists(system_presets_path):
            try:
                presets = [f.replace('.json', '') for f in os.listdir(system_presets_path) 
                          if f.endswith('.json')]
                print(f"Found {len(presets)} system presets in {system_presets_path}")
                return presets
            except Exception as e:
                print(f"Error listing system EasyEffects presets: {e}")
                return []
        else:
            print(f"System EasyEffects presets directory not found: {system_presets_path}")
            # Try a fallback approach - check if any presets exist in common locations
            fallback_paths = [
                os.path.expanduser("~/.config/PulseEffects/output/"),  # Old PulseEffects location
                "/usr/share/pulseeffects/presets/output/",  # Old system location
            ]
            
            for path in fallback_paths:
                if os.path.exists(path):
                    try:
                        presets = [f.replace('.json', '') for f in os.listdir(path) 
                                  if f.endswith('.json')]
                        if presets:
                            print(f"Found {len(presets)} presets in fallback location: {path}")
                            return presets
                    except Exception as e:
                        print(f"Error listing fallback presets at {path}: {e}")
            
            return []
        
    try:
        # List all .json files in the user presets directory
        presets = [f.replace('.json', '') for f in os.listdir(EASYEFFECTS_PRESETS_PATH) 
                  if f.endswith('.json')]
        
        # Also check system presets and merge (avoiding duplicates)
        if os.path.exists(system_presets_path):
            system_presets = [f.replace('.json', '') for f in os.listdir(system_presets_path) 
                             if f.endswith('.json')]
            # Add system presets that aren't already in user presets
            for preset in system_presets:
                if preset not in presets:
                    presets.append(preset)
        
        return presets
    except Exception as e:
        print(f"Error listing EasyEffects presets: {e}")
        return []

def apply_eq_preset(preset_name):
    """
    Apply an EasyEffects preset by name.
    Uses the gsettings command to apply the preset, which is more reliable
    than DBus for newer versions of EasyEffects.
    """
    # Validate preset exists
    available_presets = get_available_presets()
    if preset_name not in available_presets:
        print(f"Preset '{preset_name}' not found. Available presets: {available_presets}")
        return False
    
    try:
        # Method 1: Use gsettings to apply the preset (preferred method)
        cmd = [
            "gsettings", "set", "com.github.wwmm.easyeffects", "last-used-output-preset", 
            preset_name
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully applied EasyEffects preset: {preset_name}")
            return True
        else:
            print(f"gsettings method failed: {result.stderr}. Trying alternative methods.")
            
            # Method 2: Try using dbus-send as an alternative approach
            try:
                dbus_cmd = [
                    "dbus-send", "--session", "--type=method_call",
                    "--dest=com.github.wwmm.easyeffects",
                    "/com/github/wwmm/easyeffects",
                    "com.github.wwmm.easyeffects.load_preset", 
                    "string:" + preset_name
                ]
                dbus_result = subprocess.run(dbus_cmd, capture_output=True, text=True)
                
                if dbus_result.returncode == 0:
                    print(f"Applied preset {preset_name} using dbus-send")
                    return True
                else:
                    print(f"dbus-send method failed: {dbus_result.stderr}")
            except Exception as e:
                print(f"Error with dbus-send method: {e}")
            
            # Method 3: Try by copying the preset file to the current preset location
            try:
                # Find the preset file path
                user_preset_path = os.path.join(EASYEFFECTS_PRESETS_PATH, f"{preset_name}.json")
                system_preset_path = os.path.join("/usr/share/easyeffects/output", f"{preset_name}.json")
                
                src_preset_path = None
                if os.path.exists(user_preset_path):
                    src_preset_path = user_preset_path
                elif os.path.exists(system_preset_path):
                    src_preset_path = system_preset_path
                
                if src_preset_path:
                    current_preset_path = os.path.expanduser("~/.config/easyeffects/current_preset.json")
                    
                    # Make sure the output directory exists
                    os.makedirs(os.path.dirname(current_preset_path), exist_ok=True)
                    
                    # Copy the preset file content
                    with open(src_preset_path, 'r') as src_file:
                        preset_data = json.load(src_file)
                    
                    with open(current_preset_path, 'w') as dest_file:
                        json.dump(preset_data, dest_file, indent=2)
                    
                    print(f"Applied preset {preset_name} by copying the preset file")
                    
                    # Send a refresh signal to EasyEffects
                    refresh_cmd = ["pkill", "-HUP", "easyeffects"]
                    subprocess.run(refresh_cmd, capture_output=True, text=True)
                    
                    # Also try to trigger a reload via dconf
                    reload_cmd = ["dconf", "write", "/com/github/wwmm/easyeffects/reload-presets", "true"]
                    subprocess.run(reload_cmd, capture_output=True, text=True)
                    
                    return True
                else:
                    print(f"Failed to apply preset. Preset file not found for {preset_name}")
                    return False
            except Exception as e:
                print(f"Error applying preset by file copy: {e}")
                return False
    except Exception as e:
        print(f"Error applying preset '{preset_name}': {e}")
        return False
