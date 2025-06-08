#!/bin/bash
# Run the Adaptive EQ application

# Path to the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

# Check if setup has been run
if [ ! -d "system-venv" ]; then
    echo "It looks like the setup script hasn't been run yet."
    echo "Would you like to run it now? (y/n)"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        ./setup.sh
    else
        echo "Setup is required to run the application. Exiting."
        exit 1
    fi
fi

# Check if the virtual environment has system-site-packages enabled
if [ -d "system-venv" ]; then
    # Recreate the environment with system packages if needed
    if source system-venv/bin/activate && ! python3 -c "import gi" &>/dev/null; then
        echo -e "${YELLOW}Virtual environment doesn't have access to system packages.${NC}"
        echo -e "${BLUE}Recreating virtual environment with system-site-packages...${NC}"
        deactivate
        rm -rf system-venv
        python3 -m venv system-venv --system-site-packages
        echo -e "${GREEN}Virtual environment recreated with system packages access.${NC}"
    fi
fi

# Activate the virtual environment
source system-venv/bin/activate

# Check for required GTK dependencies
check_gtk_deps() {
    # Define colors for better readability
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color

    echo -e "${BLUE}Checking GTK dependencies...${NC}"
    
    # Try to import gi module
    if ! python3 -c "import gi" &>/dev/null; then
        echo -e "${RED}Error: Python GTK bindings (PyGObject) are not installed or not accessible in the virtual environment.${NC}"
        
        # First, check if the package is installed at the system level
        if python3 -c "import sys; sys.path = [p for p in sys.path if 'site-packages' in p]; import gi" &>/dev/null; then
            echo -e "${YELLOW}PyGObject is installed at the system level but not accessible in the virtual environment.${NC}"
            echo -e "${YELLOW}Would you like to recreate the virtual environment with system-site-packages? (y/n)${NC}"
            read -r recreate_venv
            
            if [[ "$recreate_venv" =~ ^[Yy]$ ]]; then
                echo -e "${BLUE}Recreating virtual environment with system-site-packages...${NC}"
                rm -rf system-venv
                python3 -m venv system-venv --system-site-packages
                source system-venv/bin/activate
                pip install -r requirements.txt
                echo -e "${GREEN}Virtual environment recreated with system packages access.${NC}"
                # Check again
                if ! python3 -c "import gi" &>/dev/null; then
                    echo -e "${RED}Still unable to import GTK modules. Please try running ./troubleshoot_gtk.sh${NC}"
                    exit 1
                else
                    echo -e "${GREEN}PyGObject is now accessible!${NC}"
                    return 0
                fi
            fi
        fi
        
        # If we get here, either the user didn't want to recreate the venv or the packages aren't installed
        echo -e "${YELLOW}Would you like to install the required dependencies now? (y/n)${NC}"
        read -r install_deps
        
        if [[ "$install_deps" =~ ^[Yy]$ ]]; then
            # Detect distribution
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                DISTRO=$ID
            else
                echo -e "${RED}Could not determine your Linux distribution.${NC}"
                echo -e "${YELLOW}Please install the GTK dependencies manually:${NC}"
                echo -e "  Debian/Ubuntu: ${BLUE}sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1${NC}"
                echo -e "  Fedora: ${BLUE}sudo dnf install python3-gobject python3-cairo gtk3 libappindicator-gtk3${NC}"
                echo -e "  Arch Linux: ${BLUE}sudo pacman -Sy python-gobject python-cairo gtk3 libappindicator-gtk3${NC}"
                echo -e "\nFor more detailed help, run: ${BLUE}./troubleshoot_gtk.sh${NC}"
                echo -e "Or see: ${BLUE}docs/gtk_dependencies.md${NC}"
                return 1
            fi
            
            case $DISTRO in
                ubuntu|debian|pop|mint|linuxmint|elementary|zorin)
                    echo -e "${BLUE}Installing dependencies for Debian/Ubuntu-based distribution...${NC}"
                    sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
                    ;;
                fedora|centos|rhel)
                    echo -e "${BLUE}Installing dependencies for Fedora/RHEL-based distribution...${NC}"
                    sudo dnf install -y python3-gobject python3-cairo gtk3 libappindicator-gtk3
                    ;;
                arch|manjaro|endeavouros)
                    echo -e "${BLUE}Installing dependencies for Arch-based distribution...${NC}"
                    sudo pacman -Sy --noconfirm python-gobject python-cairo gtk3 libappindicator-gtk3
                    ;;
                *)
                    echo -e "${RED}Unsupported distribution: $DISTRO${NC}"
                    echo -e "${YELLOW}Please install the GTK dependencies manually:${NC}"
                    echo -e "  Debian/Ubuntu: ${BLUE}sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1${NC}"
                    echo -e "  Fedora: ${BLUE}sudo dnf install python3-gobject python3-cairo gtk3 libappindicator-gtk3${NC}"
                    echo -e "  Arch Linux: ${BLUE}sudo pacman -Sy python-gobject python-cairo gtk3 libappindicator-gtk3${NC}"
                    echo -e "\nFor more detailed help, run: ${BLUE}./troubleshoot_gtk.sh${NC}"
                    echo -e "Or see: ${BLUE}docs/gtk_dependencies.md${NC}"
                    exit 1
                    ;;
            esac
            
            # Check if installation was successful
            if ! python3 -c "import gi" &>/dev/null; then
                echo -e "${RED}Installation failed. Please install the dependencies manually.${NC}"
                exit 1
            else
                echo -e "${GREEN}Dependencies installed successfully!${NC}"
            fi
        else
            echo -e "${RED}Required dependencies not installed. Exiting.${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}PyGObject is installed.${NC}"
    fi
    
    # Check for AppIndicator support
    if ! python3 -c "import gi; gi.require_version('AppIndicator3', '0.1'); from gi.repository import AppIndicator3" &>/dev/null; then
        echo -e "${RED}Error: AppIndicator3 module is not installed.${NC}"
        echo -e "${YELLOW}Would you like to install it now? (y/n)${NC}"
        read -r install_appindicator
        
        if [[ "$install_appindicator" =~ ^[Yy]$ ]]; then
            # Detect distribution
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                DISTRO=$ID
            else
                echo -e "${RED}Could not determine your Linux distribution.${NC}"
                echo -e "${YELLOW}Please install AppIndicator3 manually:${NC}"
                echo -e "  Debian/Ubuntu: ${BLUE}sudo apt install gir1.2-appindicator3-0.1${NC}"
                echo -e "  Fedora: ${BLUE}sudo dnf install libappindicator-gtk3${NC}"
                echo -e "  Arch Linux: ${BLUE}sudo pacman -Sy libappindicator-gtk3${NC}"
                exit 1
            fi
            
            case $DISTRO in
                ubuntu|debian|pop|mint|elementary|zorin)
                    echo -e "${BLUE}Installing AppIndicator3 for Debian/Ubuntu-based distribution...${NC}"
                    sudo apt install -y gir1.2-appindicator3-0.1
                    ;;
                fedora|centos|rhel)
                    echo -e "${BLUE}Installing AppIndicator3 for Fedora/RHEL-based distribution...${NC}"
                    sudo dnf install -y libappindicator-gtk3
                    ;;
                arch|manjaro|endeavouros)
                    echo -e "${BLUE}Installing AppIndicator3 for Arch-based distribution...${NC}"
                    sudo pacman -Sy --noconfirm libappindicator-gtk3
                    ;;
                *)
                    echo -e "${RED}Unsupported distribution: $DISTRO${NC}"
                    echo -e "${YELLOW}Please install AppIndicator3 manually:${NC}"
                    echo -e "  Debian/Ubuntu: ${BLUE}sudo apt install gir1.2-appindicator3-0.1${NC}"
                    echo -e "  Fedora: ${BLUE}sudo dnf install libappindicator-gtk3${NC}"
                    echo -e "  Arch Linux: ${BLUE}sudo pacman -Sy libappindicator-gtk3${NC}"
                    exit 1
                    ;;
            esac
            
            # Check if installation was successful
            if ! python3 -c "import gi; gi.require_version('AppIndicator3', '0.1'); from gi.repository import AppIndicator3" &>/dev/null; then
                echo -e "${RED}Installation failed. Please install AppIndicator3 manually.${NC}"
                exit 1
            else
                echo -e "${GREEN}AppIndicator3 installed successfully!${NC}"
            fi
        else
            echo -e "${RED}Required dependencies not installed. Exiting.${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}AppIndicator3 is installed.${NC}"
    fi
    
    echo -e "${GREEN}All GTK dependencies are installed!${NC}"
}

# Run the dependency check
check_gtk_deps

# Load Spotify credentials if they exist
if [ -f "$HOME/.adaptive-eq-credentials" ]; then
    source "$HOME/.adaptive-eq-credentials"
fi

# Run the application
echo "Starting Adaptive EQ..."
python3 ui/tray.py

# Deactivate the virtual environment when done
deactivate
