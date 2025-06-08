#!/usr/bin/env python3
"""
eq_helper.py - Helper utilities for the Adaptive EQ application

This script provides additional functionality for the Adaptive EQ application:
1. Testing EQ profile configurations
2. Listing and managing EQ presets
3. Visualizing artist to EQ preset mappings
"""

import os
import json
import sys
import argparse
import subprocess
import time
from services.eq_control import get_available_presets, apply_eq_preset
from services.spotify import get_spotify_client, get_current_track

def load_eq_profiles(config_path="config/eq_profiles.json"):
    """Load existing EQ profiles from config file."""
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {config_path} contains invalid JSON.")
            sys.exit(1)
    else:
        print(f"Warning: Config file {config_path} not found.")
        return {}

def save_eq_profiles(mappings, config_path="config/eq_profiles.json"):
    """Save EQ profiles to config file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(mappings, f, indent=2)
        
        print(f"\nEQ profiles saved to {config_path}")
        return True
    except Exception as e:
        print(f"Error saving EQ profiles: {e}")
        return False

def test_eq_profile(artist, config_path="config/eq_profiles.json"):
    """Test an EQ profile for a specific artist."""
    profiles = load_eq_profiles(config_path)
    
    if artist not in profiles:
        print(f"Artist '{artist}' not found in EQ profiles.")
        return False
    
    preset = profiles[artist]
    available_presets = get_available_presets()
    
    if preset not in available_presets:
        print(f"Error: Preset '{preset}' not found in available presets.")
        print(f"Available presets: {', '.join(available_presets)}")
        return False
    
    print(f"Applying EQ preset '{preset}' for artist '{artist}'...")
    result = apply_eq_preset(preset)
    
    if result:
        print("EQ preset applied successfully!")
    else:
        print("Failed to apply EQ preset.")
    
    return result

def list_artists_by_preset(config_path="config/eq_profiles.json"):
    """List artists grouped by EQ preset."""
    profiles = load_eq_profiles(config_path)
    
    if not profiles:
        print("No EQ profiles found.")
        return
    
    # Group artists by preset
    preset_to_artists = {}
    for artist, preset in profiles.items():
        if preset not in preset_to_artists:
            preset_to_artists[preset] = []
        preset_to_artists[preset].append(artist)
    
    # Print artists grouped by preset
    print("\nArtists grouped by EQ preset:")
    for preset, artists in sorted(preset_to_artists.items()):
        print(f"\n[{preset}] ({len(artists)} artists):")
        for i, artist in enumerate(sorted(artists), 1):
            print(f"  {i}. {artist}")

def monitor_current_track(duration=60, interval=5, config_path="config/eq_profiles.json"):
    """Monitor the current track and apply EQ preset accordingly."""
    print(f"Monitoring current track for {duration} seconds...")
    
    profiles = load_eq_profiles(config_path)
    sp = get_spotify_client()
    
    if not sp:
        print("Error: Could not initialize Spotify client.")
        return
    
    start_time = time.time()
    last_artist = None
    
    while time.time() - start_time < duration:
        track = get_current_track()
        
        if track is None:
            print("No track playing...")
        else:
            artist = track.get("artist")
            if artist != last_artist:
                print(f"\nDetected new artist: {artist}")
                print(f"Track: {track.get('track')}")
                
                if artist in profiles:
                    preset = profiles[artist]
                    print(f"Applying EQ preset: {preset}")
                    apply_eq_preset(preset)
                else:
                    print(f"No EQ preset configured for {artist}")
                
                last_artist = artist
        
        time.sleep(interval)

def remove_artist(artist, config_path="config/eq_profiles.json"):
    """Remove an artist from the EQ profiles."""
    profiles = load_eq_profiles(config_path)
    
    if artist not in profiles:
        print(f"Artist '{artist}' not found in EQ profiles.")
        return False
    
    preset = profiles.pop(artist)
    save_eq_profiles(profiles, config_path)
    
    print(f"Removed artist '{artist}' with preset '{preset}' from EQ profiles.")
    return True

def main():
    parser = argparse.ArgumentParser(description='Helper utilities for the Adaptive EQ application')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Test EQ profile for an artist
    test_parser = subparsers.add_parser('test', help='Test an EQ profile for a specific artist')
    test_parser.add_argument('artist', help='Artist name to test')
    test_parser.add_argument('--config', default='config/eq_profiles.json', help='Path to eq_profiles.json config file')
    
    # List artists by preset
    list_parser = subparsers.add_parser('list', help='List artists grouped by EQ preset')
    list_parser.add_argument('--config', default='config/eq_profiles.json', help='Path to eq_profiles.json config file')
    
    # Monitor current track
    monitor_parser = subparsers.add_parser('monitor', help='Monitor current track and apply EQ preset')
    monitor_parser.add_argument('--duration', type=int, default=60, help='Duration to monitor in seconds')
    monitor_parser.add_argument('--interval', type=int, default=5, help='Polling interval in seconds')
    monitor_parser.add_argument('--config', default='config/eq_profiles.json', help='Path to eq_profiles.json config file')
    
    # Remove artist
    remove_parser = subparsers.add_parser('remove', help='Remove an artist from the EQ profiles')
    remove_parser.add_argument('artist', help='Artist name to remove')
    remove_parser.add_argument('--config', default='config/eq_profiles.json', help='Path to eq_profiles.json config file')
    
    args = parser.parse_args()
    
    if args.command == 'test':
        test_eq_profile(args.artist, args.config)
    elif args.command == 'list':
        list_artists_by_preset(args.config)
    elif args.command == 'monitor':
        monitor_current_track(args.duration, args.interval, args.config)
    elif args.command == 'remove':
        remove_artist(args.artist, args.config)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
