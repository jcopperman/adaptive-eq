#!/bin/bash
# check_dependencies.sh - Check for required dependencies before running the application

# Define colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Adaptive EQ Dependency Checker ===${NC}"

# Detect the Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    DISTRO_VERSION=$VERSION_ID
    echo -e "Detected distribution: ${GREEN}$DISTRO $DISTRO_VERSION${NC}"
elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    DISTRO=$DISTRIB_ID
    DISTRO_VERSION=$DISTRIB_VERSION
    echo -e "Detected distribution: ${GREEN}$DISTRO $DISTRO_VERSION${NC}"
elif [ -f /etc/arch-release ]; then
    DISTRO="arch"
    echo -e "Detected distribution: ${GREEN}Arch Linux${NC}"
elif [ -f /etc/fedora-release ]; then
    DISTRO="fedora"
    echo -e "Detected distribution: ${GREEN}Fedora${NC}"
else
    DISTRO="unknown"
    echo -e "${YELLOW}Could not detect Linux distribution. Will use generic checks.${NC}"
fi

# Initialize array to store missing dependencies
MISSING_DEPS=()

# Check for python3-gi
if ! python3 -c "import gi" &>/dev/null; then
    echo -e "${RED}Error: python3-gi (PyGObject) is not installed.${NC}"
    echo -e "Please install it with:"
    echo -e "${BLUE}  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1  # Debian/Ubuntu${NC}"
    echo -e "${BLUE}  sudo dnf install python3-gobject python3-cairo gtk3 libappindicator-gtk3  # Fedora${NC}"
    echo -e "${BLUE}  sudo pacman -Sy python-gobject python-cairo gtk3 libappindicator-gtk3  # Arch${NC}"
    
    # Add to missing dependencies based on distro
    case $DISTRO in
        "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
            MISSING_DEPS+=("python3-gi python3-gi-cairo gir1.2-gtk-3.0|sudo apt install")
            ;;
        "fedora"|"rhel"|"centos"|"rocky"|"alma")
            MISSING_DEPS+=("python3-gobject python3-cairo gtk3|sudo dnf install")
            ;;
        "arch"|"manjaro"|"endeavouros")
            MISSING_DEPS+=("python-gobject python-cairo gtk3|sudo pacman -Sy")
            ;;
        *)
            MISSING_DEPS+=("python-gi python-gi-cairo gtk3|package-manager")
            ;;
    esac
else
    echo -e "${GREEN}✓ PyGObject (GTK) is installed${NC}"
fi

# Check for AppIndicator3
if ! python3 -c "import gi; gi.require_version('AppIndicator3', '0.1'); from gi.repository import AppIndicator3" &>/dev/null; then
    echo -e "${RED}Error: AppIndicator3 is not installed or not available.${NC}"
    echo -e "Please install it with:"
    echo -e "${BLUE}  sudo apt install gir1.2-appindicator3-0.1  # Debian/Ubuntu${NC}"
    echo -e "${BLUE}  sudo dnf install libappindicator-gtk3  # Fedora${NC}"
    echo -e "${BLUE}  sudo pacman -Sy libappindicator-gtk3  # Arch${NC}"
    
    # Add to missing dependencies based on distro
    case $DISTRO in
        "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
            MISSING_DEPS+=("gir1.2-appindicator3-0.1|sudo apt install")
            ;;
        "fedora"|"rhel"|"centos"|"rocky"|"alma")
            MISSING_DEPS+=("libappindicator-gtk3|sudo dnf install")
            ;;
        "arch"|"manjaro"|"endeavouros")
            MISSING_DEPS+=("libappindicator-gtk3|sudo pacman -Sy")
            ;;
        *)
            MISSING_DEPS+=("libappindicator-gtk3|package-manager")
            ;;
    esac
else
    echo -e "${GREEN}✓ AppIndicator3 is installed${NC}"
fi

# Check for EasyEffects
if ! command -v easyeffects &>/dev/null; then
    echo -e "${YELLOW}Warning: EasyEffects is not installed.${NC}"
    echo -e "This application requires EasyEffects to function properly."
    echo -e "Please install it with:"
    echo -e "${BLUE}  sudo apt install easyeffects  # Debian/Ubuntu${NC}"
    echo -e "${BLUE}  sudo dnf install easyeffects  # Fedora${NC}"
    echo -e "${BLUE}  sudo pacman -Sy easyeffects  # Arch${NC}"
    echo ""
    
    # Special handling for older Ubuntu/Debian that use PulseEffects instead of EasyEffects
    if [[ "$DISTRO" == "ubuntu" || "$DISTRO" == "debian" ]] && [[ "${DISTRO_VERSION%%.*}" -lt 22 ]]; then
        echo -e "${YELLOW}Note: Your distribution may use PulseEffects instead of EasyEffects.${NC}"
        echo -e "${BLUE}  sudo apt install pulseeffects  # Older Debian/Ubuntu${NC}"
        
        # Check if PulseEffects is installed
        if command -v pulseeffects &>/dev/null; then
            echo -e "${GREEN}✓ PulseEffects is installed, which is compatible${NC}"
        else
            MISSING_DEPS+=("pulseeffects|sudo apt install")
        fi
    else
        # Add to missing dependencies based on distro
        case $DISTRO in
            "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
                MISSING_DEPS+=("easyeffects|sudo apt install")
                ;;
            "fedora"|"rhel"|"centos"|"rocky"|"alma")
                MISSING_DEPS+=("easyeffects|sudo dnf install")
                ;;
            "arch"|"manjaro"|"endeavouros")
                MISSING_DEPS+=("easyeffects|sudo pacman -Sy")
                ;;
            *)
                MISSING_DEPS+=("easyeffects|package-manager")
                ;;
        esac
    fi
    
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ EasyEffects is installed${NC}"
fi

# Check for Python spotipy module
if ! python3 -c "import spotipy" &>/dev/null; then
    echo -e "${YELLOW}Warning: Python spotipy module is not installed.${NC}"
    echo -e "Please install it with: ${BLUE}pip install spotipy${NC}"
    MISSING_DEPS+=("spotipy|pip install")
else
    echo -e "${GREEN}✓ Python spotipy module is installed${NC}"
fi

# Display summary of missing dependencies
if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo -e "\n${GREEN}All required dependencies are installed!${NC}"
    echo -e "${GREEN}You can run the application now.${NC}"
    exit 0
else
    echo -e "\n${YELLOW}Missing dependencies:${NC}"
    
    # Group missing dependencies by installation command
    declare -A grouped_deps
    for dep in "${MISSING_DEPS[@]}"; do
        IFS='|' read -r pkg_name install_cmd <<< "$dep"
        if [[ -n "${grouped_deps[$install_cmd]}" ]]; then
            grouped_deps[$install_cmd]="${grouped_deps[$install_cmd]} $pkg_name"
        else
            grouped_deps[$install_cmd]="$pkg_name"
        fi
    done
    
    # Display grouped dependencies
    for cmd in "${!grouped_deps[@]}"; do
        echo -e "${BLUE}$cmd ${grouped_deps[$cmd]}${NC}"
    done
    
    # Ask if user wants to install missing dependencies
    echo -e "\n${YELLOW}Would you like to install the missing dependencies automatically? [y/N]${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "\n${BLUE}Installing missing dependencies...${NC}"
        
        # Install grouped dependencies
        for cmd in "${!grouped_deps[@]}"; do
            echo -e "${BLUE}Running: $cmd ${grouped_deps[$cmd]}${NC}"
            $cmd ${grouped_deps[$cmd]} || {
                echo -e "${RED}Failed to install some dependencies. You may need to install them manually.${NC}"
                exit 1
            }
        done
        
        echo -e "\n${GREEN}All dependencies have been installed. You can run the application now.${NC}"
    else
        echo -e "${YELLOW}Please install the missing dependencies manually using the commands above.${NC}"
        exit 1
    fi
fi
