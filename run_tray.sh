#!/bin/bash

# This script launches the Adaptive EQ tray application using Python virtual environment
# which has the required packages installed

# Change to project directory
cd "$(dirname "$0")"

# Source the common dependency check function from run.sh
source_run_sh() {
    # Extract the dependency check function from run.sh
    grep -A 150 "check_gtk_deps()" run.sh | grep -B 150 "All GTK dependencies are installed" > /tmp/check_deps.sh
    source /tmp/check_deps.sh
    rm /tmp/check_deps.sh
}

# If run.sh exists, source it to get the dependency check function
if [ -f "run.sh" ]; then
    source_run_sh
    # Run the dependency check
    check_gtk_deps
else
    echo "Warning: run.sh not found. Skipping dependency check."
fi

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
