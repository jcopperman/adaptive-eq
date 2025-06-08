#!/bin/bash
# demo.sh - Demonstrates the Adaptive EQ functionality

# Set up colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}Adaptive EQ Demo Script${NC}"
echo -e "${BLUE}=========================================${NC}"

# Path to the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

# Check if setup has been run
if [ ! -d "system-venv" ]; then
    echo -e "${YELLOW}It looks like the setup script hasn't been run yet.${NC}"
    echo -e "Running ${GREEN}./setup.sh${NC} first..."
    ./setup.sh
fi

# Activate virtual environment
source system-venv/bin/activate

# Check if Spotify credentials are configured
if [ ! -f ~/.adaptive-eq-credentials ]; then
    echo -e "${RED}Error: Spotify credentials not configured.${NC}"
    echo -e "Please run ${YELLOW}./configure_spotify.py${NC} first."
    exit 1
fi

# Load Spotify credentials
source ~/.adaptive-eq-credentials

# Check if EasyEffects is installed
if ! command -v easyeffects &> /dev/null; then
    echo -e "${RED}Error: EasyEffects is not installed.${NC}"
    echo -e "Please install EasyEffects first."
    exit 1
fi

# Make sure our scripts are executable
chmod +x playlist_to_eq.py eq_helper.py create_eq_presets.py configure_spotify.py test_eq_presets.py

# Check if we have any EQ presets
if [ ! -d ~/.config/easyeffects/output ] || [ -z "$(ls -A ~/.config/easyeffects/output)" ]; then
    echo -e "\n${YELLOW}Creating EQ presets for different music genres...${NC}"
    ./create_eq_presets.py --all
fi

# 1. Show current EQ profiles
echo -e "\n${YELLOW}Current EQ profiles:${NC}"
./eq_helper.py list

# 2. Monitor current track
echo -e "\n${YELLOW}Monitoring current track for 30 seconds...${NC}"
echo -e "Please play a song on Spotify to see the automatic EQ adjustment in action."
./eq_helper.py monitor --duration 30

# 3. Show example of playlist extraction
echo -e "\n${YELLOW}Would you like to extract artists from a Spotify playlist? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}Enter a Spotify playlist URL:${NC}"
    read playlist_url
    if [[ $playlist_url == *"spotify.com/playlist/"* ]]; then
        echo -e "\n${YELLOW}Extracting artists from playlist...${NC}"
        ./playlist_to_eq.py "$playlist_url"
    else
        echo -e "${RED}Invalid Spotify playlist URL.${NC}"
    fi
fi

# 4. Test EQ presets
echo -e "\n${YELLOW}Would you like to test EQ preset application? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}Testing EQ presets...${NC}"
    ./test_eq_presets.py --all --delay 3
fi

# 5. Launch the application
echo -e "\n${YELLOW}Would you like to launch the Adaptive EQ application now? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}Launching Adaptive EQ...${NC}"
    ./run.sh &
    echo -e "${GREEN}Application is now running in your system tray.${NC}"
    echo -e "You can close this terminal window."
    exit 0
fi

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Demo completed!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo
echo -e "To start the Adaptive EQ application, run: ${YELLOW}./run.sh${NC}"
echo

# Deactivate virtual environment
deactivate
