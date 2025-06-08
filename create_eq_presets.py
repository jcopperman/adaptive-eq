#!/usr/bin/env python3
"""
create_eq_presets.py - Automatically create EQ presets for EasyEffects

This script generates predefined EQ presets for different music genres
and saves them to the EasyEffects preset directory.
"""

import os
import json
import argparse

# Path where EasyEffects stores its presets
EASYEFFECTS_PRESETS_PATH = os.path.expanduser("~/.config/easyeffects/output/")

# Define EQ presets for different genres
# Format: {genre_name: [(frequency, gain), ...]}
GENRE_PRESETS = {
    "hiphop": [
        (32, 3.0), (64, 4.0), (125, 3.0), (250, 1.0), (500, -1.0),
        (1000, 0.0), (2000, 2.0), (4000, 3.0), (8000, 1.0), (16000, 1.0)
    ],
    "rock": [
        (32, 2.0), (64, 2.0), (125, 1.0), (250, 0.0), (500, -1.0),
        (1000, 0.0), (2000, 1.0), (4000, 2.0), (8000, 2.0), (16000, 0.0)
    ],
    "electronic": [
        (32, 3.0), (64, 3.0), (125, 2.0), (250, 0.0), (500, -1.0),
        (1000, -1.0), (2000, 1.0), (4000, 2.0), (8000, 3.0), (16000, 2.0)
    ],
    "pop": [
        (32, 2.0), (64, 1.0), (125, 0.0), (250, -1.0), (500, -1.0),
        (1000, 0.0), (2000, 1.0), (4000, 2.0), (8000, 2.0), (16000, 1.0)
    ],
    "jazz": [
        (32, 1.0), (64, 1.0), (125, 0.0), (250, 0.0), (500, 1.0),
        (1000, 1.0), (2000, 0.0), (4000, 0.0), (8000, -1.0), (16000, -2.0)
    ],
    "classical": [
        (32, 1.0), (64, 1.0), (125, 0.0), (250, 0.0), (500, 0.0),
        (1000, 0.0), (2000, 0.0), (4000, 1.0), (8000, 1.0), (16000, 1.0)
    ],
    "alternative": [
        (32, 1.0), (64, 1.0), (125, 0.0), (250, -1.0), (500, 1.0),
        (1000, 2.0), (2000, 1.0), (4000, 2.0), (8000, 2.0), (16000, 1.0)
    ],
    "metal": [
        (32, 2.0), (64, 2.0), (125, 1.0), (250, -2.0), (500, -3.0),
        (1000, -1.0), (2000, 2.0), (4000, 3.0), (8000, 3.0), (16000, 1.0)
    ],
    "ambient": [
        (32, 3.0), (64, 2.0), (125, 1.0), (250, 0.0), (500, -1.0),
        (1000, -2.0), (2000, 0.0), (4000, 1.0), (8000, 2.0), (16000, 3.0)
    ],
    "vocal": [
        (32, -1.0), (64, -2.0), (125, -1.0), (250, 0.0), (500, 2.0),
        (1000, 3.0), (2000, 3.0), (4000, 2.0), (8000, 0.0), (16000, -1.0)
    ],
    "reggae": [
        (32, 2.0), (64, 3.0), (125, 1.0), (250, 0.0), (500, 0.0),
        (1000, -1.0), (2000, 0.0), (4000, 0.0), (8000, 0.0), (16000, -1.0)
    ],
    "orchestral": [
        (32, 2.0), (64, 1.0), (125, 0.0), (250, 0.0), (500, 0.0),
        (1000, 0.0), (2000, -1.0), (4000, 1.0), (8000, 2.0), (16000, 1.0)
    ],
    "default": [
        (32, 0.0), (64, 0.0), (125, 0.0), (250, 0.0), (500, 0.0),
        (1000, 0.0), (2000, 0.0), (4000, 0.0), (8000, 0.0), (16000, 0.0)
    ],
}

def get_base_preset_template():
    """Returns a base preset template for EasyEffects."""
    # This is a simplified version of EasyEffects output preset template
    return {
        "output": {
            "blocklist": [],
            "equalizer": {
                "input-gain": 0.0,
                "output-gain": 0.0,
                "mode": "IIR",
                "num-bands": 10,
                "split-channels": False,
                "right": {
                    "band0": {"frequency": 32, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band1": {"frequency": 64, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band2": {"frequency": 125, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band3": {"frequency": 250, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band4": {"frequency": 500, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band5": {"frequency": 1000, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band6": {"frequency": 2000, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band7": {"frequency": 4000, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band8": {"frequency": 8000, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band9": {"frequency": 16000, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                },
                "left": {
                    "band0": {"frequency": 32, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band1": {"frequency": 64, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band2": {"frequency": 125, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band3": {"frequency": 250, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band4": {"frequency": 500, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band5": {"frequency": 1000, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band6": {"frequency": 2000, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band7": {"frequency": 4000, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band8": {"frequency": 8000, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                    "band9": {"frequency": 16000, "gain": 0.0, "mode": "RLC (BT)", "q": 1.504, "slope": "x1", "solo": False, "type": "Bell"},
                }
            },
            "plugins_order": ["equalizer"],
            "limiter": {
                "alr": False,
                "alr-attack": 5.0,
                "alr-knee": 0.0,
                "alr-release": 50.0,
                "attack": 5.0,
                "dithering": "None",
                "external-sidechain": False,
                "gain-boost": True,
                "input-gain": 0.0,
                "lookahead": 5.0,
                "mode": "Herm Thin",
                "output-gain": 0.0,
                "oversampling": "None",
                "release": 5.0,
                "sidechain-preamp": 0.0,
                "stereo-link": 100.0,
                "threshold": 0.0
            }
        }
    }

def create_eq_preset(genre_name, eq_settings, output_dir):
    """Create an EQ preset for a specific genre."""
    preset = get_base_preset_template()
    
    # Apply EQ settings to both left and right channels
    for i, (freq, gain) in enumerate(eq_settings):
        band_key = f"band{i}"
        preset["output"]["equalizer"]["left"][band_key]["gain"] = gain
        preset["output"]["equalizer"]["right"][band_key]["gain"] = gain
    
    # Save the preset to a file
    preset_path = os.path.join(output_dir, f"{genre_name}.json")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(preset_path, "w") as f:
        json.dump(preset, f, indent=4)
    
    return preset_path

def main():
    parser = argparse.ArgumentParser(description="Create EQ presets for EasyEffects")
    parser.add_argument("--genres", nargs="+", help="Specific genres to create presets for", 
                        choices=list(GENRE_PRESETS.keys()))
    parser.add_argument("--all", action="store_true", help="Create presets for all genres")
    parser.add_argument("--output-dir", default=EASYEFFECTS_PRESETS_PATH, 
                        help=f"Output directory (default: {EASYEFFECTS_PRESETS_PATH})")
    
    args = parser.parse_args()
    
    if not args.genres and not args.all:
        parser.print_help()
        print("\nAvailable genres:")
        for genre in sorted(GENRE_PRESETS.keys()):
            print(f"  - {genre}")
        return
    
    # Determine which genres to create presets for
    genres_to_create = list(GENRE_PRESETS.keys()) if args.all else args.genres
    
    created_presets = []
    for genre in genres_to_create:
        if genre in GENRE_PRESETS:
            preset_path = create_eq_preset(genre, GENRE_PRESETS[genre], args.output_dir)
            created_presets.append((genre, preset_path))
            print(f"Created preset for '{genre}' at: {preset_path}")
    
    if created_presets:
        print(f"\nSuccessfully created {len(created_presets)} preset(s).")
        print("You can now use these presets in the Adaptive EQ application.")
    else:
        print("No presets were created.")

if __name__ == "__main__":
    main()
