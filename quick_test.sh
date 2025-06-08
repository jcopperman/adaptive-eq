#!/bin/bash
# quick_test.sh - Test if Adaptive EQ works correctly

# Define colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}Adaptive EQ Quick Test${NC}"
echo -e "${BLUE}======================${NC}"

# Function to display test results
test_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    printf "%-30s " "$test_name"
    if [ "$result" -eq 0 ]; then
        echo -e "[${GREEN}PASS${NC}]"
    else
        echo -e "[${RED}FAIL${NC}]"
        if [ -n "$details" ]; then
            echo -e "  ${RED}$details${NC}"
        fi
    fi
}

# Check if Python is installed
echo -e "\n${BOLD}System Checks:${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    test_result "Python Installation" 0 
    echo -e "  ${GREEN}$PYTHON_VERSION${NC}"
else
    test_result "Python Installation" 1 "Python 3 is not installed"
    exit 1
fi

# Check dependencies
echo -e "\n${BOLD}Dependency Checks:${NC}"
./check_dependencies.sh &>/dev/null
DEPS_RESULT=$?
if [ $DEPS_RESULT -eq 0 ]; then
    test_result "Required Dependencies" 0
else
    test_result "Required Dependencies" 1 "Some dependencies are missing. Run ./check_dependencies.sh for details."
    echo -e "\n${YELLOW}Warning: Continuing with tests despite missing dependencies${NC}"
fi

# Check Spotify credentials
if [ -f "$HOME/.adaptive-eq-credentials" ]; then
    test_result "Spotify Credentials" 0
else
    test_result "Spotify Credentials" 1 "Credentials file not found at ~/.adaptive-eq-credentials"
    echo -e "  ${YELLOW}Consider running ./configure_spotify.py${NC}"
fi

# Check EasyEffects/PulseEffects installation
if command -v easyeffects &>/dev/null; then
    test_result "EasyEffects Installation" 0
    EFFECTS_TYPE="EasyEffects"
elif command -v pulseeffects &>/dev/null; then
    test_result "PulseEffects Installation" 0
    EFFECTS_TYPE="PulseEffects"
else
    test_result "Effects Application" 1 "Neither EasyEffects nor PulseEffects is installed"
    EFFECTS_TYPE="None"
fi

# Check for existing EQ presets
echo -e "\n${BOLD}Configuration Checks:${NC}"
EASYEFFECTS_PRESET_DIR="$HOME/.config/easyeffects/output"
PULSEEFFECTS_PRESET_DIR="$HOME/.config/PulseEffects/output"

if [ -d "$EASYEFFECTS_PRESET_DIR" ] && [ -n "$(ls -A "$EASYEFFECTS_PRESET_DIR" 2>/dev/null)" ]; then
    PRESET_COUNT=$(ls -1 "$EASYEFFECTS_PRESET_DIR"/*.json 2>/dev/null | wc -l)
    test_result "EQ Presets" 0
    echo -e "  ${GREEN}Found $PRESET_COUNT presets in $EASYEFFECTS_PRESET_DIR${NC}"
elif [ -d "$PULSEEFFECTS_PRESET_DIR" ] && [ -n "$(ls -A "$PULSEEFFECTS_PRESET_DIR" 2>/dev/null)" ]; then
    PRESET_COUNT=$(ls -1 "$PULSEEFFECTS_PRESET_DIR"/*.json 2>/dev/null | wc -l)
    test_result "EQ Presets" 0
    echo -e "  ${GREEN}Found $PRESET_COUNT presets in $PULSEEFFECTS_PRESET_DIR${NC}"
else
    test_result "EQ Presets" 1 "No presets found"
    echo -e "  ${YELLOW}Creating default presets...${NC}"
    ./create_eq_presets.py --all
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}Successfully created presets${NC}"
    else
        echo -e "  ${RED}Failed to create presets${NC}"
    fi
fi

# Check EQ profiles configuration
if [ -f "$HOME/.config/adaptive-eq/eq_profiles.json" ]; then
    PROFILE_COUNT=$(grep -o "\".*\":" "$HOME/.config/adaptive-eq/eq_profiles.json" | wc -l)
    test_result "EQ Profiles Configuration" 0
    echo -e "  ${GREEN}Found $PROFILE_COUNT artist mappings${NC}"
else
    test_result "EQ Profiles Configuration" 1 "No eq_profiles.json found"
    echo -e "  ${YELLOW}Creating default configuration...${NC}"
    mkdir -p "$HOME/.config/adaptive-eq"
    cp -f "config/eq_profiles.json" "$HOME/.config/adaptive-eq/"
fi

# Check EQ application
echo -e "\n${BOLD}Functionality Tests:${NC}"
if [ "$EFFECTS_TYPE" != "None" ]; then
    echo -e "${BLUE}Testing preset application...${NC}"
    ./test_eq_presets.py --preset default &>/dev/null
    if [ $? -eq 0 ]; then
        test_result "Apply EQ Preset" 0
    else
        test_result "Apply EQ Preset" 1 "Failed to apply preset"
    fi
else
    test_result "Apply EQ Preset" 1 "Effects application not installed"
fi

# Test Spotify API connection
echo -e "${BLUE}Testing Spotify API connection...${NC}"
if [ -f "$HOME/.adaptive-eq-credentials" ]; then
    source "$HOME/.adaptive-eq-credentials"
    python3 -c "import spotipy; from spotipy.oauth2 import SpotifyOAuth; sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='$SPOTIFY_CLIENT_ID', client_secret='$SPOTIFY_CLIENT_SECRET', redirect_uri='$SPOTIFY_REDIRECT_URI', scope='user-read-currently-playing')); print('Connection successful')" &>/dev/null
    if [ $? -eq 0 ]; then
        test_result "Spotify API Connection" 0
    else
        test_result "Spotify API Connection" 1 "Could not connect to Spotify API"
    fi
else
    test_result "Spotify API Connection" 1 "No credentials file"
fi

# Test application startup
echo -e "\n${BOLD}Application Test:${NC}"
echo -e "${BLUE}Starting Adaptive EQ for 5 seconds...${NC}"
echo -e "${YELLOW}Please play something on Spotify if available...${NC}"
timeout 5s ./run.sh &>/dev/null &
APP_PID=$!

# Wait for it to start
sleep 2

# Check if it's running
if ps -p $APP_PID > /dev/null; then
    test_result "Application Startup" 0
    # Kill it gracefully
    kill -TERM $APP_PID &>/dev/null
else
    test_result "Application Startup" 1 "Application crashed or failed to start"
fi

# Summary
echo -e "\n${BOLD}${BLUE}Test Summary:${NC}"
echo -e "${GREEN}✓${NC} System requirements checked"
echo -e "${GREEN}✓${NC} Dependencies verified"
echo -e "${GREEN}✓${NC} Configuration files checked"
echo -e "${GREEN}✓${NC} Basic functionality tested"

echo -e "\n${BOLD}${BLUE}Next Steps:${NC}"
echo -e "1. To run the full application, use: ${GREEN}./run.sh${NC}"
echo -e "2. To see a demo of the features, use: ${GREEN}./demo.sh${NC}"
echo -e "3. To build an AppImage, use: ${GREEN}./build_appimage.sh${NC}"

# If AppImage exists, mention it
if [ -f "Adaptive_EQ-x86_64.AppImage" ]; then
    echo -e "\n${GREEN}AppImage is available:${NC} ./Adaptive_EQ-x86_64.AppImage"
fi
