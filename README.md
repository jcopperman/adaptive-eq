# Adaptive EQ

An automatic equalizer adjustment tool for Linux audiophiles. This application automatically adjusts your EasyEffects equalizer settings based on what you're listening to in Spotify.

![Adaptive EQ Logo](icon.png)

## Features

- **Automatic EQ Adjustment**: Detects the currently playing Spotify track and applies the appropriate EQ preset
- **Genre-Based EQ Profiles**: Maps artists to genre-specific EQ presets for optimal sound
- **System Tray Interface**: Convenient access to control and status information
- **Desktop Notifications**: Notifications when EQ presets are changed
- **Offline Support**: Caches track information for use when Spotify is offline
- **Portable**: Supports multiple Linux distributions and can be packaged as an AppImage
- **Easy Setup**: Automatic creation of EQ presets and simple configuration

## Requirements

- Linux with EasyEffects installed
- Python 3.6+
- Spotify account
- Spotify Developer API credentials
- Required system packages for the GTK interface:
  ```bash
  # Debian/Ubuntu
  sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
  
  # Fedora
  sudo dnf install python3-gobject python3-cairo gtk3 libappindicator-gtk3
  
  # Arch Linux
  sudo pacman -Sy python-gobject python-cairo gtk3 libappindicator-gtk3
  ```

## Quick Installation

For the fastest installation:

```bash
# Clone repository
git clone https://github.com/jcopperman/adaptive-eq.git
cd adaptive-eq

# Run setup script - this installs all dependencies
./setup.sh

# Configure Spotify API credentials
./configure_spotify.py

# Create EQ presets for different music genres
./create_eq_presets.py --all

# Launch the app
./run_tray.sh
```

## Detailed Installation

### 1. Clone this repository:
```bash
git clone https://github.com/jcopperman/adaptive-eq.git
cd adaptive-eq
```

### 2. Run the setup script:
```bash
./setup.sh
```

### 3. Configure your Spotify API credentials:
```bash
./configure_spotify.py
```
Or manually edit the `~/.adaptive-eq-credentials` file:
```bash
export SPOTIFY_CLIENT_ID='your_client_id'
export SPOTIFY_CLIENT_SECRET='your_client_secret'
export SPOTIFY_REDIRECT_URI='http://localhost:8888/callback'
```

### 4. Create EQ presets for different music genres:
```bash
./create_eq_presets.py --all
```

### 5. Launch the application:
```bash
./run_tray.sh
```

## Usage

### Running the application

```bash
./adaptive-eq-launcher
```

### Desktop Integration

To add Adaptive EQ to your applications menu:

```bash
sudo cp app.desktop /usr/local/share/applications/adaptive-eq.desktop
```

### Configuration

Edit `config/eq_profiles.json` to map artists to EQ presets.

Example:
```json
{
  "Daft Punk": "electronic",
  "Hans Zimmer": "orchestral",
  "Metallica": "rock"
}
```

### Using the playlist_to_eq.py Helper

The `playlist_to_eq.py` script helps you extract artists from your Spotify playlists and map them to EQ presets.

```bash
# Process a single playlist
./playlist_to_eq.py https://open.spotify.com/playlist/37i9dQZF1DX4dyzvaqLBqZ

# Process multiple playlists from a file
./playlist_to_eq.py --playlists playlists.txt

# Automatically map artists based on their genres
./playlist_to_eq.py --auto https://open.spotify.com/playlist/37i9dQZF1DX4dyzvaqLBqZ

# List all artists in your EQ profiles
./playlist_to_eq.py --list-artists
```

### Using the eq_helper.py Utility

The `eq_helper.py` utility provides additional functionality for managing and testing your EQ profiles.

```bash
# Test an EQ profile for a specific artist
./eq_helper.py test "Daft Punk"

# List artists grouped by EQ preset
./eq_helper.py list

# Monitor the current track and apply EQ presets (for 60 seconds)
./eq_helper.py monitor --duration 60

# Remove an artist from your EQ profiles
./eq_helper.py remove "Artist Name"
```

## Building Portable Versions

### AppImage

```bash
# Build the AppImage
./build_appimage.sh
```

This will create an AppImage file in the current directory that can be run on any compatible Linux system.

## Features in the Tray Application

- View currently playing track
- Toggle adaptive mode on/off
- Manually select EQ presets
- Easy access to quit the application

## Troubleshooting

If you encounter issues:

1. Check your Spotify API credentials
2. Make sure EasyEffects is installed and running
3. Verify EasyEffects presets exist with the correct names
4. Check system logs for any error messages

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/adaptive-eq.git
   cd adaptive-eq
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your Spotify API credentials:
   - Create an app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
   - Set the redirect URI to `http://127.0.0.1:8888/callback`
   - Export your credentials:
     ```bash
     export SPOTIFY_CLIENT_ID='your_client_id'
     export SPOTIFY_CLIENT_SECRET='your_client_secret'
     export SPOTIFY_REDIRECT_URI='http://127.0.0.1:8888/callback'
     ```

5. Make sure EasyEffects is installed and has some presets:
   ```bash
   sudo apt install easyeffects
   ```

## Usage

### Running as a background daemon

```bash
python main.py
```

### Running with system tray icon

```bash
python -m ui.tray
```

### Configuration

Edit `config/eq_profiles.json` to map artists to EQ presets.

Example:
```json
{
  "Daft Punk": "electronic",
  "Hans Zimmer": "orchestral",
  "Metallica": "rock"
}
```

### Using the playlist_to_eq.py Helper

The `playlist_to_eq.py` script helps you extract artists from your Spotify playlists and map them to EQ presets.

```bash
# Process a single playlist
./playlist_to_eq.py https://open.spotify.com/playlist/37i9dQZF1DX4dyzvaqLBqZ

# Process multiple playlists from a file
./playlist_to_eq.py --playlists playlists.txt

# Automatically map artists based on their genres
./playlist_to_eq.py --auto https://open.spotify.com/playlist/37i9dQZF1DX4dyzvaqLBqZ

# List all artists in your EQ profiles
./playlist_to_eq.py --list-artists
```

### Using the eq_helper.py Utility

The `eq_helper.py` utility provides additional functionality for managing and testing your EQ profiles.

```bash
# Test an EQ profile for a specific artist
./eq_helper.py test "Daft Punk"

# List artists grouped by EQ preset
./eq_helper.py list

# Monitor the current track and apply EQ presets (for 60 seconds)
./eq_helper.py monitor --duration 60

# Remove an artist from your EQ profiles
./eq_helper.py remove "Artist Name"
```

## Building Portable Versions

### AppImage (recommended)

```bash
# Install required tools
pip install pyinstaller

# Build single binary
pyinstaller --onefile --name adaptive-eq ui/tray.py

# Create AppDir structure
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

# Copy binary
cp dist/adaptive-eq AppDir/usr/bin/

# Create desktop file
cat > AppDir/usr/share/applications/adaptive-eq.desktop << EOF
[Desktop Entry]
Name=Adaptive EQ
Exec=adaptive-eq
Icon=adaptive-eq
Type=Application
Categories=Audio;Music;
EOF

# Copy icon (create your own icon.png first)
cp icon.png AppDir/usr/share/icons/hicolor/256x256/apps/adaptive-eq.png

# Build AppImage (requires appimagetool)
appimagetool AppDir
```

### Debian Package

```bash
# Install required tools
sudo apt install python3-stdeb dh-python

# Build the debian package
python setup.py --command-packages=stdeb.command bdist_deb
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
