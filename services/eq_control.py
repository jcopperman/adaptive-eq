import subprocess
import os
import json
import time
from services.logger import get_logger, log_exceptions

# Set up logger
logger = get_logger(__name__)

# Path where EasyEffects stores its presets
EASYEFFECTS_PRESETS_PATH = os.path.expanduser("~/.config/easyeffects/output/")

# Track preset changes for UI refresh logic
_last_preset_change = 0
_last_applied_preset = None
_forced_ui_refresh_interval = 30  # seconds between forced UI refreshes

@log_exceptions
def get_available_presets():
    """
    Get a list of available EasyEffects presets.
    """
    # First check system-wide presets
    system_presets_path = "/usr/share/easyeffects/output"
    
    # Start with user presets
    if not os.path.exists(EASYEFFECTS_PRESETS_PATH):
        logger.warning(f"User EasyEffects presets directory not found: {EASYEFFECTS_PRESETS_PATH}")
        
        # If user presets don't exist, try system presets
        if os.path.exists(system_presets_path):
            try:
                presets = [f.replace('.json', '') for f in os.listdir(system_presets_path) 
                          if f.endswith('.json')]
                logger.info(f"Found {len(presets)} system presets in {system_presets_path}")
                return presets
            except Exception as e:
                logger.error(f"Error listing system EasyEffects presets: {e}")
                return []
        else:
            logger.warning(f"System EasyEffects presets directory not found: {system_presets_path}")
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
                            logger.info(f"Found {len(presets)} presets in fallback location: {path}")
                            return presets
                    except Exception as e:
                        logger.error(f"Error listing fallback presets at {path}: {e}")
            
            logger.error("No EasyEffects or PulseEffects presets found in any location")
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
        
        logger.info(f"Found {len(presets)} EasyEffects presets")
        logger.debug(f"Available presets: {', '.join(presets)}")
        return presets
    except Exception as e:
        logger.error(f"Error listing EasyEffects presets: {e}")
        return []

@log_exceptions
def apply_eq_preset(preset_name, force_ui_refresh=False):
    """
    Apply an EasyEffects preset by name.
    Uses multiple methods to ensure the preset is applied and the UI is updated.
    
    Args:
        preset_name: Name of the preset to apply
        force_ui_refresh: If True, will use more aggressive methods to ensure the UI updates
    """
    global _last_preset_change, _last_applied_preset, _forced_ui_refresh_interval
    
    # Validate preset exists
    available_presets = get_available_presets()
    if preset_name not in available_presets:
        logger.error(f"Preset '{preset_name}' not found. Available presets: {available_presets}")
        return False
    
    # Check if we need to force a UI refresh
    current_time = time.time()
    force_refresh = force_ui_refresh
    
    # Force UI refresh if it's been a while since the last one or if this is a new preset
    if not force_refresh:
        if (current_time - _last_preset_change > _forced_ui_refresh_interval or 
            preset_name != _last_applied_preset):
            logger.debug("Auto-enabling forced UI refresh due to timing or preset change")
            force_refresh = True
    
    logger.info(f"Applying EasyEffects preset: {preset_name} (force_refresh: {force_refresh})")
    
    # Update tracking variables
    _last_preset_change = current_time
    _last_applied_preset = preset_name
    
    try:
        # Method 1: Use gsettings to apply the preset (preferred method)
        logger.debug("Trying gsettings method")
        cmd = [
            "gsettings", "set", "com.github.wwmm.easyeffects", "last-used-output-preset", 
            preset_name
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        success = result.returncode == 0
        
        if success:
            logger.info(f"Successfully applied EasyEffects preset: {preset_name} using gsettings")
            
            # If UI refresh not forced, we're done
            if not force_refresh:
                return True
        else:
            logger.warning(f"gsettings method failed: {result.stderr}. Trying alternative methods.")
            
        # Method 2: Try using dbus-send as an alternative approach
        try:
            logger.debug("Trying dbus-send method")
            dbus_cmd = [
                "dbus-send", "--session", "--type=method_call",
                "--dest=com.github.wwmm.easyeffects",
                "/com/github/wwmm/easyeffects",
                "com.github.wwmm.easyeffects.load_preset", 
                "string:" + preset_name
            ]
            dbus_result = subprocess.run(dbus_cmd, capture_output=True, text=True)
            
            if dbus_result.returncode == 0:
                logger.info(f"Applied preset {preset_name} using dbus-send")
                success = True
                
                # If UI refresh not forced, we're done
                if not force_refresh:
                    return True
            else:
                logger.warning(f"dbus-send method failed: {dbus_result.stderr}")
        except Exception as e:
            logger.error(f"Error with dbus-send method: {e}")
        
        # Method 3: Try by copying the preset file to the current preset location
        try:
            logger.debug("Trying file copy method")
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
                
                logger.info(f"Applied preset {preset_name} by copying the preset file")
                
                # Send a refresh signal to EasyEffects
                refresh_cmd = ["pkill", "-HUP", "easyeffects"]
                subprocess.run(refresh_cmd, capture_output=True, text=True)
                
                # Also try to trigger a reload via dconf
                reload_cmd = ["dconf", "write", "/com/github/wwmm/easyeffects/reload-presets", "true"]
                subprocess.run(reload_cmd, capture_output=True, text=True)
                
                success = True
                
                # If UI refresh not forced, we're done
                if not force_refresh:
                    return True
            else:
                logger.error(f"Failed to apply preset. Preset file not found for {preset_name}")
        except Exception as e:
            logger.error(f"Error applying preset by file copy: {e}")
        
        # Method 4 (Aggressive): If force_refresh is enabled or previous methods failed,
        # try a more aggressive approach - ensure config.json exists with the right preset
        if force_refresh or not success:
            try:
                logger.debug("Using aggressive method to ensure UI refresh")
                
                # Create or update config.json
                config_dir = os.path.expanduser("~/.config/easyeffects")
                config_file = os.path.join(config_dir, "config.json")
                
                # Create minimal config data if needed
                config_data = {
                    "spectrum": {"show": "true"},
                    "last-used-input-preset": "default",
                    "last-used-output-preset": preset_name,
                    "use-dark-theme": "true"
                }
                
                # If config exists, update only the necessary part
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            existing_config = json.load(f)
                        
                        # Update only the preset setting
                        existing_config["last-used-output-preset"] = preset_name
                        config_data = existing_config
                    except Exception as e:
                        logger.warning(f"Error reading existing config.json: {e}, will create new one")
                
                # Write the config file
                with open(config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                logger.debug(f"Updated config.json with preset: {preset_name}")
                
                # Check if EasyEffects is running
                ee_running = subprocess.run(
                    ["pgrep", "-f", "easyeffects"], 
                    capture_output=True, text=True
                ).returncode == 0
                
                if ee_running:
                    # Try sending a SIGHUP signal for config reload
                    subprocess.run(
                        ["pkill", "-HUP", "easyeffects"], 
                        capture_output=True, text=True
                    )
                    
                    logger.debug("Sent SIGHUP to EasyEffects for config reload")
                else:
                    # Start EasyEffects if it's not running
                    logger.debug("EasyEffects not running, starting it")
                    subprocess.Popen(
                        ["easyeffects", "--gapplication-service"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL
                    )
                
                # Set via gsettings again after config update
                subprocess.run(
                    ["gsettings", "set", "com.github.wwmm.easyeffects", 
                     "last-used-output-preset", preset_name],
                    capture_output=True, text=True
                )
                
                # One more attempt via dconf
                subprocess.run(
                    ["dconf", "write", "/com/github/wwmm/easyeffects/reload-presets", "true"],
                    capture_output=True, text=True
                )
                
                return True
            except Exception as e:
                logger.error(f"Error with aggressive UI refresh method: {e}")
        
        return success
    except Exception as e:
        logger.error(f"Error applying preset '{preset_name}': {e}")
        return False

@log_exceptions
def force_ui_refresh():
    """
    Force EasyEffects UI to refresh by restarting the service component.
    This is a more aggressive approach when normal methods fail.
    """
    logger.info("Forcing EasyEffects UI refresh")
    
    try:
        # Check if EasyEffects is running
        ee_running = subprocess.run(
            ["pgrep", "-f", "easyeffects"], 
            capture_output=True, text=True
        ).returncode == 0
        
        if ee_running:
            # First try a gentle HUP signal
            subprocess.run(
                ["pkill", "-HUP", "easyeffects"], 
                capture_output=True, text=True
            )
            logger.debug("Sent SIGHUP to EasyEffects")
            
            # Also try dconf reload
            subprocess.run(
                ["dconf", "write", "/com/github/wwmm/easyeffects/reload-presets", "true"],
                capture_output=True, text=True
            )
            
            # If the UI is open (not just the service), we need a more specific approach
            ui_running = subprocess.run(
                ["pgrep", "-f", "easyeffects$"], 
                capture_output=True, text=True
            ).returncode == 0
            
            if ui_running:
                logger.info("EasyEffects UI is running, sending SIGUSR1")
                # SIGUSR1 might trigger a reload without killing the app
                subprocess.run(
                    ["pkill", "-USR1", "easyeffects$"], 
                    capture_output=True, text=True
                )
            
            return True
        else:
            logger.debug("EasyEffects not running, no refresh needed")
            return False
    except Exception as e:
        logger.error(f"Error forcing UI refresh: {e}")
        return False
