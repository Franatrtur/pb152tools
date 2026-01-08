from pathlib import Path

# 1. Find out where THIS python file is right now
CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent

# 2. Define where the assets are relative to the script
ASSETS_DIR = CURRENT_SCRIPT_DIR.parent / 'assets'