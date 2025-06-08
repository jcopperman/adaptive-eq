#!/usr/bin/env python3

import time
import os
import json
import argparse
from services.spotify import get_current_track
from services.eq_control import apply_eq_preset, force_ui_refresh
from services.logger import setup_logger

# Set up logger
logger = setup_logger("adaptive_eq", log_level="info")

# Load EQ profile mapping (artist → preset)
def load_profile_map(path="config/eq_profiles.json"):
    if not os.path.exists(path):
        logger.warning(f"Profile map not found at {path}")
        return {}
    with open(path, "r") as f:
        return json.load(f)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Adaptive EQ - Automatically adjust EQ based on Spotify tracks")
    parser.add_argument("--force-refresh", action="store_true", help="Force UI refresh when applying presets")
    parser.add_argument("--refresh-interval", type=int, default=30, 
                        help="Interval in seconds to force EasyEffects UI refresh (default: 30)")
    args = parser.parse_args()
    
    logger.info("Starting Adaptive EQ Daemon...")
    profile_map = load_profile_map()
    logger.info(f"Loaded {len(profile_map)} artist → preset mappings")
    
    last_artist = None
    last_refresh = time.time()

    while True:
        track = get_current_track()

        if track is None:
            logger.debug("No track playing...")
            time.sleep(10)
            continue

        artist = track.get("artist")
        current_time = time.time()
        
        # Periodically force a UI refresh
        if args.force_refresh and (current_time - last_refresh > args.refresh_interval):
            logger.debug("Performing periodic UI refresh")
            force_ui_refresh()
            last_refresh = current_time
        
        if artist != last_artist:
            logger.info(f"Detected new artist: {artist}")
            preset = profile_map.get(artist, "default")
            logger.info(f"Applying EQ preset: {preset}")
            
            success = apply_eq_preset(preset, force_ui_refresh=args.force_refresh)
            
            if success:
                logger.info(f"Successfully applied EQ preset: {preset} for artist: {artist}")
            else:
                logger.error(f"Failed to apply EQ preset: {preset} for artist: {artist}")
            last_artist = artist
            last_refresh = current_time

        time.sleep(5)

if __name__ == "__main__":
    main()
