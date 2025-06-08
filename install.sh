#!/bin/bash
# install.sh - Universal installer for Adaptive EQ
# This script detects the Linux distribution, installs dependencies, and sets up the application

set -e

# Define colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Application info
APP_NAME="Adaptive EQ"
VERSION="0.2.0"
INSTALL_DIR="$HOME/.local/share/adaptive-eq"
BIN_DIR="$HOME/.local/bin"

echo -e "${BOLD}${BLUE}=== $APP_NAME Installer (v$VERSION) ===${NC}"
echo -e "This script will install $APP_NAME and set up all required components."

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
    echo -e "${YELLOW}Could not detect Linux distribution. Will use generic installation process.${NC}"
fi

# Get package manager install command
get_install_command() {
    case $DISTRO in
        "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
            echo "sudo apt install -y"
            ;;
        "fedora"|"rhel"|"centos"|"rocky"|"alma")
            echo "sudo dnf install -y"
            ;;
        "arch"|"manjaro"|"endeavouros")
            echo "sudo pacman -S --noconfirm"
            ;;
        "opensuse"|"sles")
            echo "sudo zypper install -y"
            ;;
        *)
            echo "sudo apt install -y"
            ;;
    esac
}

# Get package names for dependencies
get_package_names() {
    local package_type="$1"
    
    case $package_type in
        "python")
            case $DISTRO in
                "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
                    echo "python3 python3-pip python3-venv"
                    ;;
                "fedora"|"rhel"|"centos"|"rocky"|"alma")
                    echo "python3 python3-pip python3-virtualenv"
                    ;;
                "arch"|"manjaro"|"endeavouros")
                    echo "python python-pip python-virtualenv"
                    ;;
                *)
                    echo "python3 python3-pip python3-venv"
                    ;;
            esac
            ;;
        "gtk")
            case $DISTRO in
                "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
                    echo "python3-gi python3-gi-cairo gir1.2-gtk-3.0"
                    ;;
                "fedora"|"rhel"|"centos"|"rocky"|"alma")
                    echo "python3-gobject python3-cairo gtk3"
                    ;;
                "arch"|"manjaro"|"endeavouros")
                    echo "python-gobject python-cairo gtk3"
                    ;;
                *)
                    echo "python3-gi python3-gi-cairo gir1.2-gtk-3.0"
                    ;;
            esac
            ;;
        "appindicator")
            case $DISTRO in
                "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
                    echo "gir1.2-appindicator3-0.1"
                    ;;
                "fedora"|"rhel"|"centos"|"rocky"|"alma")
                    echo "libappindicator-gtk3"
                    ;;
                "arch"|"manjaro"|"endeavouros")
                    echo "libappindicator-gtk3"
                    ;;
                *)
                    echo "gir1.2-appindicator3-0.1"
                    ;;
            esac
            ;;
        "easyeffects")
            case $DISTRO in
                "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary"|"zorin")
                    if [[ "${DISTRO_VERSION%%.*}" -lt 22 ]]; then
                        echo "pulseeffects"
                    else
                        echo "easyeffects"
                    fi
                    ;;
                "fedora"|"rhel"|"centos"|"rocky"|"alma")
                    echo "easyeffects"
                    ;;
                "arch"|"manjaro"|"endeavouros")
                    echo "easyeffects"
                    ;;
                *)
                    echo "easyeffects"
                    ;;
            esac
            ;;
    esac
}

# Check if user has sudo privileges
check_sudo() {
    if sudo -v &>/dev/null; then
        echo -e "${GREEN}✓ Sudo privileges available${NC}"
        return 0
    else
        echo -e "${RED}✗ No sudo privileges. Some installation steps may fail.${NC}"
        return 1
    fi
}

# Install system dependencies
install_system_dependencies() {
    echo -e "\n${BLUE}Installing system dependencies...${NC}"
    
    local install_cmd=$(get_install_command)
    local python_pkgs=$(get_package_names "python")
    local gtk_pkgs=$(get_package_names "gtk")
    local appindicator_pkgs=$(get_package_names "appindicator")
    
    echo -e "Installing Python packages: ${YELLOW}$python_pkgs${NC}"
    $install_cmd $python_pkgs || {
        echo -e "${RED}Failed to install Python. Please install manually:${NC}"
        echo -e "${BLUE}$install_cmd $python_pkgs${NC}"
        exit 1
    }
    
    echo -e "Installing GTK packages: ${YELLOW}$gtk_pkgs${NC}"
    $install_cmd $gtk_pkgs || {
        echo -e "${RED}Failed to install GTK packages. Please install manually:${NC}"
        echo -e "${BLUE}$install_cmd $gtk_pkgs${NC}"
    }
    
    echo -e "Installing AppIndicator packages: ${YELLOW}$appindicator_pkgs${NC}"
    $install_cmd $appindicator_pkgs || {
        echo -e "${RED}Failed to install AppIndicator packages. Please install manually:${NC}"
        echo -e "${BLUE}$install_cmd $appindicator_pkgs${NC}"
    }
    
    # Ask about EasyEffects installation
    local easyeffects_pkgs=$(get_package_names "easyeffects")
    echo -e "\n${YELLOW}EasyEffects is required for this application to function properly.${NC}"
    read -p "Would you like to install EasyEffects now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "Installing EasyEffects: ${YELLOW}$easyeffects_pkgs${NC}"
        $install_cmd $easyeffects_pkgs || {
            echo -e "${RED}Failed to install EasyEffects. Please install manually:${NC}"
            echo -e "${BLUE}$install_cmd $easyeffects_pkgs${NC}"
        }
    fi
}

# Create a Python virtual environment
create_virtual_env() {
    echo -e "\n${BLUE}Setting up Python virtual environment...${NC}"
    
    # Create venv directory
    mkdir -p "$INSTALL_DIR"
    
    # Create virtual environment
    python3 -m venv "$INSTALL_DIR/venv" || {
        echo -e "${RED}Failed to create virtual environment. Trying alternative method...${NC}"
        # Try virtualenv as fallback
        pip3 install virtualenv
        virtualenv "$INSTALL_DIR/venv" || {
            echo -e "${RED}Failed to create virtual environment. Please check your Python installation.${NC}"
            exit 1
        }
    }
    
    echo -e "${GREEN}✓ Created virtual environment at $INSTALL_DIR/venv${NC}"
}

# Install Python dependencies
install_python_dependencies() {
    echo -e "\n${BLUE}Installing Python dependencies...${NC}"
    
    # Activate virtual environment
    source "$INSTALL_DIR/venv/bin/activate"
    
    # Install dependencies
    pip install --upgrade pip
    pip install spotipy
    
    # Copy requirements.txt and install
    cp requirements.txt "$INSTALL_DIR/"
    pip install -r requirements.txt
    
    echo -e "${GREEN}✓ Installed Python dependencies${NC}"
}

# Copy application files
copy_application_files() {
    echo -e "\n${BLUE}Copying application files...${NC}"
    
    # Create directories
    mkdir -p "$INSTALL_DIR/config"
    mkdir -p "$INSTALL_DIR/services"
    mkdir -p "$INSTALL_DIR/ui"
    mkdir -p "$HOME/.config/adaptive-eq"
    mkdir -p "$BIN_DIR"
    
    # Copy files
    cp -r services/* "$INSTALL_DIR/services/"
    cp -r ui/* "$INSTALL_DIR/ui/"
    cp -r config/* "$INSTALL_DIR/config/"
    cp icon.png "$INSTALL_DIR/"
    cp create_eq_presets.py "$INSTALL_DIR/"
    cp configure_spotify.py "$INSTALL_DIR/"
    cp playlist_to_eq.py "$INSTALL_DIR/"
    cp eq_helper.py "$INSTALL_DIR/"
    
    # Copy config to user config directory
    if [ ! -f "$HOME/.config/adaptive-eq/eq_profiles.json" ]; then
        cp -r config/* "$HOME/.config/adaptive-eq/"
    else
        echo -e "${YELLOW}Config files already exist in $HOME/.config/adaptive-eq/ - keeping existing files${NC}"
    fi
    
    echo -e "${GREEN}✓ Copied application files to $INSTALL_DIR${NC}"
}

# Create launcher script
create_launcher() {
    echo -e "\n${BLUE}Creating launcher script...${NC}"
    
    cat > "$INSTALL_DIR/adaptive-eq-launcher" << EOF
#!/bin/bash
# Launcher script for Adaptive EQ

# Activate the virtual environment
source "$INSTALL_DIR/venv/bin/activate"

# Check dependencies
python3 "$INSTALL_DIR/services/dependency_check.py" || {
    echo "Dependency check failed. Please check the error messages above."
    read -p "Press any key to continue anyway..." -n1
    echo
}

# Run the application
exec python3 -m ui.tray
EOF
    
    chmod +x "$INSTALL_DIR/adaptive-eq-launcher"
    
    # Create symlink in ~/.local/bin
    ln -sf "$INSTALL_DIR/adaptive-eq-launcher" "$BIN_DIR/adaptive-eq"
    
    echo -e "${GREEN}✓ Created launcher script at $BIN_DIR/adaptive-eq${NC}"
}

# Create dependency checker script
create_dependency_checker() {
    echo -e "\n${BLUE}Creating dependency checker...${NC}"
    
    cat > "$INSTALL_DIR/services/dependency_check.py" << 'EOF'
#!/usr/bin/env python3
"""
Dependency checker for Adaptive EQ
Verifies that all required dependencies are installed
"""

import sys
import subprocess
import os
import importlib.util

def check_module(module_name):
    """Check if a Python module is available"""
    return importlib.util.find_spec(module_name) is not None

def check_command(command):
    """Check if a command is available in PATH"""
    try:
        subprocess.run([command, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False

def main():
    """Main dependency checking function"""
    errors = []
    
    # Check Python modules
    required_modules = {
        "gi": "PyGObject (GTK)",
        "spotipy": "Spotipy",
        "json": "JSON",
        "os": "OS",
        "sys": "System",
        "time": "Time",
        "threading": "Threading"
    }
    
    print("Checking Python modules:")
    for module, name in required_modules.items():
        if check_module(module):
            print(f"  ✓ {name} is installed")
        else:
            print(f"  ✗ {name} is not installed")
            errors.append(f"Missing Python module: {module}")
    
    # Check GTK and AppIndicator
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import Gtk, AppIndicator3
        print("  ✓ GTK and AppIndicator3 are installed")
    except ImportError as e:
        print(f"  ✗ GTK or AppIndicator3 not properly installed: {e}")
        errors.append("Missing GTK dependencies")
        
        # Provide system-specific installation instructions
        echo -e "\nTo install GTK dependencies:"
        if [[ "$DISTRO" == "ubuntu" || "$DISTRO" == "debian" || "$DISTRO" == "pop" || "$DISTRO" == "elementary" || "$DISTRO" == "mint" || "$DISTRO" == "zorin" ]]; then
            echo "  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1"
        elif [[ "$DISTRO" == "fedora" || "$DISTRO" == "rhel" || "$DISTRO" == "centos" ]]; then
            echo "  sudo dnf install python3-gobject python3-cairo gtk3 libappindicator-gtk3"
        elif [[ "$DISTRO" == "arch" || "$DISTRO" == "manjaro" || "$DISTRO" == "endeavouros" ]]; then
            echo "  sudo pacman -S python-gobject python-cairo gtk3 libappindicator-gtk3"
        else
            echo "  Please check the documentation for installing PyGObject and AppIndicator3 on your system"
            echo "  See: https://pygobject.readthedocs.io/en/latest/getting_started.html"
        fi
            
        # Note about virtual environments
        echo -e "\nNote: If you're using a virtual environment, you may need to install these dependencies system-wide,"
        echo "      or ensure your virtual environment can access the system packages."
        echo "      For more information, see: docs/gtk_dependencies.md"
    except Exception as e:
        print(f"  ✗ Error checking GTK dependencies: {e}")
        errors.append(f"GTK dependency check error: {e}")
    
    # Check EasyEffects/PulseEffects
    print("\nChecking system dependencies:")
    if check_command("easyeffects"):
        print("  ✓ EasyEffects is installed")
    elif check_command("pulseeffects"):
        print("  ✓ PulseEffects is installed (compatible with EasyEffects)")
    else:
        print("  ✗ Neither EasyEffects nor PulseEffects is installed")
        errors.append("Missing EasyEffects/PulseEffects")
    
    # Check for Spotify credentials
    creds_file = os.path.expanduser("~/.adaptive-eq-credentials")
    if os.path.exists(creds_file):
        print("  ✓ Spotify credentials file exists")
    else:
        print("  ✗ Spotify credentials file not found")
        errors.append("Missing Spotify credentials file (~/.adaptive-eq-credentials)")
    
    # Report results
    if errors:
        print("\nThe following issues were found:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix these issues before running the application.")
        return 1
    
    print("\nAll dependencies are satisfied!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF
    
    echo -e "${GREEN}✓ Created dependency checker script${NC}"
}

# Create desktop entry
create_desktop_entry() {
    echo -e "\n${BLUE}Creating desktop entry...${NC}"
    
    mkdir -p "$HOME/.local/share/applications"
    
    cat > "$HOME/.local/share/applications/adaptive-eq.desktop" << EOF
[Desktop Entry]
Name=Adaptive EQ
Comment=Automatically adjusts EasyEffects equalizer settings based on Spotify music
Exec=$BIN_DIR/adaptive-eq
Icon=$INSTALL_DIR/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Music;
Keywords=spotify;equalizer;audio;sound;music;
EOF
    
    echo -e "${GREEN}✓ Created desktop entry${NC}"
}

# Create uninstaller
create_uninstaller() {
    echo -e "\n${BLUE}Creating uninstaller...${NC}"
    
    cat > "$INSTALL_DIR/uninstall.sh" << EOF
#!/bin/bash
# Uninstaller for Adaptive EQ

echo "Uninstalling Adaptive EQ..."

# Remove symlink
rm -f "$BIN_DIR/adaptive-eq"

# Remove desktop entry
rm -f "$HOME/.local/share/applications/adaptive-eq.desktop"

# Ask about removing configuration
read -p "Do you want to remove configuration files? (y/N) " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$HOME/.config/adaptive-eq"
    rm -f "$HOME/.adaptive-eq-credentials"
    rm -rf "$HOME/.cache/adaptive-eq"
    echo "Configuration files removed."
else
    echo "Configuration files preserved."
fi

# Remove installation directory
rm -rf "$INSTALL_DIR"

echo "Adaptive EQ has been uninstalled."
EOF
    
    chmod +x "$INSTALL_DIR/uninstall.sh"
    
    echo -e "${GREEN}✓ Created uninstaller script at $INSTALL_DIR/uninstall.sh${NC}"
}

# Configure Spotify credentials
configure_spotify() {
    echo -e "\n${BLUE}Configuring Spotify credentials...${NC}"
    
    if [ -f "$HOME/.adaptive-eq-credentials" ]; then
        echo -e "${YELLOW}Spotify credentials file already exists at $HOME/.adaptive-eq-credentials${NC}"
        read -p "Do you want to reconfigure Spotify credentials? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    echo -e "${YELLOW}You need to create a Spotify application to use this app.${NC}"
    echo -e "1. Go to ${BLUE}https://developer.spotify.com/dashboard/applications${NC}"
    echo -e "2. Create a new application"
    echo -e "3. Set the redirect URI to ${BLUE}http://localhost:8888/callback${NC}"
    echo -e "4. Note your Client ID and Client Secret"
    echo
    
    read -p "Do you have your Spotify API credentials ready? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}You can configure Spotify credentials later by running:${NC}"
        echo -e "${BLUE}$BIN_DIR/adaptive-eq-configure-spotify${NC}"
        return
    fi
    
    read -p "Enter your Spotify Client ID: " client_id
    read -p "Enter your Spotify Client Secret: " client_secret
    
    # Create credentials file
    cat > "$HOME/.adaptive-eq-credentials" << EOF
# Spotify API credentials
export SPOTIFY_CLIENT_ID='$client_id'
export SPOTIFY_CLIENT_SECRET='$client_secret'
export SPOTIFY_REDIRECT_URI='http://localhost:8888/callback'
EOF
    
    chmod 600 "$HOME/.adaptive-eq-credentials"
    
    echo -e "${GREEN}✓ Spotify credentials configured${NC}"
}

# Create configuration script
create_spotify_config_script() {
    echo -e "\n${BLUE}Creating Spotify configuration script...${NC}"
    
    cat > "$INSTALL_DIR/adaptive-eq-configure-spotify" << EOF
#!/bin/bash
# Configure Spotify credentials

# Activate virtual environment
source "$INSTALL_DIR/venv/bin/activate"

# Run configure_spotify.py
python3 "$INSTALL_DIR/configure_spotify.py"
EOF
    
    chmod +x "$INSTALL_DIR/adaptive-eq-configure-spotify"
    
    # Create symlink in ~/.local/bin
    ln -sf "$INSTALL_DIR/adaptive-eq-configure-spotify" "$BIN_DIR/adaptive-eq-configure-spotify"
    
    echo -e "${GREEN}✓ Created Spotify configuration script at $BIN_DIR/adaptive-eq-configure-spotify${NC}"
}

# Create EQ presets
create_eq_presets() {
    echo -e "\n${BLUE}Creating EQ presets...${NC}"
    
    # Check if EasyEffects/PulseEffects is installed
    if command -v easyeffects &>/dev/null || command -v pulseeffects &>/dev/null; then
        echo -e "${YELLOW}Would you like to create EQ presets for different music genres? (Y/n)${NC}"
        read -p "" -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            # Activate virtual environment
            source "$INSTALL_DIR/venv/bin/activate"
            
            # Run create_eq_presets.py
            python3 "$INSTALL_DIR/create_eq_presets.py" --all
            
            echo -e "${GREEN}✓ Created EQ presets${NC}"
        else
            echo -e "${YELLOW}Skipping EQ preset creation. You can create them later with:${NC}"
            echo -e "${BLUE}$BIN_DIR/adaptive-eq-create-presets${NC}"
        fi
    else
        echo -e "${YELLOW}EasyEffects/PulseEffects is not installed. Skipping EQ preset creation.${NC}"
        echo -e "${YELLOW}You can create them later after installing EasyEffects/PulseEffects with:${NC}"
        echo -e "${BLUE}$BIN_DIR/adaptive-eq-create-presets${NC}"
    fi
}

# Create presets script
create_presets_script() {
    echo -e "\n${BLUE}Creating EQ presets script...${NC}"
    
    cat > "$INSTALL_DIR/adaptive-eq-create-presets" << EOF
#!/bin/bash
# Create EQ presets

# Activate virtual environment
source "$INSTALL_DIR/venv/bin/activate"

# Run create_eq_presets.py
python3 "$INSTALL_DIR/create_eq_presets.py" --all
EOF
    
    chmod +x "$INSTALL_DIR/adaptive-eq-create-presets"
    
    # Create symlink in ~/.local/bin
    ln -sf "$INSTALL_DIR/adaptive-eq-create-presets" "$BIN_DIR/adaptive-eq-create-presets"
    
    echo -e "${GREEN}✓ Created EQ presets script at $BIN_DIR/adaptive-eq-create-presets${NC}"
}

# Run the installation
echo -e "\n${BLUE}=== Starting installation ===${NC}\n"

# Check for sudo access
check_sudo

# Install system dependencies
install_system_dependencies

# Create virtual environment
create_virtual_env

# Install Python dependencies
install_python_dependencies

# Copy application files
copy_application_files

# Create launcher script
create_launcher

# Create dependency checker
create_dependency_checker

# Create desktop entry
create_desktop_entry

# Create uninstaller
create_uninstaller

# Create Spotify configuration script
create_spotify_config_script

# Create presets script
create_presets_script

# Configure Spotify credentials
configure_spotify

# Create EQ presets
create_eq_presets

echo -e "\n${GREEN}${BOLD}=== Installation Complete! ===${NC}"
echo -e "You can now launch Adaptive EQ from your applications menu"
echo -e "or by running: ${BLUE}$BIN_DIR/adaptive-eq${NC}"
echo -e "\nTo uninstall, run: ${BLUE}$INSTALL_DIR/uninstall.sh${NC}"

# Ask if user wants to run the application now
echo -e "\n${YELLOW}Would you like to start Adaptive EQ now? (Y/n)${NC}"
read -p "" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo -e "Starting Adaptive EQ..."
    "$BIN_DIR/adaptive-eq"
fi
