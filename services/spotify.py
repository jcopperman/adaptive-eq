import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Environment variables for Spotify API authentication
# You'll need to set these or load from a config file
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')

def get_spotify_client():
    """
    Initialize and return a Spotify client with proper authentication.
    Returns None if authentication fails.
    """
    try:
        # Set up authentication scope
        scope = "user-read-currently-playing user-read-playback-state"
        
        # Create Spotify client
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope,
            cache_path=os.path.join(os.path.expanduser('~'), '.adaptive-eq-spotify-cache')
        ))
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
        
        return track_info
    except Exception as e:
        print(f"Error getting current track: {e}")
        return None
