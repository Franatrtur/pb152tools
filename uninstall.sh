#!/bin/bash

# Define the locations based on the installer
INSTALL_DIR="$HOME/.pb152tools"
BIN_DIR="$HOME/bin"
SYMLINK_PATH="$BIN_DIR/pb152tools"

echo "Uninstalling pb152tools..."

# 1. Remove the installation directory
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing application directory: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
else
    echo "Application directory not found. Skipping."
fi

# 2. Remove the symlinks
if [ -L "$SYMLINK_PATH" ]; then
    echo "Removing symlink: $SYMLINK_PATH"
    rm -f "$SYMLINK_PATH"
else
    echo "Symlink 'pb152tools' not found. Skipping."
fi

# Also remove the alias if it exists
ALIAS_PATH="$BIN_DIR/pb152cv"
if [ -L "$ALIAS_PATH" ]; then
    echo "Removing alias symlink: $ALIAS_PATH"
    rm -f "$ALIAS_PATH"
else
    echo "Alias 'pb152cv' not found. Skipping."
fi

echo "------------------------------------------------"
echo "Uninstallation Complete."
echo "If you have modified your PATH, you may need to manually revert the changes."
echo "------------------------------------------------"
