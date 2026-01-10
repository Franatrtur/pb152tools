# Veryfi

A collection of command-line utilities designed to streamline your workflow for the `pb152` course at FI. It helps with mock exam generation, code formatting practice, and getting AI-powered hints for your assignments.

## Features

*   **Mock Exam Generation**: Create realistic, timed mock exams using a random selection of tasks from your coursework.
*   **AI-Powered Tutor**: Get intelligent, context-aware hints for your code without revealing the solution.
*   **Automatic Update Notifications**: The tool will let you know when a new version is available.
*   **Safe & Simple Installation**: A one-line installer that automatically configures your PATH.
*   **Robust Update/Uninstall Process**: Simple commands to update or completely remove the tool.

## Installation

Run the following commands in your terminal:

```bash
git clone https://github.com/Franatrtur/veryfi.git
cd veryfi
bash install.sh
```

The installer will copy the necessary files to `~/.veryfi` and create a symbolic link in `~/bin`. It will also automatically check if `~/bin` is in your system's `PATH` and, if not, will add it to your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`).

You will be prompted to install the optional AI Advisor, which requires an internet connection to download dependencies.

## Updating

To update Veryfi to the latest version, simply run:

```bash
veryfi update
```

The script will ask for confirmation, then safely download the latest version and reinstall the tool.

## Commands

### `veryfi exam [options]`

Generates a mock exam in a new directory. It copies a random selection of `p*` or `r*` files from your `~/pb152` directory.

*   **`[options]`**:
    *   `-n 5`: Number of tasks for the exam (default: 5).
    *   `-w 01-05`: Use tasks only from a specific range of weeks (e.g., weeks 1 to 5).
    *   `-p`: Use only 'p' (practice) tasks.
    *   `-r`: Use only 'r' (review) tasks.
    *   `-s`: Preserve original file names instead of renaming them to `task_1.c`, `task_2.c`, etc.

*   **`veryfi exam done`**: Archives the current exam to `~/pb152/exams_finished` and logs the time spent.
*   **`veryfi exam reveal`**: If you didn't use the `-s` option, this renames the `task_*.c` files back to their original names.

### `veryfi my <your_file.c>`

The AI Tutor. This command analyzes your source code and its corresponding `.log` file to provide a helpful hint without giving away the solution.

**Note:** This is an optional component. You must agree to its installation when running the installer. You also need to provide a Gemini API Key via an environment variable:

```bash
export GEMINI_API_KEY="your_key_here"
```
It's recommended to add this line to your `~/.bashrc` or `~/.zshrc` file.

### `veryfi format`

Helps you practice for the code formatting test. It copies a C file with messy formatting to `~/pb152/print_format_practice.c` and provides instructions on how to compile and check your work.

### `veryfi update`

Checks for and installs the latest version of the tool.

### `veryfi uninstall`

Removes all Veryfi files and symlinks from your system.

## Uninstalling

You can uninstall the tool at any time by running:
```bash
veryfi uninstall
```
This will remove the `~/.veryfi` directory and the symlinks from `~/bin`.
