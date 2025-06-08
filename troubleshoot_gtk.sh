#!/bin/bash
# troubleshoot_gtk.sh - Script to diagnose and fix GTK-related issues

# Define colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}===== Adaptive EQ GTK Troubleshooter =====${NC}\n"
echo -e "This script will help diagnose and fix GTK-related issues with Adaptive EQ."
echo -e "It will check for missing dependencies and suggest solutions.\n"

# Detect Linux distribution
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

# Check Python version
echo -e "\n${BLUE}${BOLD}Checking Python version:${NC}"
PYTHON_VERSION=$(python3 --version)
echo -e "Python version: ${GREEN}$PYTHON_VERSION${NC}"

# Check if running in virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "\n${BLUE}${BOLD}Running in virtual environment:${NC} ${GREEN}$VIRTUAL_ENV${NC}"
    
    # Check if virtual environment has system packages
    echo -e "\n${BLUE}${BOLD}Testing virtual environment access to system packages:${NC}"
    if python3 -c "import sys; print('System site-packages enabled' if any('site-packages' in p for p in sys.path) else 'System site-packages disabled')" | grep -q "enabled"; then
        echo -e "${GREEN}✓ Virtual environment has access to system site-packages${NC}"
    else
        echo -e "${RED}✗ Virtual environment does not have access to system site-packages${NC}"
        echo -e "${YELLOW}You may need to recreate your virtual environment with the --system-site-packages flag:${NC}"
        echo -e "  deactivate"
        echo -e "  rm -rf $VIRTUAL_ENV"
        echo -e "  python3 -m venv $VIRTUAL_ENV --system-site-packages"
    fi
else
    echo -e "\n${BLUE}${BOLD}Not running in a virtual environment${NC}"
fi

# Check for PyGObject
echo -e "\n${BLUE}${BOLD}Checking for PyGObject (GTK bindings):${NC}"
if python3 -c "import gi" 2>/dev/null; then
    echo -e "${GREEN}✓ PyGObject is installed${NC}"
    
    # Check GTK version
    if python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print(f'GTK version: {Gtk._version}')" 2>/dev/null; then
        echo -e "${GREEN}✓ GTK 3.0 is properly installed${NC}"
    else
        echo -e "${RED}✗ GTK 3.0 is not properly installed${NC}"
        echo -e "${YELLOW}Installing GTK 3.0 libraries...${NC}"
        case $DISTRO in
            "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
                sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
                ;;
            "fedora"|"rhel"|"centos"|"rocky"|"alma")
                sudo dnf install -y python3-gobject python3-cairo gtk3
                ;;
            "arch"|"manjaro"|"endeavouros")
                sudo pacman -Sy python-gobject python-cairo gtk3
                ;;
            *)
                echo -e "${RED}Could not install GTK automatically. Please install manually.${NC}"
                echo -e "See docs/gtk_dependencies.md for instructions."
                ;;
        esac
    fi
else
    echo -e "${RED}✗ PyGObject is not installed${NC}"
    echo -e "${YELLOW}Installing PyGObject...${NC}"
    case $DISTRO in
        "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
            sudo apt-get install -y python3-gi python3-gi-cairo
            ;;
        "fedora"|"rhel"|"centos"|"rocky"|"alma")
            sudo dnf install -y python3-gobject python3-cairo
            ;;
        "arch"|"manjaro"|"endeavouros")
            sudo pacman -Sy python-gobject python-cairo
            ;;
        *)
            echo -e "${RED}Could not install PyGObject automatically. Please install manually.${NC}"
            echo -e "See docs/gtk_dependencies.md for instructions."
            ;;
    esac
fi

# Check for AppIndicator3
echo -e "\n${BLUE}${BOLD}Checking for AppIndicator3:${NC}"
if python3 -c "import gi; gi.require_version('AppIndicator3', '0.1'); from gi.repository import AppIndicator3" 2>/dev/null; then
    echo -e "${GREEN}✓ AppIndicator3 is installed${NC}"
else
    echo -e "${RED}✗ AppIndicator3 is not installed${NC}"
    echo -e "${YELLOW}Installing AppIndicator3...${NC}"
    case $DISTRO in
        "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
            sudo apt-get install -y gir1.2-appindicator3-0.1
            ;;
        "fedora"|"rhel"|"centos"|"rocky"|"alma")
            sudo dnf install -y libappindicator-gtk3
            ;;
        "arch"|"manjaro"|"endeavouros")
            sudo pacman -Sy libappindicator-gtk3
            ;;
        *)
            echo -e "${RED}Could not install AppIndicator3 automatically. Please install manually.${NC}"
            echo -e "See docs/gtk_dependencies.md for instructions."
            ;;
    esac
fi

# Check X11/Wayland environment
echo -e "\n${BLUE}${BOLD}Checking display server:${NC}"
if [ -n "$WAYLAND_DISPLAY" ]; then
    echo -e "Running on ${GREEN}Wayland${NC} (WAYLAND_DISPLAY=$WAYLAND_DISPLAY)"
    echo -e "${YELLOW}Note: Some older GTK applications may have issues with Wayland.${NC}"
elif [ -n "$DISPLAY" ]; then
    echo -e "Running on ${GREEN}X11${NC} (DISPLAY=$DISPLAY)"
else
    echo -e "${RED}No display server detected. GTK applications require a display server.${NC}"
    echo -e "${YELLOW}Are you running in a headless environment or via SSH without X forwarding?${NC}"
fi

# Final verification
echo -e "\n${BLUE}${BOLD}Running final verification tests:${NC}"
echo -e "${YELLOW}Testing GTK import...${NC}"
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK import successful')" || echo -e "${RED}GTK import failed${NC}"

echo -e "${YELLOW}Testing AppIndicator3 import...${NC}"
python3 -c "import gi; gi.require_version('AppIndicator3', '0.1'); from gi.repository import AppIndicator3; print('AppIndicator3 import successful')" || echo -e "${RED}AppIndicator3 import failed${NC}"

echo -e "\n${BLUE}${BOLD}Troubleshooting complete!${NC}"
echo -e "If you're still experiencing issues, please check the troubleshooting guide:"
echo -e "${GREEN}docs/gtk_dependencies.md${NC}"
echo -e "Or report the issue on GitHub with the output of this script."
