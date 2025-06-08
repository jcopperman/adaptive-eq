#!/usr/bin/env python3

import time
import os
import json
from services.spotify import get_current_track
from services.eq_control import apply_eq_preset

# Load EQ profile mapping (artist → preset)
def load_profile_map(path="config/eq_profiles.json"):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def main():
    print("Starting Adaptive EQ Daemon...")
    profile_map = load_profile_map()
    print(f"Loaded {len(profile_map)} artist → preset mappings")
    last_artist = None

    while True:
        track = get_current_track()

        if track is None:
            print("No track playing...")
            time.sleep(10)
            continue

        artist = track.get("artist")
        if artist != last_artist:
            print(f"Detected new artist: {artist}")
            preset = profile_map.get(artist, "default")
            print(f"Applying EQ preset: {preset}")
            success = apply_eq_preset(preset)
            if success:
                print(f"Successfully applied EQ preset: {preset} for artist: {artist}")
            else:
                print(f"Failed to apply EQ preset: {preset} for artist: {artist}")
            last_artist = artist

        time.sleep(5)

if __name__ == "__main__":
    main()
