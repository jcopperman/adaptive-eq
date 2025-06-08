#!/bin/bash

# This script installs the required dependencies for Adaptive EQ

set -e

echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 easyeffects

echo "Installing Python dependencies..."
# Check if we're in a virtual environment
if python3 -c "import sys; sys.exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)"; then
    pip3 install spotipy
else
    pip3 install --user spotipy
fi

echo "Dependencies installed successfully!"

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

echo "Setup complete! You can now run the application with ./run_tray.sh"
