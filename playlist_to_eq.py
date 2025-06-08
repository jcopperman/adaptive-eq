#!/usr/bin/env python3
"""
playlist_to_eq.py - Extract artists from a Spotify playlist and map them to EQ profiles

This script takes a Spotify playlist URL, extracts all unique artists,
and updates the eq_profiles.json file with the artist -> EQ profile mappings.
"""

import os
import sys
import json
import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def load_credentials():
    """Load Spotify credentials from the credentials file."""
    creds = {
        'client_id': None,
        'client_secret': None,
        'redirect_uri': 'http://localhost:8888/callback'
    }
    
    creds_file = os.path.expanduser("~/.adaptive-eq-credentials")
    if os.path.exists(creds_file):
        with open(creds_file, 'r') as f:
            for line in f:
                if line.startswith('export SPOTIFY_CLIENT_ID='):
                    creds['client_id'] = line.split('=')[1].strip().strip("'").strip('"')
                elif line.startswith('export SPOTIFY_CLIENT_SECRET='):
                    creds['client_secret'] = line.split('=')[1].strip().strip("'").strip('"')
                elif line.startswith('export SPOTIFY_REDIRECT_URI='):
                    creds['redirect_uri'] = line.split('=')[1].strip().strip("'").strip('"')
    
    if not creds['client_id'] or not creds['client_secret']:
        print("Error: Spotify credentials not found or incomplete.")
        print("Please run ./configure_spotify.py first.")
        sys.exit(1)
    
    return creds

def get_spotify_client():
    """Initialize and return an authenticated Spotify client."""
    creds = load_credentials()
    
    try:
        # Set up authentication scope
        scope = "playlist-read-private user-library-read"
        
        # Create Spotify client
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=creds['client_id'],
            client_secret=creds['client_secret'],
            redirect_uri=creds['redirect_uri'],
            scope=scope,
            cache_path=os.path.expanduser('~/.adaptive-eq-spotify-cache')
        ))
        return sp
    except Exception as e:
        print(f"Error authenticating with Spotify: {e}")
        sys.exit(1)

def extract_playlist_id(playlist_url):
    """Extract the playlist ID from a Spotify playlist URL."""
    if 'spotify.com/playlist/' in playlist_url:
        playlist_id = playlist_url.split('playlist/')[1].split('?')[0]
        return playlist_id
    else:
        print("Error: Invalid Spotify playlist URL.")
        print("URL should look like: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
        sys.exit(1)

def get_unique_artists(sp, playlist_id):
    """Get all unique artists from a Spotify playlist."""
    try:
        results = sp.playlist_items(playlist_id, fields='items.track.artists,next', limit=100)
        
        # Extract all artist names
        artists = []
        artist_ids = []
        tracks_processed = 0
        
        items = results['items']
        while items:
            for item in items:
                track = item.get('track')
                if track and track.get('artists'):
                    for artist in track['artists']:
                        artists.append(artist['name'])
                        if 'id' in artist:
                            artist_ids.append(artist['id'])
            
            tracks_processed += len(items)
            print(f"Processed {tracks_processed} tracks...")
            
            if results.get('next'):
                results = sp.next(results)
                items = results['items']
            else:
                items = None
        
        # Get unique artists and their IDs
        unique_artists = []
        unique_artist_ids = []
        
        # Use a dictionary to track unique artists while preserving order
        artist_dict = {}
        for i, artist in enumerate(artists):
            if artist not in artist_dict:
                artist_dict[artist] = i
                
        # Sort by order of appearance
        unique_artists = sorted(artist_dict.keys(), key=lambda k: artist_dict[k])
        
        # Get corresponding IDs (may not have IDs for all artists)
        unique_artist_ids = [artist_ids[artists.index(artist)] for artist in unique_artists if artist in artists and artists.index(artist) < len(artist_ids)]
        
        return unique_artists, unique_artist_ids
    
    except Exception as e:
        print(f"Error getting playlist data: {e}")
        sys.exit(1)

def recommend_preset(genres):
    """Recommend an EQ preset based on artist genres."""
    # Define genre to preset mapping
    genre_preset_map = {
        'rock': 'rock',
        'alternative': 'alternative',
        'metal': 'rock',
        'hard rock': 'rock',
        'hip hop': 'hiphop',
        'rap': 'hiphop',
        'trap': 'hiphop',
        'pop': 'pop',
        'dance': 'electronic',
        'electronic': 'electronic',
        'edm': 'electronic',
        'house': 'electronic',
        'techno': 'electronic',
        'ambient': 'electronic',
        'classical': 'classical',
        'orchestra': 'orchestral',
        'orchestral': 'orchestral',
        'soundtrack': 'orchestral',
        'folk': 'acoustic',
        'acoustic': 'acoustic',
        'jazz': 'jazz',
        'blues': 'blues',
        'soul': 'vocal',
        'r&b': 'vocal',
        'vocal': 'vocal',
        'reggae': 'reggae'
    }
    
    if not genres:
        return None
    
    # Count genre matches
    preset_counts = {}
    for genre in genres:
        genre_lower = genre.lower()
        
        # Check for partial matches
        for key, preset in genre_preset_map.items():
            if key in genre_lower:
                preset_counts[preset] = preset_counts.get(preset, 0) + 1
    
    # Return the most matched preset or None if no matches
    if preset_counts:
        return max(preset_counts.items(), key=lambda x: x[1])[0]
    
    return None

def get_artist_genres(sp, artist_ids):
    """Get genre information for artists."""
    genre_map = {}
    
    if not artist_ids:
        return genre_map
        
    # Process in batches of 50 (Spotify API limit)
    batch_size = 50
    for i in range(0, len(artist_ids), batch_size):
        batch = artist_ids[i:i+batch_size]
        try:
            results = sp.artists(batch)
            for artist in results['artists']:
                if artist['name'] not in genre_map and artist['genres']:
                    genre_map[artist['name']] = artist['genres']
            
            print(f"Retrieved genre info for {len(genre_map)} artists...")
        except Exception as e:
            print(f"Error getting artist genres: {e}")
    
    return genre_map

def get_available_presets():
    """Get available EQ presets from EasyEffects."""
    presets_path = os.path.expanduser("~/.config/easyeffects/output/")
    if not os.path.exists(presets_path):
        print(f"Warning: EasyEffects presets directory not found: {presets_path}")
        return []
    
    try:
        # List all .json files in the presets directory
        presets = [f.replace('.json', '') for f in os.listdir(presets_path) 
                  if f.endswith('.json')]
        return presets
    except Exception as e:
        print(f"Error listing EasyEffects presets: {e}")
        return []

def map_artists_to_presets(artists, existing_profiles, available_presets, default_preset):
    """Map artists to EQ presets, prompting the user for input when needed."""
    mappings = existing_profiles.copy()
    
    # If no available presets, use the default
    if not available_presets:
        print("Warning: No EasyEffects presets found. Using 'default' for all artists.")
        for artist in artists:
            if artist not in mappings:
                mappings[artist] = "default"
        return mappings
    
    # Show available presets
    print("\nAvailable EQ presets:")
    for i, preset in enumerate(available_presets, 1):
        print(f"{i}. {preset}")
    
    # Options for mapping
    print("\nMapping options:")
    print("1. Map all new artists to a single preset")
    print("2. Map each artist individually (interactive)")
    print("3. Skip new artists (keep existing mappings only)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        print("\nAvailable presets:")
        for i, preset in enumerate(available_presets, 1):
            print(f"{i}. {preset}")
        
        preset_choice = input(f"\nSelect preset number (1-{len(available_presets)}) or name: ").strip()
        
        if preset_choice.isdigit() and 1 <= int(preset_choice) <= len(available_presets):
            selected_preset = available_presets[int(preset_choice) - 1]
        elif preset_choice in available_presets:
            selected_preset = preset_choice
        else:
            print(f"Invalid preset selection. Using default preset: {default_preset}")
            selected_preset = default_preset
        
        for artist in artists:
            if artist not in mappings:
                mappings[artist] = selected_preset
    
    elif choice == '2':
        for artist in artists:
            if artist not in mappings:
                print(f"\nArtist: {artist}")
                print("Available presets:")
                for i, preset in enumerate(available_presets, 1):
                    print(f"{i}. {preset}")
                
                preset_choice = input(f"Select preset number (1-{len(available_presets)}) or name [default={default_preset}]: ").strip()
                
                if not preset_choice:
                    mappings[artist] = default_preset
                elif preset_choice.isdigit() and 1 <= int(preset_choice) <= len(available_presets):
                    mappings[artist] = available_presets[int(preset_choice) - 1]
                elif preset_choice in available_presets:
                    mappings[artist] = preset_choice
                else:
                    print(f"Invalid preset selection. Using default preset: {default_preset}")
                    mappings[artist] = default_preset
    
    elif choice == '3':
        print("Keeping existing mappings only.")
    
    else:
        print(f"Invalid choice. Using default preset: {default_preset} for all new artists.")
        for artist in artists:
            if artist not in mappings:
                mappings[artist] = default_preset
    
    return mappings

def save_eq_profiles(mappings, config_path):
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

def load_eq_profiles(config_path):
    """Load existing EQ profiles from config file."""
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {config_path} contains invalid JSON.")
            sys.exit(1)
    return {}

def process_playlist(sp, playlist_url, existing_profiles, available_presets, default_preset, config_path, auto_map=False):
    """Process a single playlist and update the EQ profiles."""
    # Get playlist ID
    playlist_id = extract_playlist_id(playlist_url)
    
    # Get playlist info
    try:
        playlist = sp.playlist(playlist_id, fields='name,owner.display_name')
        print(f"\nExtracting artists from playlist: {playlist['name']} (by {playlist['owner']['display_name']})")
    except Exception as e:
        print(f"Error getting playlist info: {e}")
        return
    
    # Get unique artists
    print("\nFetching artists from playlist...")
    artists, artist_ids = get_unique_artists(sp, playlist_id)
    
    print(f"\nFound {len(artists)} unique artists in the playlist.")
    
    # Count how many artists are already mapped
    already_mapped = sum(1 for artist in artists if artist in existing_profiles)
    
    print(f"{already_mapped} artists are already mapped to EQ profiles.")
    print(f"{len(artists) - already_mapped} artists need to be mapped.")
    
    if len(artists) - already_mapped == 0:
        print("\nAll artists in this playlist are already mapped.")
        if not auto_map:
            choice = input("Do you want to review/update existing mappings? (y/n): ").strip().lower()
            if choice != 'y':
                print("No changes made to EQ profiles.")
                return
    
    # If auto-mapping is enabled, get genre information for unmapped artists
    if auto_map and len(artists) - already_mapped > 0:
        print("\nAuto-mapping artists based on genre...")
        
        # Get genre information for artists
        genre_map = get_artist_genres(sp, artist_ids)
        
        # Create a temporary mapping for unmapped artists based on genres
        temp_mappings = existing_profiles.copy()
        for artist in artists:
            if artist not in temp_mappings:
                genres = genre_map.get(artist, [])
                if genres:
                    print(f"Artist: {artist}")
                    print(f"Genres: {', '.join(genres)}")
                    
                    # Recommend a preset based on genres
                    recommended_preset = recommend_preset(genres)
                    if recommended_preset and recommended_preset in available_presets:
                        print(f"Recommended preset: {recommended_preset}")
                        temp_mappings[artist] = recommended_preset
                    else:
                        print(f"No suitable preset found. Using default: {default_preset}")
                        temp_mappings[artist] = default_preset
                else:
                    print(f"No genre info found for {artist}. Using default preset.")
                    temp_mappings[artist] = default_preset
        
        # Ask for confirmation
        print("\nProposed mappings:")
        for artist in [a for a in artists if a not in existing_profiles]:
            print(f"{artist} → {temp_mappings[artist]}")
            
        choice = input("\nApply these mappings? (y/n): ").strip().lower()
        if choice == 'y':
            save_eq_profiles(temp_mappings, config_path)
            print("\nEQ profiles updated with auto-mapped artists.")
            return
        else:
            print("Continuing with manual mapping...")
    
    # Map artists to presets manually
    mappings = map_artists_to_presets(artists, existing_profiles, available_presets, default_preset)
    
    # Save mappings
    save_eq_profiles(mappings, config_path)

def main():
    parser = argparse.ArgumentParser(description='Extract artists from a Spotify playlist and map them to EQ profiles')
    parser.add_argument('playlist_url', nargs='?', help='Spotify playlist URL to extract artists from')
    parser.add_argument('--playlists', '-p', help='File containing list of Spotify playlist URLs (one per line)')
    parser.add_argument('--default', default='default', help='Default EQ preset to use for unmapped artists')
    parser.add_argument('--config', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'eq_profiles.json'),
                        help='Path to eq_profiles.json config file')
    parser.add_argument('--auto', '-a', action='store_true', help='Automatically map artists based on genre')
    parser.add_argument('--list-artists', '-l', action='store_true', help='List all artists in eq_profiles.json')
    
    args = parser.parse_args()
    
    # Load existing EQ profiles
    existing_profiles = load_eq_profiles(args.config)
    
    # Just list artists if requested
    if args.list_artists:
        print(f"\nArtists in {args.config}:")
        for i, (artist, preset) in enumerate(sorted(existing_profiles.items()), 1):
            print(f"{i}. {artist} → {preset}")
        return
    
    # Check arguments
    if not args.playlist_url and not args.playlists:
        parser.print_help()
        print("\nError: You must provide either a playlist URL or a file with playlist URLs")
        sys.exit(1)
    
    print(f"Using config file: {args.config}")
    print(f"Default preset: {args.default}")
    
    # Get Spotify client
    sp = get_spotify_client()
    
    # Get available presets
    available_presets = get_available_presets()
    
    # Process a single playlist
    if args.playlist_url:
        process_playlist(sp, args.playlist_url, existing_profiles, available_presets, args.default, args.config, args.auto)
    
    # Process multiple playlists
    if args.playlists:
        if not os.path.exists(args.playlists):
            print(f"Error: Playlist file not found: {args.playlists}")
            sys.exit(1)
            
        with open(args.playlists, 'r') as f:
            playlist_urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        
        print(f"\nProcessing {len(playlist_urls)} playlists...")
        for i, url in enumerate(playlist_urls, 1):
            print(f"\n[{i}/{len(playlist_urls)}] Processing playlist: {url}")
            try:
                process_playlist(sp, url, existing_profiles, available_presets, args.default, args.config, args.auto)
                # Reload profiles after each playlist
                existing_profiles = load_eq_profiles(args.config)
            except Exception as e:
                print(f"Error processing playlist {url}: {e}")
    
    print("\nAll playlists processed successfully!")
    print(f"Total artists in profile: {len(load_eq_profiles(args.config))}")

if __name__ == "__main__":
    main()
