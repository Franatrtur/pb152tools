# veryfi

this is a collection of tools for pb152cv.

## how to install

```bash
# just clone this repo and run the installer
./install.sh
```
make sure `~/bin` is in your `PATH`. it probably is.

## what it does

#### `veryfi exam [options]` - make a fake test

this makes a mock exam in a new folder. it copies random `p*` or `r*` files from your `~/pb152` folder.

**options:**
*   `-n 5`: how many tasks (default is 5)
*   `-w 01-05`: use only weeks 1 to 5
*   `-p`: only 'p' tasks
*   `-r`: only 'r' tasks
*   `-s`: don't rename files to `task_1.c`, `task_2.c` etc.

after you're done:
*   `veryfi exam done`: archives your test to `exams_finished`
*   `veryfi exam reveal`: renames `task_*.c` back to original names if you didn't use `-s`

#### `veryfi format` - practice for the format test

copies a messy C file to `~/pb152/print_format_practice.c`.
your job is to fix the formatting. it tells you how to compile it to check your work.

#### `veryfi my <your_file.c>` - get hints for my code

this is an AI tutor. it looks at your code and the `.log` file and gives you a hint about what to do next. it won't give you the answer.

you need to set your Gemini API key first:
```bash
export GEMINI_API_KEY="your_key_here"
```
put that in your `.bashrc` or something.

## how to uninstall

just run this from the repo folder:
```bash
./uninstall.sh
```

it will delete `~/.veryfi` and the symlink in `~/bin`.