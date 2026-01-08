#!/bin/bash
set -x # show commands

# Define the "Permanent Home" for the app
INSTALL_DIR="$HOME/.veryfi"
BIN_DIR="$HOME/bin"

echo "Installing Veryfi to $INSTALL_DIR..."

# 1. Clean Slate
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing previous installation..."
    rm -rf "$INSTALL_DIR"
fi

# 2. Create the directory
mkdir -p "$INSTALL_DIR"

# 3. Copy all source files
cp -r src "$INSTALL_DIR/"
cp -r bin "$INSTALL_DIR/"
cp -r assets "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"
cp uninstall.sh "$INSTALL_DIR/" # <-- COPY UNINSTALLER

# 4. Create the Isolated Venv
echo "Creating isolated virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

# 5. Install Dependencies (with visible output)
echo "Installing dependencies..."
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" # <-- SHOW PIP OUTPUT

# 6. Make executables
chmod +x "$INSTALL_DIR/bin/veryfi"
chmod +x "$INSTALL_DIR/uninstall.sh" # <-- MAKE UNINSTALLER EXECUTABLE

# 7. Symlink
mkdir -p "$BIN_DIR"
rm -f "$BIN_DIR/veryfi"
ln -s "$INSTALL_DIR/bin/veryfi" "$BIN_DIR/veryfi"

# 8. Ask for optional alias
read -p "Do you want to add the 'pb152cv' alias for 'veryfi'? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f "$BIN_DIR/pb152cv"
    ln -s "$INSTALL_DIR/bin/veryfi" "$BIN_DIR/pb152cv"
    echo "Alias 'pb152cv' created."
fi

set +x # hide commands
echo "------------------------------------------------"
echo "Installation Complete."
echo "Location: $INSTALL_DIR"
echo "Run 'veryfi help' to get started."
echo "To uninstall, you can now run 'veryfi uninstall'."