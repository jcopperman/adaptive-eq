#!/usr/bin/env python3
"""
debug_easyeffects.py - Diagnostic tool for EasyEffects integration

This script tests the connection between Adaptive EQ and EasyEffects by:
1. Checking if EasyEffects is running
2. Testing preset application with visual feedback
3. Monitoring EasyEffects UI state changes
4. Verifying audio processing is actually changing
"""

import os
import sys
import time
import json
import subprocess
import signal
import argparse
from services.logger import setup_logger
from services.eq_control import apply_eq_preset, get_available_presets

# Set up logger
logger = setup_logger("debug_easyeffects", log_level="debug")

def check_easyeffects_running():
    """Check if EasyEffects is currently running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "easyeffects"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            pid = result.stdout.strip()
            logger.info(f"✅ EasyEffects is running (PID: {pid})")
            return True
        else:
            logger.error("❌ EasyEffects is not running!")
            logger.info("Please start EasyEffects and try again")
            return False
    except Exception as e:
        logger.error(f"Error checking if EasyEffects is running: {e}")
        return False

def check_gsettings_schema():
    """Check if the EasyEffects gsettings schema is available"""
    try:
        result = subprocess.run(
            ["gsettings", "list-recursively", "com.github.wwmm.easyeffects"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ EasyEffects gsettings schema is available")
            
            # Check for the last-used-output-preset key specifically
            if "last-used-output-preset" in result.stdout:
                preset = subprocess.run(
                    ["gsettings", "get", "com.github.wwmm.easyeffects", "last-used-output-preset"],
                    capture_output=True,
                    text=True
                ).stdout.strip().strip("'")
                
                logger.info(f"✅ Current preset according to gsettings: {preset}")
                return True
            else:
                logger.warning("⚠️ 'last-used-output-preset' key not found in gsettings schema")
                return False
        else:
            logger.error("❌ EasyEffects gsettings schema is not available!")
            logger.info("This could indicate EasyEffects is not properly installed")
            return False
    except Exception as e:
        logger.error(f"Error checking gsettings schema: {e}")
        return False

def check_dbus_interface():
    """Check if EasyEffects is accessible via DBus"""
    try:
        result = subprocess.run(
            ["dbus-send", "--session", "--print-reply", "--dest=com.github.wwmm.easyeffects", 
             "/com/github/wwmm/easyeffects", "org.freedesktop.DBus.Introspectable.Introspect"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ EasyEffects DBus interface is accessible")
            return True
        else:
            logger.error("❌ EasyEffects DBus interface is not accessible!")
            logger.error(f"Error: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error checking DBus interface: {e}")
        return False

def check_preset_files():
    """Check EasyEffects preset files"""
    user_presets_path = os.path.expanduser("~/.config/easyeffects/output/")
    system_presets_path = "/usr/share/easyeffects/output"
    
    if os.path.exists(user_presets_path):
        presets = [f for f in os.listdir(user_presets_path) if f.endswith('.json')]
        logger.info(f"✅ Found {len(presets)} user presets in {user_presets_path}")
        logger.debug(f"User presets: {', '.join(presets)}")
    else:
        logger.warning(f"⚠️ User presets directory not found: {user_presets_path}")
    
    if os.path.exists(system_presets_path):
        presets = [f for f in os.listdir(system_presets_path) if f.endswith('.json')]
        logger.info(f"✅ Found {len(presets)} system presets in {system_presets_path}")
        logger.debug(f"System presets: {', '.join(presets)}")
    else:
        logger.warning(f"⚠️ System presets directory not found: {system_presets_path}")
    
    # Check for current_preset.json file
    current_preset_path = os.path.expanduser("~/.config/easyeffects/current_preset.json")
    if os.path.exists(current_preset_path):
        logger.info(f"✅ Found current_preset.json at {current_preset_path}")
        try:
            with open(current_preset_path, 'r') as f:
                data = json.load(f)
                logger.debug(f"Current preset file content: {json.dumps(data, indent=2)[:200]}...")
        except Exception as e:
            logger.error(f"Error reading current preset file: {e}")
    else:
        logger.warning(f"⚠️ Current preset file not found: {current_preset_path}")

def test_preset_application(preset_name=None, delay=5):
    """Test applying EQ presets with visual feedback"""
    presets = get_available_presets()
    
    if not presets:
        logger.error("❌ No EasyEffects presets found!")
        return False
    
    logger.info(f"Found {len(presets)} presets: {', '.join(presets)}")
    
    if preset_name and preset_name not in presets:
        logger.error(f"❌ Specified preset '{preset_name}' not found!")
        return False
    
    test_presets = [preset_name] if preset_name else presets[:3]  # Test first 3 presets if none specified
    
    logger.info(f"Will test presets: {', '.join(test_presets)}")
    logger.info(f"For each preset: Wait {delay} seconds and check if EasyEffects UI updates")
    logger.info("Look at the EasyEffects UI while this test runs to see if the preset changes visually")
    
    for preset in test_presets:
        logger.info(f"\n🔄 Applying preset: {preset}")
        
        # Method 1: Try gsettings
        logger.info("Method 1: Using gsettings...")
        subprocess.run(
            ["gsettings", "set", "com.github.wwmm.easyeffects", "last-used-output-preset", preset],
            capture_output=True,
            text=True
        )
        
        # Check if the preset was applied via gsettings
        current = subprocess.run(
            ["gsettings", "get", "com.github.wwmm.easyeffects", "last-used-output-preset"],
            capture_output=True,
            text=True
        ).stdout.strip().strip("'")
        
        if current == preset:
            logger.info(f"✅ gsettings successfully set to '{preset}'")
        else:
            logger.warning(f"⚠️ gsettings shows '{current}' instead of '{preset}'")
        
        logger.info(f"Waiting {delay} seconds to check UI update...")
        for i in range(delay, 0, -1):
            sys.stdout.write(f"\rTime remaining: {i}s ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r                 \r")
        
        # Ask for user feedback
        ui_updated = input(f"Did the EasyEffects UI update to show '{preset}' preset? (y/n): ")
        if ui_updated.lower() == 'y':
            logger.info("✅ UI successfully updated")
        else:
            logger.warning("⚠️ UI did not update visually")
            
            # Try Method 2: DBus
            logger.info("\nMethod 2: Trying via DBus...")
            try:
                dbus_cmd = [
                    "dbus-send", "--session", "--type=method_call",
                    "--dest=com.github.wwmm.easyeffects",
                    "/com/github/wwmm/easyeffects",
                    "com.github.wwmm.easyeffects.load_preset", 
                    f"string:{preset}"
                ]
                dbus_result = subprocess.run(dbus_cmd, capture_output=True, text=True)
                
                if dbus_result.returncode == 0:
                    logger.info(f"✅ DBus command executed successfully")
                else:
                    logger.warning(f"⚠️ DBus command failed: {dbus_result.stderr}")
            except Exception as e:
                logger.error(f"Error with DBus method: {e}")
            
            # Wait again
            logger.info(f"Waiting {delay} seconds to check UI update...")
            for i in range(delay, 0, -1):
                sys.stdout.write(f"\rTime remaining: {i}s ")
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write("\r                 \r")
            
            # Ask for user feedback
            ui_updated = input(f"Did the EasyEffects UI update after DBus method? (y/n): ")
            if ui_updated.lower() == 'y':
                logger.info("✅ UI successfully updated with DBus method")
            else:
                logger.warning("⚠️ UI did not update with DBus method")
                
                # Try Method 3: File copy
                logger.info("\nMethod 3: Trying file copy method...")
                try:
                    # Find the preset file
                    user_preset_path = os.path.expanduser(f"~/.config/easyeffects/output/{preset}.json")
                    system_preset_path = f"/usr/share/easyeffects/output/{preset}.json"
                    
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
                        
                        logger.info(f"✅ Copied preset file from {src_preset_path} to {current_preset_path}")
                        
                        # Send a refresh signal to EasyEffects
                        refresh_cmd = ["pkill", "-HUP", "easyeffects"]
                        subprocess.run(refresh_cmd, capture_output=True, text=True)
                        logger.info("✅ Sent refresh signal to EasyEffects")
                        
                        # Also try to trigger a reload via dconf
                        reload_cmd = ["dconf", "write", "/com/github/wwmm/easyeffects/reload-presets", "true"]
                        subprocess.run(reload_cmd, capture_output=True, text=True)
                        logger.info("✅ Sent reload-presets signal via dconf")
                    else:
                        logger.error(f"❌ Preset file not found for {preset}")
                except Exception as e:
                    logger.error(f"Error with file copy method: {e}")
                
                # Wait again
                logger.info(f"Waiting {delay} seconds to check UI update...")
                for i in range(delay, 0, -1):
                    sys.stdout.write(f"\rTime remaining: {i}s ")
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write("\r                 \r")
                
                # Ask for user feedback
                ui_updated = input(f"Did the EasyEffects UI update after file copy method? (y/n): ")
                if ui_updated.lower() == 'y':
                    logger.info("✅ UI successfully updated with file copy method")
                else:
                    logger.error("❌ All methods failed to update EasyEffects UI")
        
        # Ask if the sound actually changed
        sound_changed = input("Did the sound/EQ settings change even if the UI didn't update? (y/n): ")
        if sound_changed.lower() == 'y':
            logger.info("✅ Sound/EQ settings changed successfully")
        else:
            logger.error("❌ Sound/EQ settings did not change")
    
    return True

def check_config_directory():
    """Check for EasyEffects config directory structure"""
    config_dir = os.path.expanduser("~/.config/easyeffects")
    if not os.path.exists(config_dir):
        logger.warning(f"⚠️ EasyEffects config directory not found: {config_dir}")
        logger.info("Creating config directory...")
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(os.path.join(config_dir, "output"), exist_ok=True)
        return False
    
    config_file = os.path.join(config_dir, "config.json")
    if not os.path.exists(config_file):
        logger.warning(f"⚠️ EasyEffects config.json not found: {config_file}")
        return False
    
    logger.info(f"✅ EasyEffects config directory exists: {config_dir}")
    return True

def ensure_config_file():
    """Create a minimal EasyEffects config.json if it doesn't exist"""
    config_file = os.path.expanduser("~/.config/easyeffects/config.json")
    if os.path.exists(config_file):
        logger.info(f"✅ EasyEffects config.json exists: {config_file}")
        return
    
    logger.warning(f"⚠️ EasyEffects config.json not found, creating minimal version")
    
    # Create a minimal config
    minimal_config = {
        "spectrum": {
            "show": "true"
        },
        "last-used-input-preset": "default",
        "last-used-output-preset": "default",
        "use-dark-theme": "true"
    }
    
    try:
        with open(config_file, 'w') as f:
            json.dump(minimal_config, f, indent=2)
        logger.info(f"✅ Created minimal config.json at {config_file}")
    except Exception as e:
        logger.error(f"❌ Failed to create config.json: {e}")

def main():
    parser = argparse.ArgumentParser(description="Debug EasyEffects integration")
    parser.add_argument("--preset", help="Test a specific preset")
    parser.add_argument("--delay", type=int, default=5, help="Delay in seconds between tests")
    parser.add_argument("--check-only", action="store_true", help="Only run checks, don't test preset application")
    
    args = parser.parse_args()
    
    logger.info("=== EasyEffects Integration Diagnostic Tool ===")
    
    # Run checks
    ee_running = check_easyeffects_running()
    if not ee_running:
        logger.info("Starting EasyEffects...")
        subprocess.Popen(["easyeffects"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)  # Wait for it to start
        ee_running = check_easyeffects_running()
    
    if not ee_running:
        logger.error("❌ Cannot continue without EasyEffects running")
        return 1
    
    check_config_directory()
    ensure_config_file()
    check_gsettings_schema()
    check_dbus_interface()
    check_preset_files()
    
    if args.check_only:
        logger.info("Checks completed. Use --preset to test applying a specific preset.")
        return 0
    
    # Test preset application
    test_preset_application(args.preset, args.delay)
    
    logger.info("\n=== Diagnostic Summary ===")
    logger.info("If presets change the sound but don't update the UI, you may need to:")
    logger.info("1. Ensure you have the latest version of EasyEffects")
    logger.info("2. Reset EasyEffects configuration (rename ~/.config/easyeffects)")
    logger.info("3. Check for incompatibilities with your desktop environment")
    logger.info("4. Try restarting the EasyEffects service after preset changes")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
