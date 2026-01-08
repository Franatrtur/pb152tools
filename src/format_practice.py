from pathlib import Path
import os

# 1. Find out where THIS python file is right now
CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent

# 2. Define where the assets are relative to the script
ASSETS_DIR = CURRENT_SCRIPT_DIR.parent / 'assets'
SOURCE_C_FILE_PATH = ASSETS_DIR / 'print_format_practice.c'

def main():
    """
    This script copies a C file to a specific location in the user's home directory
    and provides instructions for the user to practice formatting.
    """
    if not SOURCE_C_FILE_PATH.exists():
        print(f"Error: The source file {SOURCE_C_FILE_PATH} does not exist.")
        return

    # Define the target directory and file path
    TARGET_DIR = Path.home() / 'pb152'
    TARGET_C_FILE_PATH = TARGET_DIR / 'print_format_practice.c'

    # Create the target directory if it doesn't exist
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Read the content from the source file
        with open(SOURCE_C_FILE_PATH, 'r') as f_source:
            content = f_source.read()

        # Write the content to the target file
        with open(TARGET_C_FILE_PATH, 'w') as f_target:
            f_target.write(content)

        print("--- C Code Formatting Practice ---")
        print(f"A C file has been placed in: {TARGET_C_FILE_PATH}")
        print("Objective: Open this file, reformat the C code to match style guidelines, and save your changes.")
        print("You can compile and run your formatted code to check your work.")
        print(f"For example: gcc {TARGET_C_FILE_PATH} -o {TARGET_DIR}/formatted_c_file && {TARGET_DIR}/formatted_c_file")
        print("-----------------------------------")

    except IOError as e:
        print(f"Error: Could not copy the file. {e}")


if __name__ == "__main__":
    main()
