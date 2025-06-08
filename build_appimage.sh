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

# Create a simple placeholder icon if it doesn't exist
if [ ! -f "icon.png" ]; then
    echo "Creating placeholder icon..."
    convert -size 256x256 xc:none -fill "#3584e4" -draw "circle 128,128 128,20" \
            -pointsize 120 -gravity center -annotate 0 "EQ" icon.png || echo "Warning: Failed to create icon. Make sure ImageMagick is installed."
fi

# Create AppDir structure
echo "Creating AppDir structure..."
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/lib/python3/dist-packages
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

# Copy files
echo "Copying application files..."
cp -r services AppDir/usr/lib/python3/
cp -r ui AppDir/usr/lib/python3/
cp -r config AppDir/usr/
cp adaptive-eq-launcher AppDir/usr/bin/
chmod +x AppDir/usr/bin/adaptive-eq-launcher

# Copy icon
cp icon.png AppDir/usr/share/icons/hicolor/256x256/apps/adaptive-eq.png

# Create desktop file
cat > AppDir/usr/share/applications/adaptive-eq.desktop << EOF
[Desktop Entry]
Name=Adaptive EQ
Exec=adaptive-eq-launcher
Icon=adaptive-eq
Type=Application
Categories=Audio;Music;
EOF

# Create AppRun script
cat > AppDir/AppRun << EOF
#!/bin/bash
# Export path to include our libraries
export LD_LIBRARY_PATH="\${APPDIR}/usr/lib:\${LD_LIBRARY_PATH}"
export PYTHONPATH="\${APPDIR}/usr/lib/python3:\${PYTHONPATH}"

# Run the application
"\${APPDIR}/usr/bin/adaptive-eq-launcher"
EOF
chmod +x AppDir/AppRun

# Build AppImage
echo "Building AppImage with appimagetool..."
appimagetool AppDir

echo "Build process completed!"
