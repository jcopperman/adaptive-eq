#!/usr/bin/env python3

import os
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

class SpotifyCredentialsDialog(Gtk.Dialog):
    def __init__(self, parent=None):
        super().__init__(title="Spotify API Credentials", parent=parent)
        self.set_modal(True)
        self.set_default_size(400, 200)
        
        # Get current credentials
        current_creds = self.load_credentials()
        
        # Create form
        box = self.get_content_area()
        box.set_spacing(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        # Add labels and entries
        label = Gtk.Label(label="<b>Enter your Spotify API credentials</b>")
        label.set_use_markup(True)
        box.add(label)
        
        # Client ID
        client_id_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        client_id_label = Gtk.Label(label="Client ID:")
        client_id_label.set_width_chars(15)
        client_id_label.set_xalign(0)
        self.client_id_entry = Gtk.Entry()
        self.client_id_entry.set_text(current_creds.get('client_id', ''))
        client_id_box.pack_start(client_id_label, False, False, 0)
        client_id_box.pack_start(self.client_id_entry, True, True, 0)
        box.add(client_id_box)
        
        # Client Secret
        client_secret_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        client_secret_label = Gtk.Label(label="Client Secret:")
        client_secret_label.set_width_chars(15)
        client_secret_label.set_xalign(0)
        self.client_secret_entry = Gtk.Entry()
        self.client_secret_entry.set_text(current_creds.get('client_secret', ''))
        client_secret_box.pack_start(client_secret_label, False, False, 0)
        client_secret_box.pack_start(self.client_secret_entry, True, True, 0)
        box.add(client_secret_box)
        
        # Redirect URI
        redirect_uri_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        redirect_uri_label = Gtk.Label(label="Redirect URI:")
        redirect_uri_label.set_width_chars(15)
        redirect_uri_label.set_xalign(0)
        self.redirect_uri_entry = Gtk.Entry()
        self.redirect_uri_entry.set_text(current_creds.get('redirect_uri', 'http://localhost:8888/callback'))
        redirect_uri_box.pack_start(redirect_uri_label, False, False, 0)
        redirect_uri_box.pack_start(self.redirect_uri_entry, True, True, 0)
        box.add(redirect_uri_box)
        
        # Info label
        info_label = Gtk.Label(label="<small>You can get your credentials from the Spotify Developer Dashboard: \nhttps://developer.spotify.com/dashboard/</small>")
        info_label.set_use_markup(True)
        box.add(info_label)
        
        # Add buttons
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Save", Gtk.ResponseType.OK)
        
        self.show_all()
    
    def load_credentials(self):
        creds = {
            'client_id': '',
            'client_secret': '',
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
        
        return creds
    
    def save_credentials(self):
        client_id = self.client_id_entry.get_text()
        client_secret = self.client_secret_entry.get_text()
        redirect_uri = self.redirect_uri_entry.get_text()
        
        creds_file = os.path.expanduser("~/.adaptive-eq-credentials")
        with open(creds_file, 'w') as f:
            f.write("# Spotify API credentials for Adaptive EQ\n")
            f.write(f"export SPOTIFY_CLIENT_ID='{client_id}'\n")
            f.write(f"export SPOTIFY_CLIENT_SECRET='{client_secret}'\n")
            f.write(f"export SPOTIFY_REDIRECT_URI='{redirect_uri}'\n")
        
        return True

def main():
    dialog = SpotifyCredentialsDialog()
    response = dialog.run()
    
    if response == Gtk.ResponseType.OK:
        dialog.save_credentials()
        print("Credentials saved successfully!")
    else:
        print("Cancelled")
    
    dialog.destroy()
    
if __name__ == "__main__":
    main()
