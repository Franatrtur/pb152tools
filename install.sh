#!/bin/bash

# --- Get Script's own directory ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Define the "Permanent Home" for the app
INSTALL_DIR="$HOME/.pb152tools"
BIN_DIR="$HOME/bin"

echo "Installing pb152tools to $INSTALL_DIR..."

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
cp "$SCRIPT_DIR/version.txt" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/repo.conf" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/uninstall.sh" "$INSTALL_DIR/"

# 4. Create the Isolated Venv
echo "--> Creating Python virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

# 5. Install Optional AI Advisor Dependencies
read -p "Do you want to install the optional AI Advisor (BETA) (requires ~50MB download)? (y/N) " -n 1 -r
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
chmod +x "$INSTALL_DIR/bin/pb152tools"
chmod +x "$INSTALL_DIR/bin/apply-migrations.sh"
chmod +x "$INSTALL_DIR/uninstall.sh"

# 7. Symlink
echo "--> Creating symlink in $BIN_DIR..."
mkdir -p "$BIN_DIR"
rm -f "$BIN_DIR/pb152tools"
ln -s "$INSTALL_DIR/bin/pb152tools" "$BIN_DIR/pb152tools"

# 8. Run migrations for past breaking changes
bash "$INSTALL_DIR/bin/apply-migrations.sh"

# 9. Ask for optional alias
read -p "Do you want to add the 'pb152cv' alias for 'pb152tools'? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "--> Creating alias 'pb152cv'..."
    rm -f "$BIN_DIR/pb152cv"
    ln -s "$INSTALL_DIR/bin/pb152tools" "$BIN_DIR/pb152cv"
fi

# 10. Self-destruct the source folder silently
(
  sleep 2 &&
  rm -rf "$SCRIPT_DIR"
) &
disown

# --- Setup user's PATH to include $HOME/bin ---
setup_user_path() {
    echo "--> Checking if $HOME/bin is in your PATH..."
    if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
        echo "    -> '$HOME/bin' is not in your PATH."
        
        # Determine shell profile file
        if [ -n "$BASH_VERSION" ]; then
            PROFILE_FILE="$HOME/.bashrc"
        elif [ -n "$ZSH_VERSION" ]; then
            PROFILE_FILE="$HOME/.zshrc"
        else
            PROFILE_FILE="$HOME/.profile"
        fi

        echo "    -> Detected shell profile: $PROFILE_FILE"

        if [ -f "$PROFILE_FILE" ] && grep -q 'export PATH=.*$HOME/bin' "$PROFILE_FILE"; then
            echo "    -> Your '$PROFILE_FILE' already seems to set the PATH, but it's not sourced."
            echo "    -> Please run 'source $PROFILE_FILE' or open a new terminal."
        else
            echo "    -> Adding '$HOME/bin' to PATH in '$PROFILE_FILE'."
            # Append the export command
            echo -e "\n# Added by pb152tools installer to include local binaries" >> "$PROFILE_FILE"
            echo 'export PATH="$HOME/bin:$PATH"' >> "$PROFILE_FILE"
            echo "    -> PATH updated. Please run 'source $PROFILE_FILE' or open a new terminal for changes to take effect."
        fi
    else
        echo "--> '$HOME/bin' is already in your PATH. Excellent."
    fi
}

# Run the function to check and configure the user's path
setup_user_path


echo "------------------------------------------------"
echo "Installation Complete."
echo "Location: $INSTALL_DIR"
echo "Run 'pb152tools help' to get started."
echo "To uninstall, you can now run 'pb152tools uninstall'."
echo
echo "NOTE: If the 'pb152tools' command is not found, please restart your terminal or run 'source ~/.bashrc'."