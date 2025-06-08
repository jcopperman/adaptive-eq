#!/bin/bash
# Run the Adaptive EQ CLI application with force-refresh enabled

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

# Activate the virtual environment
source system-venv/bin/activate

# Load Spotify credentials if they exist
if [ -f "$HOME/.adaptive-eq-credentials" ]; then
    source "$HOME/.adaptive-eq-credentials"
fi

# Run the application with force-refresh enabled
echo "Starting Adaptive EQ CLI with force UI refresh..."
python3 main.py --force-refresh

# Deactivate the virtual environment when done
deactivate
