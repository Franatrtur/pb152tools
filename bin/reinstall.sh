#!/bin/bash

# --- CWD Sanity Check ---
# Abort if the current working directory has been deleted while the user was in it.
if ! pwd > /dev/null 2>&1; then
    echo "Error: The current working directory is invalid or has been deleted."
    echo "Please 'cd' to a valid directory and run the update again."
    exit 1
fi

echo "Starting Veryfi reinstallation..."
echo "This will uninstall and reinstall the application."

read -p "Are you sure you want to update? This will fetch the latest version from GitHub. (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Update cancelled."
    exit 1
fi

# Define locations and the source repository
INSTALL_DIR="$HOME/.veryfi"

# --- Sanity Check ---
# Ensure the installation directory exists before we try to update.
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Error: Veryfi installation directory not found at $INSTALL_DIR."
    echo "Nothing to update. Please run the installer if you want to install veryfi."
    exit 1
fi

source "$INSTALL_DIR/repo.conf"

# --- Run the uninstaller to clean up the old version ---
echo
echo "--> Step 1 of 3: Uninstalling the current version..."
if [ -f "$INSTALL_DIR/uninstall.sh" ]; then
    bash "$INSTALL_DIR/uninstall.sh"
else
    echo "Uninstall script not found. Attempting to remove directories manually..."
    rm -rf "$INSTALL_DIR"
    rm -f "$HOME/bin/veryfi"
    rm -f "$HOME/bin/pb152cv"
fi
echo "--> Uninstallation complete."

# --- Clone the latest version from GitHub ---
echo
echo "--> Step 2 of 3: Cloning the latest version from GitHub..."
CLONE_DIR=$(mktemp -d /tmp/veryfi-reinstall.XXXXXX)

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "!!! FATAL: 'git' is not installed. Cannot proceed with the reinstallation."
    exit 1
fi

git clone --depth 1 "$REPO_URL" "$CLONE_DIR"
if [ ! -f "$CLONE_DIR/install.sh" ]; then
    echo "!!! FATAL: Reinstallation failed. Could not clone the repository from $REPO_URL."
    rm -rf "$CLONE_DIR"
    exit 1
fi
echo "--> Successfully cloned."

# --- Run the installer from the new version ---
echo
echo "--> Step 3 of 3: Running the new installer..."
# The -p flag on mkdir is gone, install.sh should handle it
bash "$CLONE_DIR/install.sh"

# The new installer will self-destruct the CLONE_DIR, so no extra cleanup is needed.
echo
echo "------------------------------------------------"
echo "Reinstallation process complete."
echo "------------------------------------------------"
