#!/bin/bash

# Function to update requirements.txt
update_requirements() {
    echo "Updating requirements.txt..."
    pip freeze > ../backend-gateway/requirements.txt
    echo "requirements.txt has been updated!"
}

# Main script
if [ "$1" = "install" ]; then
    # Run pip install with all arguments passed to this script
    pip "$@"
    
    # If pip install was successful, update requirements.txt
    if [ $? -eq 0 ]; then
        update_requirements
    fi
else
    # For all other pip commands, just pass through
    pip "$@"
fi