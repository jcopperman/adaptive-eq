#!/usr/bin/env python3
"""
test_eq_presets.py - Tool to test EasyEffects preset application

This script tests if the EasyEffects preset application is working correctly
by applying different presets in sequence.
"""

import time
import sys
import os

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from services.eq_control import get_available_presets, apply_eq_preset

def test_all_presets(delay=5):
    """Test all available presets with a delay between each."""
    presets = get_available_presets()
    
    if not presets:
        print("No EasyEffects presets found.")
        return False
    
    print(f"Found {len(presets)} presets: {', '.join(presets)}")
    print(f"Will apply each preset with a {delay}-second delay between them.")
    print("Press Ctrl+C to stop the test at any time.")
    print()
    
    try:
        for preset in presets:
            print(f"Applying preset: {preset}")
            success = apply_eq_preset(preset)
            
            if success:
                print(f"✅ Successfully applied {preset} preset")
            else:
                print(f"❌ Failed to apply {preset} preset")
            
            # Wait for specified delay before next preset
            for i in range(delay, 0, -1):
                print(f"Waiting {i} seconds before next preset...", end="\r")
                time.sleep(1)
            print()
            
        print("All presets tested!")
        return True
    
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
        return False
    except Exception as e:
        print(f"\nError during preset test: {e}")
        return False

def test_specific_preset(preset_name):
    """Test a specific preset."""
    presets = get_available_presets()
    
    if not presets:
        print("No EasyEffects presets found.")
        return False
    
    if preset_name not in presets:
        print(f"Preset '{preset_name}' not found.")
        print(f"Available presets: {', '.join(presets)}")
        return False
    
    print(f"Applying preset: {preset_name}")
    success = apply_eq_preset(preset_name)
    
    if success:
        print(f"✅ Successfully applied {preset_name} preset")
        return True
    else:
        print(f"❌ Failed to apply {preset_name} preset")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test EasyEffects preset application")
    parser.add_argument("--preset", help="Test a specific preset")
    parser.add_argument("--all", action="store_true", help="Test all available presets")
    parser.add_argument("--delay", type=int, default=5, help="Delay in seconds between preset changes (default: 5)")
    
    args = parser.parse_args()
    
    if args.preset:
        test_specific_preset(args.preset)
    elif args.all:
        test_all_presets(args.delay)
    else:
        presets = get_available_presets()
        if presets:
            print(f"Available presets: {', '.join(presets)}")
        else:
            print("No EasyEffects presets found.")
        parser.print_help()

if __name__ == "__main__":
    main()
