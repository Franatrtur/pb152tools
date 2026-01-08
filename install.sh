#!/bin/bash

# --- Get Script's own directory ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Define the "Permanent Home" for the app
INSTALL_DIR="$HOME/.veryfi"
BIN_DIR="$HOME/bin"

echo "Installing Veryfi to $INSTALL_DIR..."

# 1. Clean Slate
if [ -d "$INSTALL_DIR" ]; then
    echo "--> Removing previous installation..."
    rm -rf "$INSTALL_DIR"
fi

# 2. Create directories
echo "--> Creating directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# 3. Copy all source files
echo "--> Copying application files..."
cp -r "$SCRIPT_DIR/src" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/bin" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/assets" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/uninstall.sh" "$INSTALL_DIR/"

# 4. Create the Isolated Venv
echo "--> Creating Python virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

# 5. Install Optional AI Advisor Dependencies
read -p "Do you want to install the optional AI Advisor (requires ~50MB download)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "--> Installing AI Advisor dependencies via pip..."
    "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    # Create a flag file to indicate the advisor is enabled
    touch "$INSTALL_DIR/.advisor_enabled"
    echo "--> AI Advisor installed."
else
    echo "--> Skipping AI Advisor installation."
fi

# 6. Make executables
echo "--> Setting file permissions..."
chmod +x "$INSTALL_DIR/bin/veryfi"
chmod +x "$INSTALL_DIR/uninstall.sh"

# 7. Symlink
echo "--> Creating symlink in $BIN_DIR..."
mkdir -p "$BIN_DIR"
rm -f "$BIN_DIR/veryfi"
ln -s "$INSTALL_DIR/bin/veryfi" "$BIN_DIR/veryfi"

# 8. Ask for optional alias
read -p "Do you want to add the 'pb152cv' alias for 'veryfi'? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "--> Creating alias 'pb152cv'..."
    rm -f "$BIN_DIR/pb152cv"
    ln -s "$INSTALL_DIR/bin/veryfi" "$BIN_DIR/pb152cv"
fi

# 9. Self-destruct the source folder
(
  sleep 2 &&
  echo -e "\n--> Cleaning up installation source folder..." &&
  rm -rf "$SCRIPT_DIR" &
) &
# Detach the subshell completely
disown

echo "------------------------------------------------"
echo "Installation Complete."
echo "Location: $INSTALL_DIR"
echo "Run 'veryfi help' to get started."
echo "To uninstall, you can now run 'veryfi uninstall'."
echo
echo "NOTE: If the 'veryfi' command is not found, please restart your terminal or run 'source ~/.bashrc'."