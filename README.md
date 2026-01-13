<h1 align="center">pb152tools</h1>

<p align="center">A collection of tools for PB152cv course at FI MUNI.</p>

## Installation on AISA

run in shell:
```bash
git clone https://github.com/franatrtur/pb152tools.git
pb152tools/install.sh
```

## Exam tool

The `exam` tool is used to practice for the PB152cv exam.  
Thanks to this tool, me and other students have passed with flying colors.

```bash
pb152tools exam
```

will create a mock exam just like the real one in the `pb152` directory.  
You can also specify which weeks to select from and whether to only select __P__ or __R__ assignments.
```
~/
├─ pb152/
│  ├─ exam/
│  │  ├─ task_1.c
│  │  ├─ task_2.c
│  │  ├─ task_3.c
│  │  ├─ task_4.c
│  │  ├─ task_5.c
│  ├─ exams_finished/
│  ├─ exams.progress.json

```
You can run standard `make` commands as you are used to, thanks to custom makefile generation.  
You can track your progress (saved in `exams.progress.json`) with `pb152tools exam progress`.  

Your completed exams are archived automatically to the `exams_finished` folder.  
For reliable timing, make sure to run `pb152tools exam done` as soon as you have completed your mock exam.

For more options, see `pb152tools exam --help`

## Advisor tool (Beta)

The `advisor` tool is a work in progress. It is an AI feature intended to provide advice on how to improve your C code, while __not writing the code for you__.

More information about the `advisor` tool can be found in the `CONTRIBUTING.md` file.

## Format practice tool
`pb152tools format`
This tool helps you practice your C string formatting skills  
(`fprintf(..., "heres a string: %s", ...)`, `sprinf(number_text, "x = %d", x)`).  

It can be useful for debugging and priting formatted output. Also necessary with snprintf and sprintf for a few assignments. It will copy a C file to `~/pb152/print_format_practice.c` and give you instructions on how to compile and run it.


## Updates and Uninstallation

To reinstall to the most recent version:
```bash
pb152tools update
```
To uninstall:
```bash
pb152tools uninstall
```