#!/bin/bash

# Exit on error
set -e

echo "Building Adaptive EQ AppImage..."

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

# Create AppDir structure
echo "Creating AppDir structure..."
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
mkdir -p AppDir/usr/share/adaptive-eq/config

# Copy files
echo "Copying application files..."
cp dist/adaptive-eq AppDir/usr/bin/
cp -r config/* AppDir/usr/share/adaptive-eq/config/

# Create a wrapper script to set up environment
cat > AppDir/usr/bin/adaptive-eq-wrapper << 'EOF'
#!/bin/bash
# Set up environment variables
export XDG_CONFIG_HOME="${HOME}/.config"
export PATH="${APPDIR}/usr/bin:${PATH}"
export PYTHONPATH="${APPDIR}/usr/lib/python3/dist-packages:${PYTHONPATH}"

# Run the application
exec "${APPDIR}/usr/bin/adaptive-eq" "$@"
EOF
chmod +x AppDir/usr/bin/adaptive-eq-wrapper

# Copy icon
cp icon.png AppDir/usr/share/icons/hicolor/256x256/apps/adaptive-eq.png

# Create desktop file
cat > AppDir/usr/share/applications/adaptive-eq.desktop << EOF
[Desktop Entry]
Name=Adaptive EQ
Exec=adaptive-eq-wrapper
Icon=adaptive-eq
Type=Application
Categories=Audio;Music;
EOF

# Create AppRun script
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
# Export path to include our libraries
export APPDIR="$(dirname "$(readlink -f "$0")")"
export XDG_DATA_DIRS="${APPDIR}/usr/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"
export PATH="${APPDIR}/usr/bin:${PATH}"

# Create config directory if it doesn't exist
mkdir -p "${HOME}/.config/adaptive-eq"

# If this is the first run, copy the config files
if [ ! -f "${HOME}/.config/adaptive-eq/eq_profiles.json" ]; then
    mkdir -p "${HOME}/.config/adaptive-eq"
    cp -r "${APPDIR}/usr/share/adaptive-eq/config/"* "${HOME}/.config/adaptive-eq/"
fi

# Run the application
exec "${APPDIR}/usr/bin/adaptive-eq-wrapper" "$@"
EOF
chmod +x AppDir/AppRun

# Build AppImage
echo "Building AppImage with appimagetool..."
ARCH=x86_64 appimagetool AppDir

echo "Build process completed! Your AppImage is ready."
echo "You can run it with: ./Adaptive_EQ-x86_64.AppImage"
