#!/bin/bash

# This script installs the required dependencies for Adaptive EQ
# and sets up the environment

set -e

# Define colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Adaptive EQ Setup${NC}"
echo -e "${BLUE}=====================================${NC}"

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    echo -e "Detected distribution: ${GREEN}$DISTRO${NC}"
elif [ -f /etc/debian_version ]; then
    DISTRO="debian"
    echo -e "Detected distribution: ${GREEN}Debian-based${NC}"
elif [ -f /etc/fedora-release ]; then
    DISTRO="fedora"
    echo -e "Detected distribution: ${GREEN}Fedora${NC}"
elif [ -f /etc/arch-release ]; then
    DISTRO="arch"
    echo -e "Detected distribution: ${GREEN}Arch Linux${NC}"
else
    DISTRO="unknown"
    echo -e "${YELLOW}Could not detect Linux distribution. Will use generic installation process.${NC}"
fi

# Install GTK dependencies
echo -e "${BLUE}Installing system dependencies...${NC}"
case $DISTRO in
    "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
        echo -e "Installing dependencies for ${GREEN}Debian/Ubuntu-based${NC} system..."
        sudo apt-get update
        sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 easyeffects
        ;;
    "fedora"|"rhel"|"centos"|"rocky"|"alma")
        echo -e "Installing dependencies for ${GREEN}Fedora/RHEL-based${NC} system..."
        sudo dnf install -y python3-gobject python3-cairo gtk3 libappindicator-gtk3 easyeffects
        ;;
    "arch"|"manjaro"|"endeavouros")
        echo -e "Installing dependencies for ${GREEN}Arch-based${NC} system..."
        sudo pacman -Sy python-gobject python-cairo gtk3 libappindicator-gtk3 easyeffects
        ;;
    *)
        echo -e "${YELLOW}Warning: Unsupported distribution. Please install the required packages manually:${NC}"
        echo -e "- Python3 GTK3 bindings (python3-gi/python-gobject)"
        echo -e "- Cairo bindings (python3-cairo/python-cairo)"
        echo -e "- GTK3 libraries (gtk3)"
        echo -e "- AppIndicator libraries (libappindicator-gtk3)"
        echo -e "- EasyEffects"
        echo -e "\nSee docs/gtk_dependencies.md for more information."
        ;;
esac

# Create virtual environment with system packages
if [ ! -d "system-venv" ]; then
    echo -e "${BLUE}Creating Python virtual environment with system packages...${NC}"
    python3 -m venv system-venv --system-site-packages
else
    echo -e "${YELLOW}Virtual environment already exists. Checking if it has system packages access...${NC}"
    # Test if the virtual environment can access system packages
    if source system-venv/bin/activate && ! python3 -c "import gi" &>/dev/null; then
        echo -e "${RED}Virtual environment does not have access to system packages.${NC}"
        echo -e "${YELLOW}Would you like to recreate it with system packages access? (y/n)${NC}"
        read -r recreate
        if [[ "$recreate" =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}Recreating virtual environment with system packages...${NC}"
            rm -rf system-venv
            python3 -m venv system-venv --system-site-packages
        else
            echo -e "${YELLOW}Continuing with current virtual environment. GTK may not work correctly.${NC}"
            echo -e "See docs/gtk_dependencies.md for troubleshooting information."
        fi
    fi
fi

# Activate virtual environment
source system-venv/bin/activate

echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}Dependencies installed successfully!${NC}"

# Verify GTK dependencies
echo -e "${BLUE}Verifying GTK dependencies...${NC}"
if python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK is installed')" &>/dev/null; then
    echo -e "${GREEN}✓ GTK is properly installed and accessible${NC}"
else
    echo -e "${RED}✗ GTK is not properly installed or not accessible${NC}"
    echo -e "${YELLOW}Please check the GTK dependencies troubleshooting guide: docs/gtk_dependencies.md${NC}"
fi

if python3 -c "import gi; gi.require_version('AppIndicator3', '0.1'); from gi.repository import AppIndicator3; print('AppIndicator3 is installed')" &>/dev/null; then
    echo -e "${GREEN}✓ AppIndicator3 is properly installed and accessible${NC}"
else
    echo -e "${RED}✗ AppIndicator3 is not properly installed or not accessible${NC}"
    echo -e "${YELLOW}Please check the GTK dependencies troubleshooting guide: docs/gtk_dependencies.md${NC}"
fi

echo -e "${BLUE}Setting up configuration directories...${NC}"
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

echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo "You can now run the application with:"
echo "./run_tray.sh"
echo ""
echo "Or from your applications menu."
echo -e "${BLUE}=====================================${NC}"

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
