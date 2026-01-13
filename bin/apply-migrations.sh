#!/bin/bash

# This script applies necessary migrations to adapt to new versions of pb152tools.
# It is designed to be run from the installer.
# It should be safe to run this script multiple times.

echo "--> Applying necessary migrations..."

# --- Migration: v2.0 -> v2.1 ---
# Reason: The progress tracking file was renamed for clarity and to avoid conflicts.
# Action: Rename the old 'progress.json' to 'exams.progress.json' if it exists.
if [ -f "$HOME/pb152/progress.json" ]; then
    echo "    [MIGRATE] Renaming ~/pb152/progress.json to ~/pb152/exams.progress.json"
    mv "$HOME/pb152/progress.json" "$HOME/pb152/exams.progress.json"
fi

# --- Add future migrations below this line ---

echo "--> Migrations complete."
