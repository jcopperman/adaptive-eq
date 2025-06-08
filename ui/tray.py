import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib, Gio
import os
import threading
import signal
import sys
import time
import argparse

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.spotify import get_current_track
from services.eq_control import get_available_presets, apply_eq_preset, force_ui_refresh
from services.logger import setup_logger

# Set up logger
logger = setup_logger("adaptive_eq_tray", log_level="info")

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
        self.current_preset = "None"
        self.last_notification_id = None
        
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
        
        # EQ Preset status
        self.preset_item = Gtk.MenuItem(label="Current EQ: None")
        self.preset_item.set_sensitive(False)
        menu.append(self.preset_item)
        
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
        
        # Add option to refresh profiles
        refresh_item = Gtk.MenuItem(label="Refresh Profiles")
        refresh_item.connect("activate", self.refresh_profiles)
        menu.append(refresh_item)
        
        # Add option to create EQ presets
        create_presets_item = Gtk.MenuItem(label="Create EQ Presets")
        create_presets_item.connect("activate", self.create_eq_presets)
        menu.append(create_presets_item)
        
        # Add option to configure Spotify
        config_spotify_item = Gtk.MenuItem(label="Configure Spotify")
        config_spotify_item.connect("activate", self.configure_spotify)
        menu.append(config_spotify_item)
        
        # Add option to force UI refresh
        force_refresh_item = Gtk.MenuItem(label="Force EasyEffects Refresh")
        force_refresh_item.connect("activate", self.force_refresh)
        menu.append(force_refresh_item)
        
        # Add separator
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
            logger.info("Adaptive EQ mode enabled")
            self.show_notification("Adaptive EQ", "Adaptive EQ mode enabled")
        else:
            logger.info("Adaptive EQ mode disabled (manual mode)")
            self.show_notification("Adaptive EQ", "Manual EQ mode enabled")
    
    def apply_preset(self, widget, preset_name):
        """Apply a specific EQ preset manually"""
        success = apply_eq_preset(preset_name, force_ui_refresh=True)
        if success:
            self.current_preset = preset_name
            self.update_preset_status(preset_name)
            self.show_notification("Adaptive EQ", f"Applied preset: {preset_name}")
            return True
        else:
            self.show_notification("Adaptive EQ", f"Failed to apply preset: {preset_name}", "error")
            return False
    
    def refresh_profiles(self, widget=None):
        """Refresh the EQ profiles and presets"""
        # Rebuild the presets submenu
        presets_item = None
        for item in self.menu.get_children():
            if isinstance(item, Gtk.MenuItem) and item.get_label() == "EQ Presets":
                presets_item = item
                break
        
        if presets_item:
            presets_menu = Gtk.Menu()
            presets = get_available_presets()
            for preset in presets:
                preset_item = Gtk.MenuItem(label=preset)
                preset_item.connect("activate", self.apply_preset, preset)
                presets_menu.append(preset_item)
            
            presets_menu.show_all()
            presets_item.set_submenu(presets_menu)
            
            self.show_notification("Adaptive EQ", "Profiles refreshed")
    
    def create_eq_presets(self, widget=None):
        """Launch the create_eq_presets.py script"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'create_eq_presets.py'), '--all'])
            self.show_notification("Adaptive EQ", "Creating EQ presets...", "info")
        except Exception as e:
            logger.error(f"Error launching create_eq_presets.py: {e}")
            self.show_notification("Adaptive EQ", f"Error creating presets: {e}", "error")
    
    def configure_spotify(self, widget=None):
        """Launch the configure_spotify.py script"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'configure_spotify.py')])
        except Exception as e:
            logger.error(f"Error launching configure_spotify.py: {e}")
            self.show_notification("Adaptive EQ", f"Error configuring Spotify: {e}", "error")
    
    def force_refresh(self, widget=None):
        """Force EasyEffects UI to refresh"""
        logger.info("Manually forcing EasyEffects UI refresh")
        if force_ui_refresh():
            self.show_notification("Adaptive EQ", "EasyEffects UI refresh triggered", "info")
        else:
            self.show_notification("Adaptive EQ", "EasyEffects not running, nothing to refresh", "info")
            
        # Also reapply the current preset if one is active
        if self.current_preset and self.current_preset != "None":
            logger.info(f"Reapplying current preset: {self.current_preset}")
            apply_eq_preset(self.current_preset, force_ui_refresh=True)
            self.show_notification("Adaptive EQ", f"Reapplied preset: {self.current_preset}")
    
    def update_status(self, track_info=None):
        """Update the status display in the menu"""
        if track_info:
            status_text = f"▶️ {track_info['artist']} - {track_info['track']}"
        else:
            status_text = "No track playing"
            
        # Update in the UI thread
        GLib.idle_add(self._update_status_ui, status_text)
    
    def update_preset_status(self, preset_name):
        """Update the preset status display in the menu"""
        GLib.idle_add(self._update_preset_ui, preset_name)
    
    def _update_status_ui(self, status_text):
        """Update UI elements (must be called from UI thread)"""
        self.status_item.set_label(status_text)
        return False  # Required for GLib.idle_add
    
    def _update_preset_ui(self, preset_name):
        """Update preset UI elements (must be called from UI thread)"""
        self.preset_item.set_label(f"Current EQ: {preset_name}")
        return False  # Required for GLib.idle_add
    
    def show_notification(self, title, message, notification_type="info"):
        """Show a desktop notification"""
        try:
            notification = Gio.Notification.new(title)
            notification.set_body(message)
            
            if notification_type == "error":
                notification.set_priority(Gio.NotificationPriority.HIGH)
            else:
                notification.set_priority(Gio.NotificationPriority.NORMAL)
            
            # Create a new application object for notifications
            application = Gio.Application.new("com.github.adaptive-eq", Gio.ApplicationFlags.FLAGS_NONE)
            application.register()
            application.send_notification(None, notification)
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
    
    def monitor_spotify(self):
        """Background thread that monitors Spotify and applies EQ profiles"""
        import json
        import os

        # Load EQ profile mapping (artist → preset)
        profile_map = {}
        profile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'eq_profiles.json')
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                profile_map = json.load(f)
        
        logger.info(f"Loaded {len(profile_map)} artist → preset mappings")
        last_artist = None
        current_preset = None
        retry_count = 0
        max_retries = 3

        while self.running:
            try:
                track = get_current_track()
                retry_count = 0  # Reset retry counter on successful API call
                self.update_status(track)

                if track and self.adaptive_mode:
                    artist = track.get("artist")
                    if artist != last_artist:
                        logger.info(f"Detected new artist: {artist}")
                        preset = profile_map.get(artist, "default")
                        
                        # Only change preset if it's different from the current one
                        if preset != current_preset:
                            logger.info(f"Applying EQ preset: {preset}")
                            success = apply_eq_preset(preset, force_ui_refresh=True)
                            if success:
                                logger.info(f"Successfully applied EQ preset: {preset} for artist: {artist}")
                                current_preset = preset
                                self.current_preset = preset
                                self.update_preset_status(preset)
                                
                                # Show notification for preset change
                                self.show_notification(
                                    "Adaptive EQ", 
                                    f"Applied '{preset}' preset for {artist}"
                                )
                            else:
                                logger.warning(f"Failed to apply EQ preset: {preset} for artist: {artist}")
                        else:
                            logger.info(f"Preset {preset} already active, skipping application")
                        
                        last_artist = artist
            except Exception as e:
                retry_count += 1
                logger.error(f"Error in monitor_spotify: {e}")
                if retry_count >= max_retries:
                    self.show_notification(
                        "Adaptive EQ Error", 
                        f"Failed to connect to Spotify after {max_retries} attempts. Please check your Spotify connection.",
                        "error"
                    )
                    retry_count = 0  # Reset after showing notification
                    
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
