#!/bin/bash

# This script launches the Adaptive EQ tray application using Python virtual environment
# which has the required packages installed

# Change to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source system-venv/bin/activate

# Export Spotify API credentials if provided as environment variables
if [ -f "$HOME/.adaptive-eq-credentials" ]; then
    source "$HOME/.adaptive-eq-credentials"
fi

# Run the application
python3 ui/tray.py

# Deactivate virtual environment at exit
deactivate
