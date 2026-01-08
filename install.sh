#!/bin/bash

# Define the "Permanent Home" for the app
INSTALL_DIR="$HOME/.veryfi"
BIN_DIR="$HOME/bin"

echo "Installing Veryfi to $INSTALL_DIR..."

# 1. Clean Slate (Optional: removes old version to ensure clean update)
# If you want to be safer, only remove if it exists.
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing previous installation..."
    rm -rf "$INSTALL_DIR"
fi

# 2. Create the directory
mkdir -p "$INSTALL_DIR"

# 3. Copy the source files from the CURRENT folder to the INSTALL folder
# We assume the user is running this script from inside the downloaded repo
cp -r src "$INSTALL_DIR/"
cp -r bin "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"

# COPY ASSETS
cp -r assets "$INSTALL_DIR/"

# 4. Create the Isolated Venv (Inside the install dir)
echo "Creating isolated virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

# 5. Install Dependencies (Inside the venv)
echo "Installing dependencies (google-generativeai)..."
# We pipe to /dev/null to keep it looking clean, unless it errors
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" > /dev/null

# 6. Make executable
chmod +x "$INSTALL_DIR/bin/veryfi"

# 7. Symlink
mkdir -p "$BIN_DIR"
# Remove old link if exists
rm -f "$BIN_DIR/veryfi"
# Create new link
ln -s "$INSTALL_DIR/bin/veryfi" "$BIN_DIR/veryfi"

echo "------------------------------------------------"
echo "Installation Complete."
echo "Location: $INSTALL_DIR"
echo "Usage: veryfi exam ..."
echo "------------------------------------------------"