import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import json

# Cached client to avoid repeated authentication
_spotify_client = None
_last_auth_attempt = 0
_auth_retry_interval = 60  # seconds to wait before retrying authentication

# Environment variables for Spotify API authentication
# You'll need to set these or load from a config file
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')

def load_credentials_from_file():
    """Load credentials from the credentials file if environment variables are not set."""
    global SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
    
    if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
        return True
        
    creds_file = os.path.expanduser("~/.adaptive-eq-credentials")
    if os.path.exists(creds_file):
        try:
            with open(creds_file, 'r') as f:
                for line in f:
                    if line.startswith('export SPOTIFY_CLIENT_ID='):
                        SPOTIFY_CLIENT_ID = line.split('=')[1].strip().strip("'").strip('"')
                    elif line.startswith('export SPOTIFY_CLIENT_SECRET='):
                        SPOTIFY_CLIENT_SECRET = line.split('=')[1].strip().strip("'").strip('"')
                    elif line.startswith('export SPOTIFY_REDIRECT_URI='):
                        SPOTIFY_REDIRECT_URI = line.split('=')[1].strip().strip("'").strip('"')
            
            if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
                return True
        except Exception as e:
            print(f"Error loading credentials from file: {e}")
    
    return False

def get_spotify_client():
    """
    Initialize and return a Spotify client with proper authentication.
    Returns None if authentication fails.
    
    Uses a cached client to avoid repeated authentication.
    """
    global _spotify_client, _last_auth_attempt
    
    # If we already have a client, return it
    if _spotify_client:
        try:
            # Test the client with a simple API call
            _spotify_client.current_user()
            return _spotify_client
        except:
            # If the client is no longer valid, clear it and try again
            print("Cached Spotify client is no longer valid. Re-authenticating...")
            _spotify_client = None
    
    # If we've recently tried and failed to authenticate, don't try again yet
    current_time = time.time()
    if current_time - _last_auth_attempt < _auth_retry_interval:
        return None
    
    _last_auth_attempt = current_time
    
    # Try to load credentials if not already set
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        if not load_credentials_from_file():
            print("Spotify credentials not found. Please set up your credentials.")
            return None
    
    try:
        # Set up authentication scope
        scope = "user-read-currently-playing user-read-playback-state"
        
        # Create Spotify client
        cache_path = os.path.join(os.path.expanduser('~'), '.adaptive-eq-spotify-cache')
        
        # Make sure the directory exists
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope,
            cache_path=cache_path
        ))
        
        # Test the connection
        sp.current_user()
        
        # Cache the client for future use
        _spotify_client = sp
        return sp
    except Exception as e:
        print(f"Spotify authentication error: {e}")
        return None

def get_current_track():
    """
    Get information about the currently playing track.
    Returns a dict with artist, track, album, etc. or None if no track is playing
    or there's an error.
    """
    client = get_spotify_client()
    if not client:
        return None
    
    try:
        # Get currently playing track
        current = client.current_playback()
        
        if not current or not current.get('is_playing'):
            return None
            
        item = current.get('item')
        if not item:
            return None
            
        # Extract relevant track information
        track_info = {
            'artist': item['artists'][0]['name'],  # Primary artist
            'all_artists': [artist['name'] for artist in item['artists']],
            'track': item['name'],
            'album': item['album']['name'],
            'id': item['id'],
            'uri': item['uri']
        }
        
        # Store in cache for offline use
        _cache_track_info(track_info)
        
        return track_info
    except Exception as e:
        print(f"Error getting current track: {e}")
        
        # If we can't get the current track, try to use cached information
        cached_track = _get_cached_track_info()
        if cached_track:
            print("Using cached track information.")
            return cached_track
        
        return None

def _cache_track_info(track_info):
    """Cache track information for offline use."""
    try:
        cache_dir = os.path.expanduser("~/.cache/adaptive-eq")
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, "last_track.json")
        with open(cache_file, 'w') as f:
            json.dump(track_info, f)
    except Exception as e:
        print(f"Error caching track info: {e}")

def _get_cached_track_info():
    """Get cached track information."""
    try:
        cache_file = os.path.expanduser("~/.cache/adaptive-eq/last_track.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error reading cached track info: {e}")
    
    return None

def get_artist_genres(artist_name):
    """
    Get genres associated with an artist.
    Returns a list of genre strings or empty list if none found or there's an error.
    """
    client = get_spotify_client()
    if not client:
        return []
    
    try:
        # Search for the artist
        results = client.search(q=f'artist:{artist_name}', type='artist', limit=1)
        
        if not results or not results['artists']['items']:
            return []
            
        artist = results['artists']['items'][0]
        
        # Check if this is the correct artist (name match)
        if artist['name'].lower() != artist_name.lower():
            # Try to find a better match
            all_artists = results['artists']['items']
            for a in all_artists:
                if a['name'].lower() == artist_name.lower():
                    artist = a
                    break
        
        return artist.get('genres', [])
    except Exception as e:
        print(f"Error getting artist genres: {e}")
        return []
