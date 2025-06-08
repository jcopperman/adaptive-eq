#!/bin/bash

# Exit on error
set -e

echo "Building Adaptive EQ AppImage..."

# Source GTK dependency check function from check_dependencies.sh
echo "Checking GTK dependencies before building..."
if [ -f "check_dependencies.sh" ]; then
    source check_dependencies.sh
else
    echo "Warning: check_dependencies.sh not found. Skipping dependency check."
    echo "Make sure you have the required GTK dependencies installed:"
    echo "  - python3-gi or python-gobject"
    echo "  - python3-gi-cairo or python-cairo"
    echo "  - gir1.2-gtk-3.0 or gtk3"
    echo "  - gir1.2-appindicator3-0.1 or libappindicator-gtk3"
fi

# Make sure dependencies are installed
if ! command -v appimagetool &> /dev/null; then
    echo "appimagetool not found. Downloading..."
    wget -c "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" -O appimagetool
    chmod +x appimagetool
    sudo mv appimagetool /usr/local/bin/
fi

# Make sure PyInstaller is installed
if ! pip3 show pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

# Check if PyInstaller binary already exists
if [ -f "dist/adaptive-eq" ]; then
    echo "Using existing PyInstaller binary from dist/adaptive-eq"
else
    # Create a simple placeholder icon if it doesn't exist
    if [ ! -f "icon.png" ]; then
        echo "Creating placeholder icon..."
        convert -size 256x256 xc:none -fill "#3584e4" -draw "circle 128,128 128,20" \
                -pointsize 120 -gravity center -annotate 0 "EQ" icon.png || echo "Warning: Failed to create icon. Make sure ImageMagick is installed."
    fi

    # Build single binary with PyInstaller
    echo "Building application with PyInstaller..."
    pyinstaller --onefile --name adaptive-eq \
        --add-data "icon.png:." \
        --add-data "config:config" \
        --hidden-import=gi \
        --hidden-import=cairo \
        --hidden-import=spotipy \
        ui/tray.py
fi

# Create AppDir structure
echo "Creating AppDir structure..."
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
mkdir -p AppDir/usr/share/adaptive-eq/config
mkdir -p AppDir/usr/share/metainfo

# Copy files
echo "Copying application files..."
cp dist/adaptive-eq AppDir/usr/bin/
cp -r config/* AppDir/usr/share/adaptive-eq/config/
cp adaptive-eq.appdata.xml AppDir/usr/share/metainfo/

# Create a wrapper script to set up environment
cat > AppDir/usr/bin/adaptive-eq-wrapper << 'EOF'
#!/bin/bash
# Set up environment variables
export XDG_CONFIG_HOME="${HOME}/.config"
export PATH="${APPDIR}/usr/bin:${PATH}"
export PYTHONPATH="${APPDIR}/usr/lib/python3/dist-packages:${PYTHONPATH}"

# Check for Spotify credentials
if [ ! -f "${HOME}/.adaptive-eq-credentials" ]; then
    echo "Warning: Spotify credentials not found."
    echo "The application will not be able to connect to Spotify."
    echo ""
    echo "Would you like to configure Spotify credentials now? (y/n)"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo "Please enter your Spotify API Client ID:"
        read -r client_id
        echo "Please enter your Spotify API Client Secret:"
        read -r client_secret
        
        mkdir -p "${HOME}/.config/adaptive-eq"
        cat > "${HOME}/.adaptive-eq-credentials" << EOC
# Spotify API credentials
export SPOTIFY_CLIENT_ID='${client_id}'
export SPOTIFY_CLIENT_SECRET='${client_secret}'
export SPOTIFY_REDIRECT_URI='http://localhost:8888/callback'
EOC
        chmod 600 "${HOME}/.adaptive-eq-credentials"
        echo "Credentials saved to ${HOME}/.adaptive-eq-credentials"
        
        # Source the credentials for this session
        source "${HOME}/.adaptive-eq-credentials"
    fi
fi

# Run the application
exec "${APPDIR}/usr/bin/adaptive-eq" "$@"
EOF
chmod +x AppDir/usr/bin/adaptive-eq-wrapper

# Copy icon
cp icon.png AppDir/usr/share/icons/hicolor/256x256/apps/adaptive-eq.png
# Also copy to root for AppImage (required by appimagetool)
cp icon.png AppDir/adaptive-eq.png

# Create desktop file
cat > AppDir/adaptive-eq.desktop << EOF
[Desktop Entry]
Name=Adaptive EQ
Exec=adaptive-eq-wrapper
Icon=adaptive-eq
Type=Application
Categories=AudioVideo;Audio;Music;
EOF

# Also copy to the standard location for AppImage
cp AppDir/adaptive-eq.desktop AppDir/usr/share/applications/adaptive-eq.desktop

# Create AppRun script
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
# Export path to include our libraries
export APPDIR="$(dirname "$(readlink -f "$0")")"
export XDG_DATA_DIRS="${APPDIR}/usr/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"
export PATH="${APPDIR}/usr/bin:${PATH}"

# Check for required dependencies
check_dependency() {
    local pkg_name="$1"
    local import_cmd="$2"
    local install_instructions="$3"
    
    if ! python3 -c "$import_cmd" &>/dev/null; then
        echo "Error: $pkg_name is not installed."
        echo "Please install it with:"
        echo "$install_instructions"
        return 1
    fi
    return 0
}

# Check for PyGObject (GTK)
check_dependency "PyGObject" "import gi" \
    "  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1  # Debian/Ubuntu
  sudo dnf install python3-gobject python3-cairo gtk3 libappindicator-gtk3  # Fedora
  sudo pacman -Sy python-gobject python-cairo gtk3 libappindicator-gtk3  # Arch" || exit 1

# Check for AppIndicator3
check_dependency "AppIndicator3" "import gi; gi.require_version('AppIndicator3', '0.1'); from gi.repository import AppIndicator3" \
    "  sudo apt install gir1.2-appindicator3-0.1  # Debian/Ubuntu
  sudo dnf install libappindicator-gtk3  # Fedora
  sudo pacman -Sy libappindicator-gtk3  # Arch" || exit 1

# Check for EasyEffects (optional but recommended)
if ! command -v easyeffects &>/dev/null; then
    echo "Warning: EasyEffects is not installed."
    echo "This application requires EasyEffects to function properly."
    echo "Please install it with:"
    echo "  sudo apt install easyeffects  # Debian/Ubuntu"
    echo "  sudo dnf install easyeffects  # Fedora"
    echo "  sudo pacman -Sy easyeffects  # Arch"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create config directory if it doesn't exist
mkdir -p "${HOME}/.config/adaptive-eq"

# If this is the first run, copy the config files
if [ ! -f "${HOME}/.config/adaptive-eq/eq_profiles.json" ]; then
    mkdir -p "${HOME}/.config/adaptive-eq"
    cp -r "${APPDIR}/usr/share/adaptive-eq/config/"* "${HOME}/.config/adaptive-eq/"
fi

# Run the application
exec "${APPDIR}/usr/bin/adaptive-eq" "$@"
EOF
chmod +x AppDir/AppRun

# Build AppImage
echo "Building AppImage with appimagetool..."
ARCH=x86_64 appimagetool AppDir

echo "Build process completed! Your AppImage is ready."
echo "You can run it with: ./Adaptive_EQ-x86_64.AppImage"
