#!/usr/bin/env python3
"""
verify_ui_sync.py - Test if EasyEffects UI is properly synchronized with preset changes

This script applies a sequence of EQ presets and checks if the UI is updating
by asking for user feedback.
"""

import sys
import time
import subprocess
from services.eq_control import get_available_presets, apply_eq_preset, force_ui_refresh
from services.logger import setup_logger

# Set up logger
logger = setup_logger("verify_ui_sync", log_level="info")

def ensure_easyeffects_running():
    """Make sure EasyEffects is running"""
    is_running = subprocess.run(
        ["pgrep", "-f", "easyeffects"], 
        capture_output=True, 
        text=True
    ).returncode == 0
    
    if not is_running:
        logger.info("Starting EasyEffects...")
        subprocess.Popen(
            ["easyeffects"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)  # Wait for it to start

def test_ui_sync():
    """Test if UI sync is working correctly"""
    logger.info("=== EasyEffects UI Sync Verification ===")
    
    # First make sure EasyEffects is running
    ensure_easyeffects_running()
    
    # Get available presets
    presets = get_available_presets()
    if not presets:
        logger.error("No EasyEffects presets found. Please create some presets first.")
        return False
    
    logger.info(f"Found {len(presets)} presets: {', '.join(presets)}")
    
    # Only test a few presets to keep it short
    test_presets = presets[:3] if len(presets) > 3 else presets
    
    logger.info("\nStarting UI sync test:")
    logger.info("1. Each preset will be applied")
    logger.info("2. Watch the EasyEffects UI to see if it updates")
    logger.info("3. You'll be asked to confirm if you saw the update\n")
    
    input("Press Enter to begin the test...")
    
    method_results = {
        "standard": 0,
        "force_ui": 0
    }
    
    # Test standard method first
    logger.info("\n=== Testing Standard Method ===")
    for preset in test_presets:
        logger.info(f"\nApplying preset: {preset} using standard method")
        apply_eq_preset(preset, force_ui_refresh=False)
        time.sleep(3)  # Give UI time to update
        
        response = input(f"Did the EasyEffects UI change to show '{preset}'? (y/n): ")
        if response.lower() == 'y':
            method_results["standard"] += 1
    
    # Test with force_ui_refresh
    logger.info("\n=== Testing Force UI Refresh Method ===")
    for preset in test_presets:
        logger.info(f"\nApplying preset: {preset} with force_ui_refresh=True")
        apply_eq_preset(preset, force_ui_refresh=True)
        time.sleep(3)  # Give UI time to update
        
        response = input(f"Did the EasyEffects UI change to show '{preset}'? (y/n): ")
        if response.lower() == 'y':
            method_results["force_ui"] += 1
    
    # Test with manual force_ui_refresh
    logger.info("\n=== Testing Manual UI Refresh ===")
    preset = test_presets[0]
    logger.info(f"\nApplying preset: {preset} then forcing UI refresh")
    apply_eq_preset(preset, force_ui_refresh=False)
    time.sleep(1)
    logger.info("Forcing UI refresh...")
    force_ui_refresh()
    time.sleep(3)
    
    response = input(f"Did the EasyEffects UI change to show '{preset}' after the force refresh? (y/n): ")
    manual_refresh_works = response.lower() == 'y'
    
    # Show results
    logger.info("\n=== Results ===")
    logger.info(f"Standard method: {method_results['standard']}/{len(test_presets)} presets visible in UI")
    logger.info(f"Force UI method: {method_results['force_ui']}/{len(test_presets)} presets visible in UI")
    logger.info(f"Manual refresh: {'Works' if manual_refresh_works else 'Does not work'}")
    
    if method_results["force_ui"] > method_results["standard"]:
        logger.info("\nRecommendation: Use force_ui_refresh=True for better UI synchronization")
        logger.info("Run the application with: ./run_cli.sh or python3 main.py --force-refresh")
    elif method_results["standard"] == len(test_presets):
        logger.info("\nGood news! Standard preset application works correctly with your EasyEffects version")
    else:
        logger.info("\nUI synchronization issues detected. Please check the troubleshooting guide:")
        logger.info("docs/easyeffects_troubleshooting.md")
    
    return True

if __name__ == "__main__":
    try:
        test_ui_sync()
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
