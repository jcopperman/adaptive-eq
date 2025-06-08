# Adaptive EQ

An automatic equalizer adjustment tool for Linux audiophiles. This application automatically adjusts your EasyEffects equalizer settings based on what you're listening to in Spotify.

## Features

- **Automatic EQ Adjustment**: Detects the currently playing Spotify track and applies the appropriate EQ preset
- **Genre-Based EQ Profiles**: Maps artists to genre-specific EQ presets for optimal sound
- **System Tray Interface**: Convenient access to control and status information
- **Desktop Notifications**: Notifications when EQ presets are changed
- **Offline Support**: Caches track information for use when Spotify is offline
- **Portable**: Supports multiple Linux distributions and can be packaged as an AppImage
- **Easy Setup**: Automatic creation of EQ presets and simple configuration
- **Universal Installer**: Works across different Linux distributions
- **Robust Error Handling**: Comprehensive error handling and fallback mechanisms
- **Logging System**: Detailed logging for troubleshooting

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
  See the [GTK Dependencies Troubleshooting Guide](docs/gtk_dependencies.md) for more detailed information and solutions to common issues.

## Quick Installation

For the fastest installation:

```bash
# Clone repository
git clone https://github.com/jcopperman/adaptive-eq.git
cd adaptive-eq

# Run the universal installer script
./install.sh

# Or for a more manual approach:
# Run setup script - this installs all dependencies
./setup.sh

# Configure Spotify API credentials
./configure_spotify.py

# Create EQ presets for different music genres
./create_eq_presets.py --all

# Launch the app
./run.sh
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

### AppImage (recommended)

```bash
# Option 1: Run the build script (recommended)
./build_appimage.sh

# Option 2: Manual AppImage build
# Install required tools
pip install pyinstaller

# Build single binary first
pyinstaller --onefile --name adaptive-eq \
    --add-data "icon.png:." \
    --add-data "config:config" \
    --hidden-import=gi \
    --hidden-import=cairo \
    --hidden-import=spotipy \
    ui/tray.py

# Then build the AppImage manually
mkdir -p AppDir/usr/bin AppDir/usr/share/applications
cp dist/adaptive-eq AppDir/usr/bin/
cp adaptive-eq.desktop AppDir/usr/share/applications/
cp icon.png AppDir/
# ... etc.
```

This will create an AppImage file named `Adaptive_EQ-x86_64.AppImage` in the current directory.

### AppImage Dependencies

The AppImage will automatically check for required dependencies and guide users on installation if anything is missing. The primary dependencies are:

```bash
# For Debian/Ubuntu
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1

# For Fedora
sudo dnf install python3-gobject python3-cairo gtk3 libappindicator-gtk3

# For Arch Linux
sudo pacman -Sy python-gobject python-cairo gtk3 libappindicator-gtk3
```

### Troubleshooting AppImage

If you encounter issues with the AppImage:

1. Make sure it has execute permissions: `chmod +x Adaptive_EQ-x86_64.AppImage`
2. Run with debug output: `ADAPTIVE_EQ_LOG_LEVEL=debug ./Adaptive_EQ-x86_64.AppImage`
3. Check GTK dependencies as mentioned above
4. Check logs at `~/.cache/adaptive-eq/logs/`

### Universal Installer

For users who prefer a traditional installation, the universal installer script (`install.sh`) provides a more integrated experience:

```bash
# Run the installer
./install.sh
```

The installer:
- Detects your Linux distribution
- Installs all required dependencies
- Creates a Python virtual environment
- Configures Spotify credentials
- Creates desktop entries
- Sets up EQ presets
- Installs to `~/.local/share/adaptive-eq`

After installation, you can launch the application from your desktop environment or run:

```bash
~/.local/bin/adaptive-eq
```

To uninstall:

```bash
~/.local/share/adaptive-eq/uninstall.sh
```

## Troubleshooting

If you encounter issues:

1. **Check Dependencies**: Run `./check_dependencies.sh` to verify all required packages are installed
2. **Verify Spotify Credentials**: Make sure your Spotify API credentials are correctly set up
3. **EasyEffects Connection**: Ensure EasyEffects is installed and running
4. **Check Logs**: Examine logs in `~/.cache/adaptive-eq/logs/` for detailed error information
5. **Test Application**: Run `./quick_test.sh` to perform a comprehensive test of all components
6. **Permission Issues**: Ensure all scripts have executable permissions (`chmod +x *.sh`)
7. **Compatibility**: If using the AppImage, verify GTK dependencies on your system

### Common Issues

1. **"No module named 'gi'"**: Install PyGObject with:
   ```bash
   sudo apt install python3-gi python3-gi-cairo  # Debian/Ubuntu
   sudo dnf install python3-gobject python3-cairo  # Fedora
   sudo pacman -Sy python-gobject python-cairo  # Arch
   ```

2. **"AppIndicator3 not found"**: Install AppIndicator with:
   ```bash
   sudo apt install gir1.2-appindicator3-0.1  # Debian/Ubuntu
   sudo dnf install libappindicator-gtk3  # Fedora
   sudo pacman -Sy libappindicator-gtk3  # Arch
   ```

3. **"Cannot connect to Spotify"**: Check your credentials and internet connection. You can run:
   ```bash
   ./configure_spotify.py
   ```

4. **"Failed to apply EQ preset"**: Make sure EasyEffects is installed and running. Try:
   ```bash
   ./test_eq_presets.py --preset default
   ```

5. **AppImage issues**: If the AppImage fails to run, check if your system has the required GTK libraries:
   ```bash
   sudo apt install libgtk-3-0 libappindicator3-1  # Debian/Ubuntu
   ```

## Troubleshooting EasyEffects UI Issues

If you notice that EQ presets are applied (the sound changes) but the EasyEffects UI doesn't update to show the current preset, you can:

1. **Use the Force Refresh Feature**:
   - In the tray icon menu, click "Force EasyEffects Refresh"
   - When running the CLI version, use the force-refresh option:
     ```bash
     ./run_cli.sh
     ```
     or
     ```bash
     python3 main.py --force-refresh
     ```

2. **Run the Diagnostic Tool**:
   ```bash
   ./debug_easyeffects.py
   ```
   This will:
   - Check EasyEffects configuration
   - Test different preset application methods
   - Guide you through fixing UI refresh issues

3. **Common Fixes**:
   - Ensure EasyEffects is running before starting Adaptive EQ
   - Restart EasyEffects if UI sync issues persist
   - Check that `~/.config/easyeffects/config.json` exists and has proper permissions

The application now uses multiple methods to ensure presets are properly applied and visible in the UI, including:
- Using gsettings to set presets
- DBus interface communication
- Direct file updates
- Sending reload signals to EasyEffects

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
# Install required tools (if not already installed)
source system-venv/bin/activate  # Or your virtual environment
pip install pyinstaller

# Option 1: Build single binary first
pyinstaller --onefile --name adaptive-eq \
    --add-data "icon.png:." \
    --add-data "config:config" \
    --hidden-import=gi \
    --hidden-import=cairo \
    --hidden-import=spotipy \
    ui/tray.py

# Option 2: Use the build script to handle everything
./build_appimage.sh
```

This will create an AppImage file named `Adaptive_EQ-x86_64.AppImage` in the current directory.

> **Note**: The AppImage will still require the GTK libraries to be installed on the target system.
> Install these dependencies on the target system with:
> ```bash
> # For Debian/Ubuntu
> sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
> 
> # For Fedora
> sudo dnf install python3-gobject python3-cairo gtk3 libappindicator-gtk3
> 
> # For Arch Linux
> sudo pacman -Sy python-gobject python-cairo gtk3 libappindicator-gtk3
> ```

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
