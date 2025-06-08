#!/bin/bash

# This script installs the required dependencies for Adaptive EQ
# and sets up the environment

set -e

echo "====================================="
echo "Adaptive EQ Setup"
echo "====================================="

# Create virtual environment if it doesn't exist
if [ ! -d "system-venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv system-venv
fi

# Activate virtual environment
source system-venv/bin/activate

echo "Installing system dependencies..."
if [ -f /etc/debian_version ]; then
    # Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 easyeffects
elif [ -f /etc/fedora-release ]; then
    # Fedora
    sudo dnf install -y python3-gobject python3-cairo gtk3 libappindicator-gtk3 easyeffects
elif [ -f /etc/arch-release ]; then
    # Arch Linux
    sudo pacman -Sy python-gobject python-cairo gtk3 libappindicator-gtk3 easyeffects
else
    echo "Warning: Unsupported distribution. Please install the required packages manually:"
    echo "- Python3 GTK3 bindings (python3-gi/python-gobject)"
    echo "- Cairo bindings (python3-cairo/python-cairo)"
    echo "- GTK3 libraries (gtk3)"
    echo "- AppIndicator libraries (libappindicator-gtk3)"
    echo "- EasyEffects"
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Dependencies installed successfully!"

echo "Setting up configuration directories..."
mkdir -p ~/.config/adaptive-eq
mkdir -p ~/.cache/adaptive-eq

# Create Spotify credentials file template if it doesn't exist
echo "Creating Spotify credentials file template..."
if [ ! -f "$HOME/.adaptive-eq-credentials" ]; then
    cat > "$HOME/.adaptive-eq-credentials" << EOF
# Set your Spotify API credentials here
export SPOTIFY_CLIENT_ID='your_client_id'
export SPOTIFY_CLIENT_SECRET='your_client_secret'
export SPOTIFY_REDIRECT_URI='http://localhost:8888/callback'
EOF
    echo "Created $HOME/.adaptive-eq-credentials"
    echo "Please edit this file to add your Spotify API credentials."
else
    echo "Credentials file already exists at $HOME/.adaptive-eq-credentials"
fi

# Copy default configuration if it doesn't exist
if [ ! -f "$HOME/.config/adaptive-eq/eq_profiles.json" ] && [ -f "config/eq_profiles.json" ]; then
    echo "Copying default EQ profiles..."
    cp config/eq_profiles.json "$HOME/.config/adaptive-eq/"
fi

# Create desktop file for easy launching
echo "Creating desktop file..."
mkdir -p ~/.local/share/applications/
cat > ~/.local/share/applications/adaptive-eq.desktop << EOF
[Desktop Entry]
Name=Adaptive EQ
Comment=Automatically adjusts EQ based on music
Exec=$(pwd)/run_tray.sh
Icon=$(pwd)/icon.png
Terminal=false
Type=Application
Categories=Audio;Music;Utility;
StartupNotify=true
EOF

# Make the launcher scripts executable
chmod +x run_tray.sh adaptive-eq-launcher

echo "====================================="
echo "Setup complete!"
echo "You can now run the application with:"
echo "./run_tray.sh"
echo ""
echo "Or from your applications menu."
echo "====================================="

# Prompt for Spotify configuration
echo ""
read -p "Would you like to configure Spotify API credentials now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./configure_spotify.py
fi

# Prompt to create EQ presets
echo ""
read -p "Would you like to create EQ presets now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./create_eq_presets.py --all
fi
