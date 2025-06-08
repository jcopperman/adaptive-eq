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

# Check if Spotify credentials are configured
if [ ! -f ~/.adaptive-eq-credentials ]; then
    echo -e "${RED}Error: Spotify credentials not configured.${NC}"
    echo -e "Please run ${YELLOW}./configure_spotify.py${NC} first."
    exit 1
fi

# Check if EasyEffects is installed
if ! command -v easyeffects &> /dev/null; then
    echo -e "${RED}Error: EasyEffects is not installed.${NC}"
    echo -e "Please install EasyEffects first."
    exit 1
fi

# Make sure our scripts are executable
chmod +x playlist_to_eq.py eq_helper.py

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

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Demo completed!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo
echo -e "To start the Adaptive EQ application, run: ${YELLOW}./adaptive-eq-launcher${NC}"
echo
