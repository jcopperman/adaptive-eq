import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib
import os
import threading
import signal
import sys

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.spotify import get_current_track
from services.eq_control import get_available_presets, apply_eq_preset

class AdaptiveEQTray:
    def __init__(self):
        self.app = 'adaptive-eq'
        self.indicator = AppIndicator3.Indicator.new(
            self.app,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'icon.png'),
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        self.current_track = None
        self.running = True
        self.adaptive_mode = True
        
        # Initialize the menu
        self.menu = self.create_menu()
        self.indicator.set_menu(self.menu)
        
        # Start background thread for monitoring
        self.monitor_thread = threading.Thread(target=self.monitor_spotify)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def create_menu(self):
        """Create the tray icon menu"""
        menu = Gtk.Menu()
        
        # Status item (what's currently playing)
        self.status_item = Gtk.MenuItem(label="No track playing")
        self.status_item.set_sensitive(False)
        menu.append(self.status_item)
        
        menu.append(Gtk.SeparatorMenuItem())
        
        # Adaptive mode toggle
        self.adaptive_item = Gtk.CheckMenuItem(label="Adaptive Mode")
        self.adaptive_item.set_active(True)
        self.adaptive_item.connect("toggled", self.toggle_adaptive)
        menu.append(self.adaptive_item)
        
        menu.append(Gtk.SeparatorMenuItem())
        
        # Manual EQ preset selection submenu
        presets_item = Gtk.MenuItem(label="EQ Presets")
        presets_menu = Gtk.Menu()
        
        # Add all available presets
        presets = get_available_presets()
        for preset in presets:
            preset_item = Gtk.MenuItem(label=preset)
            preset_item.connect("activate", self.apply_preset, preset)
            presets_menu.append(preset_item)
        
        presets_item.set_submenu(presets_menu)
        menu.append(presets_item)
        
        menu.append(Gtk.SeparatorMenuItem())
        
        # Quit item
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit)
        menu.append(quit_item)
        
        menu.show_all()
        return menu
    
    def toggle_adaptive(self, widget):
        """Toggle adaptive mode on/off"""
        self.adaptive_mode = widget.get_active()
        if self.adaptive_mode:
            print("Adaptive EQ mode enabled")
        else:
            print("Adaptive EQ mode disabled (manual mode)")
    
    def apply_preset(self, widget, preset_name):
        """Apply a specific EQ preset manually"""
        apply_eq_preset(preset_name)
    
    def update_status(self, track_info=None):
        """Update the status display in the menu"""
        if track_info:
            status_text = f"▶️ {track_info['artist']} - {track_info['track']}"
        else:
            status_text = "No track playing"
            
        # Update in the UI thread
        GLib.idle_add(self._update_status_ui, status_text)
    
    def _update_status_ui(self, status_text):
        """Update UI elements (must be called from UI thread)"""
        self.status_item.set_label(status_text)
        return False  # Required for GLib.idle_add
    
    def monitor_spotify(self):
        """Background thread that monitors Spotify and applies EQ profiles"""
        import time
        from services.eq_control import apply_eq_preset
        import json
        import os

        # Load EQ profile mapping (artist → preset)
        profile_map = {}
        profile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'eq_profiles.json')
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                profile_map = json.load(f)
        
        last_artist = None

        while self.running:
            track = get_current_track()
            self.update_status(track)

            if track and self.adaptive_mode:
                artist = track.get("artist")
                if artist != last_artist:
                    print(f"Detected new artist: {artist}")
                    preset = profile_map.get(artist, "default")
                    print(f"Applying EQ preset: {preset}")
                    apply_eq_preset(preset)
                    last_artist = artist

            time.sleep(5)
    
    def quit(self, widget):
        """Quit the application"""
        self.running = False
        Gtk.main_quit()

def main():
    # Set up signal handling for clean exit
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # Start the tray application
    app = AdaptiveEQTray()
    Gtk.main()

if __name__ == "__main__":
    main()
