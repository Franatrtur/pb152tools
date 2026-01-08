#!/usr/bin/env python

import os
import sys
import subprocess
import google.generativeai as genai
from pathlib import Path

# --- Constants ---
SCRIPT_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
PROCESS_CONTEXT_FILE = ASSETS_DIR / "pb152.process.txt"
REFERENCE_CONTEXT_FILE = ASSETS_DIR / "pb152.reference.compressed.txt"

# --- Prompt Templates ---

# Prompt for when the code runs successfully
SUCCESS_PROMPT_TEMPLATE = """
You are an expert C programming tutor for the PB152 course. The student's code has passed all visible tests. Your task is to provide guidance on potential improvements, edge cases, and hidden tests.

Do not provide a direct solution or complete code. Instead, act as a helpful guide. Your advice should be based on the provided context, which includes the student's current code, the successful output from the `make` command, a description of the course's build environment, and a reference manual.

**Guiding Principles:**
- **Code Quality:** Suggest improvements related to style, clarity, and efficiency.
- **Edge Cases:** Encourage the student to think about inputs or conditions their code might not be handling (e.g., empty input, large values, specific character sequences).
- **Hidden Tests:** The PB152 environment runs additional hidden tests. Based on the problem (inferred from the C file's `main` function), what kind of hidden tests might exist? What aspects of the solution are likely to be stressed further?
- **Robustness:** How could the code be made more robust against unexpected or invalid inputs?

**Context:**

1.  **Course Environment Description (`pb152.process.txt`):**
    ```
    {process_context}
    ```

2.  **C/POSIX Reference Manual (`pb152.reference.compressed.txt`):**
    ```
    {reference_context}
    ```

3.  **Student's C Code (`{c_file_path}`):**
    ```c
    {c_code}
    ```

4.  **Successful `make` Output:**
    ```
    {make_output}
    ```

**Your Task:**
The student's code works for the basic tests. Congratulate them briefly. Then, challenge them to think deeper. Prompt them with questions about potential edge cases and what hidden tests might be evaluating. Suggest areas for code refinement without rewriting it for them.
"""

# Prompt for when the code fails or has issues
FAILURE_PROMPT_TEMPLATE = """
You are an expert C programming tutor for the PB152 course. Your task is to provide guidance to a student on how to proceed with their coding assignment based on the errors from their last run.

Do not provide a direct solution or complete code. Instead, act as a helpful guide who points the student in the right direction. Your advice should be based on the provided context, which includes the student's current code, the `make` output, the detailed error log, a description of the course's build environment, and a reference manual.

Analyze the student's code in light of the `make` output and the log file. Your guidance should help the student understand the error, suggest relevant functions from the reference manual, and give them a strategy for the next steps.

**Context:**

1.  **Course Environment Description (`pb152.process.txt`):**
    ```
    {process_context}
    ```

2.  **C/POSIX Reference Manual (`pb152.reference.compressed.txt`):**
    ```
    {reference_context}
    ```

3.  **Student's C Code (`{c_file_path}`):**
    ```c
    {c_code}
    ```

4.  **`make` Command Output:**
    ```
    {make_output}
    ```
    
5.  **Execution Log (`{log_file_path}`):**
    ```
    {log_content}
    ```

**Your Task:**
Based on the error messages, provide a clear, encouraging, and actionable guide for the student. Focus on what they should try next. Explain what the error means in this context and what part of the code is likely causing it.
"""


def read_file_or_default(path: Path, default: str) -> str:
    """Reads a file's content, returning a default string if it doesn't exist."""
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return default

def main():
    """Main function to generate and print the advisor's guidance."""
    # 1. Check for API Key
    if "GEMINI_API_KEY" not in os.environ:
        print("Error: The GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # 2. Get File Path from Arguments
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path_to_c_file>", file=sys.stderr)
        sys.exit(1)
    
    c_file_path = Path(sys.argv[1]).resolve()

    if not c_file_path.is_file():
        print(f"Error: File not found at '{c_file_path}'", file=sys.stderr)
        sys.exit(1)

    c_file_dir = c_file_path.parent
    c_file_name = c_file_path.name

    # 3. Run `make` command
    print(f"Running 'make {c_file_name}' in {c_file_dir}...", file=sys.stderr)
    try:
        make_process = subprocess.run(
            ["make", c_file_name],
            cwd=c_file_dir,
            capture_output=True,
            text=True,
            timeout=30 # 30-second timeout for safety
        )
        make_output = make_process.stdout + make_process.stderr
        print("---", "make output", "---", file=sys.stderr)
        print(make_output, file=sys.stderr)
        print("---", "end make output", "---", "\n", file=sys.stderr)

    except FileNotFoundError:
        print("Error: 'make' command not found. Is it installed and in your PATH?", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"Error: 'make {c_file_name}' timed out after 30 seconds.", file=sys.stderr)
        sys.exit(1)

    # 4. Determine Log File Path and Read Context
    log_file_name = f".{c_file_name}.log"
    log_file_path = c_file_dir / log_file_name

    c_code = read_file_or_default(c_file_path, "")
    process_context = read_file_or_default(PROCESS_CONTEXT_FILE, "Process context not found.")
    reference_context = read_file_or_default(REFERENCE_CONTEXT_FILE, "Reference context not found.")
    log_content = read_file_or_default(log_file_path, "No log file found.")

    # 5. Choose Prompt and Construct
    tests_passed = make_process.stdout.strip().endswith("OK")

    if tests_passed:
        prompt = SUCCESS_PROMPT_TEMPLATE.format(
            process_context=process_context,
            reference_context=reference_context,
            c_file_path=c_file_name,
            c_code=c_code,
            make_output=make_output
        )
    else:
        prompt = FAILURE_PROMPT_TEMPLATE.format(
            process_context=process_context,
            reference_context=reference_context,
            c_file_path=c_file_name,
            c_code=c_code,
            make_output=make_output,
            log_file_path=log_file_path.name,
            log_content=log_content
        )

    # 6. Call the Gemini API
    try:
        print(f"Veryfi Advisor is thinking...\n", file=sys.stderr)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt,
                                         generation_config=genai.types.GenerationConfig(
                                             temperature=0.2,
                                         ))
        
        # 7. Print the Response
        print(response.text)

    except Exception as e:
        print(f"\nError: An error occurred while contacting the Gemini API: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()