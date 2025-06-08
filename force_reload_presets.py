#!/usr/bin/env python3
"""
force_reload_presets.py - Force EasyEffects to reload its presets

This script enhances eq_control.py by implementing a more aggressive approach
to ensure EasyEffects reloads presets when they change.
"""

import os
import sys
import json
import time
import subprocess
from services.logger import get_logger, log_exceptions

# Set up logger
logger = get_logger(__name__)

@log_exceptions
def force_reload_easyeffects(preset_name):
    """
    Force EasyEffects to reload its presets and apply the specified preset.
    Uses multiple methods to ensure the preset is applied and the UI is updated.
    """
    logger.info(f"Forcing reload of EasyEffects with preset: {preset_name}")
    
    # Method 1: Use gsettings
    try:
        logger.debug("Setting preset via gsettings...")
        cmd = ["gsettings", "set", "com.github.wwmm.easyeffects", 
               "last-used-output-preset", preset_name]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.debug("gsettings command successful")
        else:
            logger.warning(f"gsettings command failed: {result.stderr}")
    except Exception as e:
        logger.error(f"Error with gsettings method: {e}")
    
    # Method 2: Reset and restart EasyEffects
    try:
        # First check if EasyEffects is running
        ee_running = subprocess.run(["pgrep", "-f", "easyeffects"], 
                                    capture_output=True, text=True).returncode == 0
        
        if ee_running:
            logger.debug("EasyEffects is running, will restart it")
            
            # Create or update config.json if needed
            config_dir = os.path.expanduser("~/.config/easyeffects")
            config_file = os.path.join(config_dir, "config.json")
            
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                os.makedirs(os.path.join(config_dir, "output"), exist_ok=True)
            
            # Update or create config file with the preset
            config_data = {}
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                except Exception:
                    # If file exists but is invalid, create a new one
                    config_data = {}
            
            # Update the preset
            config_data["last-used-output-preset"] = preset_name
            
            # Write the config file
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.debug(f"Updated config.json with preset: {preset_name}")
            
            # Stop EasyEffects
            subprocess.run(["killall", "easyeffects"], 
                          capture_output=True, text=True)
            
            # Wait a moment
            time.sleep(1)
            
            # Start EasyEffects in the background
            subprocess.Popen(["easyeffects", "--gapplication-service"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            
            logger.info("Restarted EasyEffects service")
        else:
            logger.debug("EasyEffects is not running, starting it")
            
            # Start EasyEffects in the background with the preset
            subprocess.Popen(["easyeffects", "--gapplication-service"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            
            logger.info("Started EasyEffects service")
            
            # Wait a moment
            time.sleep(1)
            
            # Apply the preset
            cmd = ["gsettings", "set", "com.github.wwmm.easyeffects", 
                  "last-used-output-preset", preset_name]
            subprocess.run(cmd, capture_output=True, text=True)
    except Exception as e:
        logger.error(f"Error restarting EasyEffects: {e}")
    
    # Method 3: Copy the preset file
    try:
        # Find the preset file
        user_preset_path = os.path.expanduser(f"~/.config/easyeffects/output/{preset_name}.json")
        system_preset_path = f"/usr/share/easyeffects/output/{preset_name}.json"
        
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
            
            logger.debug(f"Copied preset from {src_preset_path} to current_preset.json")
            
            # Send a refresh signal
            subprocess.run(["pkill", "-HUP", "easyeffects"], 
                          capture_output=True, text=True)
            
            # Trigger a reload via dconf
            subprocess.run(["dconf", "write", "/com/github/wwmm/easyeffects/reload-presets", "true"],
                          capture_output=True, text=True)
            
            logger.debug("Sent signals to reload presets")
        else:
            logger.warning(f"Preset file not found for {preset_name}")
    except Exception as e:
        logger.error(f"Error with file copy method: {e}")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python force_reload_presets.py <preset_name>")
        return 1
    
    preset_name = sys.argv[1]
    success = force_reload_easyeffects(preset_name)
    
    if success:
        print(f"Successfully forced reload with preset: {preset_name}")
        return 0
    else:
        print(f"Failed to force reload with preset: {preset_name}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
