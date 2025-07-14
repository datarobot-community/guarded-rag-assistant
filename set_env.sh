#!/bin/bash

# Function to check if script is sourced
check_if_sourced() {
    if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
        echo "Please run this script using 'source' or '.' like this:"
        echo "  source ${0}"
        echo "  . ${0}"
        return 1
    fi
}

# Function to load .env file
load_env_file() {
    if [ ! -f .env ]; then
        echo "Error: .env file not found."
        echo "Please create a .env file with VAR_NAME=value pairs."
        return 1
    fi
    set -a
    source .env
    set +a
    echo "Environment variables from .env have been set."
}

# Function to activate the virtual environment if it exists
activate_virtual_environment() {
    if [ -f .venv/bin/activate ]; then
        echo "Activated virtual environment found at .venv/bin/activate"
        source .venv/bin/activate
    fi
}

# Main execution
if check_if_sourced ; then
    load_env_file
    activate_virtual_environment
fi
