# Veryfi - pb152cv tools

It is very, very FI.  
this is a collection of tools for pb152cv to help with mock exams, formatting, and getting hints.

## how to install

ON AISA:
```bash
git clone https://github.com/Franatrtur/veryfi.git
cd veryfi
bash install.sh
```
The installer will try to add `~/bin` to your PATH. You might need to open a new terminal for it to work.

## how to update

Just run:
```bash
veryfi update
```
It will check for a new version online, show you what's new (e.g. `v2.3 -> v2.8`), and ask before updating.

## what it does

#### `veryfi exam [options]` - make a fake test

This makes a mock exam in a new folder. It copies random `p*` or `r*` files from your `~/pb152` folder.

**options:**
*   `-n 5`: how many tasks (default is 5)
*   `-w 01-05`: use only weeks 1 to 5
*   `-p`: only 'p' tasks
*   `-r`: only 'r' tasks
*   `-s`: don't rename files to `task_1.c`, `task_2.c` etc.

After you're done:
*   `veryfi exam done`: archives your test to `exams_finished` and tells you how long you took.
*   `veryfi exam reveal`: renames `task_*.c` back to original names if you didn't use `-s`.

#### `veryfi format` - practice for the format test

Copies a messy C file to `~/pb152/print_format_practice.c`.
Your job is to fix the formatting. It tells you how to compile it to check your work.

#### `veryfi my <your_file.c>` - get hints for my code

This is an AI tutor. It looks at your code and the `.log` file and gives you a hint about what to do next. It won't give you the answer.

You need to set your Gemini API key first:
```bash
export GEMINI_API_KEY="your_key_here"
```
Put that in your `.bashrc` or something.

#### `veryfi update`

Checks for new versions and installs them.

#### `veryfi uninstall`

Removes all veryfi files and symlinks from your system.

## how to uninstall

The easiest way is to run the command:
```bash
veryfi uninstall
```
It will delete `~/.veryfi` and the symlinks in `~/bin`.