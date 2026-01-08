#!/bin/python
import os
import re
import shutil
import random
import json
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Set, Dict

# --- Configuration ---
MONTH_DIR_PATTERN = re.compile(r'^(0[1-9]|1[0-2])$')
SUPPORT_FILES = ['pb152.cpp', 'pb152io.c', '.helper.sh']
PROGRESS_FILE = 'progress.json'
DEST_DIR_NAME = 'exam'
ARCHIVE_DIR_NAME = 'exams_finished'
TEXT_SOURCE_FILE = 'text/pb152.reference.txt'

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

def get_root_dir() -> Path:
    cwd = Path.cwd()
    if (cwd / '01').exists() and (cwd / 'pb152.cpp').exists():
        return cwd
    home_path = Path.home() / 'pb152'
    if home_path.exists():
        return home_path
    return cwd

def parse_week_range(week_str: str) -> Set[str]:
    if not week_str or week_str.lower() == 'all':
        return set()
    weeks = set()
    parts = week_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                for w in range(start, end + 1):
                    weeks.add(f"{w:02d}")
            except ValueError: pass
        else:
            try:
                weeks.add(f"{int(part):02d}")
            except ValueError: pass
    return weeks

def load_processed_paths(path: Path) -> Set[str]:
    if not path.exists(): return set()
    try:
        with path.open() as f: return set(json.load(f))
    except: return set()

def save_processed_paths(path: Path, paths: Set[str]):
    try:
        with path.open('w') as f: json.dump(sorted(list(paths)), f, indent=4)
    except Exception as e: logging.error(f"Failed to save progress: {e}")

def get_candidates(root: Path, target_weeks: Set[str], include_p: bool, include_r: bool, processed: Set[str]) -> List[Path]:
    candidates = []
    prefixes = []
    if include_p: prefixes.append('p')
    if include_r: prefixes.append('r')
    if not prefixes: return []

    pattern_str = r'^(' + '|'.join(prefixes) + r')\d.*\.c$'
    file_pattern = re.compile(pattern_str, re.IGNORECASE)

    all_items = sorted([p for p in root.iterdir() if p.is_dir()])
    for week_dir in all_items:
        if not MONTH_DIR_PATTERN.match(week_dir.name): continue
        if target_weeks and week_dir.name not in target_weeks: continue

        for file_path in week_dir.iterdir():
            if file_path.name.endswith('.pristine'): continue
            if file_pattern.match(file_path.name):
                rel_str = f"{week_dir.name}/{file_path.name}"
                if rel_str not in processed:
                    candidates.append(file_path)
    return candidates

def archive_existing_exam(exam_dir: Path, archive_root: Path):
    """
    Moves completed assignment C files to exams_finished.
    De-anonymizes filenames if a mapping file exists.
    Cleans up the rest of the exam folder.
    """
    if not exam_dir.exists():
        return

    # Ensure archive root exists
    archive_root.mkdir(parents=True, exist_ok=True)

    # Check if there is anything to archive
    if not any(exam_dir.iterdir()):
        return

    # 1. Create timestamped folder based on makefile modification time
    existing = [p for p in archive_root.iterdir() if p.is_dir()]
    index = len(existing) + 1
    prefix = f"{index:02d}"

    # Get modification time of 'makefile'
    makefile_path = exam_dir / 'makefile'
    if makefile_path.exists():
        # Get the float timestamp and convert to datetime
        mtime = makefile_path.stat().st_mtime
        dt_object = datetime.fromtimestamp(mtime)
    else:
        # Fallback to current time if makefile is missing
        logging.warning(f"makefile not found in {exam_dir}, using current time for timestamp.")
        dt_object = datetime.now()

    timestamp = dt_object.strftime("%a %-d.%-m. %-I%p")
    dest_dir = archive_root / f"exam{prefix} {timestamp}"
    
    # 2. Load mapping if exists
    mapping = {}
    mapping_file = exam_dir / '00_mapping.txt'
    if mapping_file.exists():
        try:
            with open(mapping_file, 'r') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.split('=')
                        # "task_1.c" -> "12/p6_norm.c"
                        mapping[k.strip()] = v.strip()
        except Exception as e:
            logging.warning(f"Could not read mapping file: {e}")

    # 3. Move relevant files
    files_moved = 0
    
    # Only look for .c files
    for file_path in exam_dir.glob("*.c"):
        # Skip support files
        if file_path.name in ['pb152io.c', 'pb152.c'] or file_path.name.startswith('.'):
            continue
            
        # Determine target name (De-anonymize)
        if file_path.name in mapping:
            # Value is "12/p6_norm.c", we want "12.p6_norm.c"
            original_path_str = mapping[file_path.name]
            parts = original_path_str.split('/')
            if len(parts) == 2:
                target_name = f"{parts[0]}.{parts[1]}"
            else:
                target_name = parts[-1]
        else:
            target_name = file_path.name

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(dest_dir / target_name))
            files_moved += 1
        except Exception as e:
            logging.error(f"Failed to archive {file_path.name}: {e}")

    if files_moved > 0:
        logging.info(f"Archived {files_moved} assignments to {dest_dir.name}")

    # 4. Wipe the exam directory clean (remove logs, executables, support files)
    try:
        shutil.rmtree(exam_dir)
        # Recreate empty folder immediately to be ready for next steps
        exam_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to cleanup exam directory: {e}")

def generate_intro_joke(root_dir: Path, dest_dir: Path):
    """
    Generates a nonsense 00_intro.txt using random words from the reference text.
    Structure: 3 paragraphs, 4 lines each, 10 words per line.
    """
    ref_file = root_dir / TEXT_SOURCE_FILE
    words = []

    # Try to load words from reference
    if ref_file.exists():
        try:
            with open(ref_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find words (alphanumeric, ignoring punctuation)
                words = re.findall(r'\w+', content)
                # Filter out very short words for better "visuals"
                words = [w for w in words if len(w) > 2]
        except Exception:
            pass
    
    # Fallback if file missing or empty
    if not words:
        words = ["void", "int", "char", "struct", "pointer", "segmentation", "fault", 
                 "core", "dump", "buffer", "overflow", "stack", "heap", "malloc", "free"]

    output_lines = []
    
    for p in range(3): # 3 Paragraphs
        paragraph = []
        for l in range(4): # 4 Lines
            # Sample 10 random words (allow duplicates in general, but sample unique for the line)
            # If we don't have enough unique words, allow replacement
            if len(words) >= 10:
                line_words = random.sample(words, 10)
            else:
                line_words = [random.choice(words) for _ in range(10)]
            
            paragraph.append(" ".join(line_words))
        
        output_lines.append("\n".join(paragraph))

    preambule = '# Good luck u stupid\n\nPokud něčemu nerozumíte, stačí si vzpomenout na jednoduchá faktická tvrzení.\n\nJako podklad máte k dispozici učební materiál:\n\n\n'
    final_text = preambule + "\n\n".join(output_lines)
    
    try:
        with open(dest_dir / '00_intro.txt', 'w', encoding='utf-8') as f:
            f.write(final_text + "\n")
        logging.info("Generated a very serious 00_intro.txt")
    except Exception as e:
        logging.warning(f"Failed to generate intro joke: {e}")

def copy_support_files(root: Path, dest_dir: Path) -> Path:
    weeks = sorted([d for d in root.iterdir() if d.is_dir() and MONTH_DIR_PATTERN.match(d.name)], 
                   key=lambda x: x.name, reverse=True)
    best_week = next((w for w in weeks if (w / 'makefile').exists()), None)
    
    if not best_week: raise FileNotFoundError("No makefile found.")

    for filename in SUPPORT_FILES:
        src = best_week / filename
        if not src.exists(): src = root / filename
        if src.exists(): shutil.copy2(src, dest_dir / filename)

    return best_week / 'makefile'

def create_dynamic_makefile(template_path: Path, dest_dir: Path, active_filenames: List[str]):
    active_filenames.sort()
    with open(template_path, 'r') as f: content = f.read()

    # Clear D, E, T, R
    for v in ['SRC_D', 'SRC_E', 'SRC_T', 'SRC_R']:
        content = re.sub(fr'^({v}\s*=).*$', r'\1', content, flags=re.MULTILINE)

    # Set P
    files_str = ' '.join(active_filenames)
    if re.search(r'^SRC_P\s*=', content, re.MULTILINE):
        content = re.sub(r'^(SRC_P\s*=).*$', f'\\1 {files_str}', content, flags=re.MULTILINE)
    else:
        content = f"SRC_P = {files_str}\n" + content

    with open(dest_dir / 'makefile', 'w') as f: f.write(content)

def reveal_exam_files(exam_dir: Path):
    """
    Checks if the exam is anonymized and reveals original filenames.
    """
    mapping_file = exam_dir / '00_mapping.txt'
    if not mapping_file.exists():
        logging.info("Exam is not anonymized or no mapping file found.")
        return

    logging.info("Mapping file found. Revealing original filenames...")
    
    mapping = {}
    new_filenames = []
    
    try:
        with open(mapping_file, 'r') as f:
            for line in f:
                if '=' in line:
                    k, v = line.split('=')
                    mapping[k.strip()] = v.strip() # k=task_1.c, v=04/p02.c
    except Exception as e:
        logging.error(f"Failed to read mapping file: {e}")
        return

    for task_name, original_path_str in mapping.items():
        src_file = exam_dir / task_name
        if src_file.exists():
            # Convert 04/p02.c -> 04.p02.c
            parts = original_path_str.split('/')
            if len(parts) == 2:
                final_name = f"{parts[0]}.{parts[1]}"
            else:
                final_name = parts[-1]
            
            dest_file = exam_dir / final_name
            try:
                shutil.move(str(src_file), str(dest_file))
                new_filenames.append(final_name)
                logging.info(f"Revealed: {task_name} -> {final_name}")
            except Exception as e:
                logging.error(f"Failed to rename {task_name}: {e}")
        else:
            logging.warning(f"File {task_name} listed in mapping but not found in exam dir.")

    # Update Makefile if it exists
    makefile_path = exam_dir / 'makefile'
    if makefile_path.exists() and new_filenames:
        create_dynamic_makefile(makefile_path, exam_dir, new_filenames)
        logging.info("Makefile updated with revealed names.")
    
    # Remove mapping file
    try:
        os.remove(mapping_file)
        logging.info("Mapping file removed.")
    except Exception as e:
        logging.error(f"Failed to remove mapping file: {e}")

def run_pb152_update():
    logging.info("Running pb152 update.")
    subprocess.run("cd ~/pb152 && pb152 update", shell=True, check=True)
    logging.info("pb152 update finished.")

def main():
    parser = argparse.ArgumentParser(description="Generate a mock PB152 exam.")
    
    # Add subparsers to handle commands like 'reveal'
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.add_parser('reveal', help='Reveal anonymized file names in the current exam')
    subparsers.add_parser('done', help='Archive last exam')
    
    parser.add_argument('-n', '--num', type=int, default=5, help="Number of files")
    parser.add_argument('-w', '--weeks', type=str, default="all", help="Weeks filter, for example -w 04-08,11")
    parser.add_argument('-p', '--only-p', action='store_true', help="Only P assignments")
    parser.add_argument('-r', '--only-r', action='store_true', help="Only R assignments")
    parser.add_argument('-s', '--show', action='store_true', help="Do not anonymize name to task_X.c, show true name")
    args = parser.parse_args()

    root_dir = get_root_dir()
    dest_dir = root_dir / DEST_DIR_NAME

    archive_dir = root_dir / ARCHIVE_DIR_NAME
    progress_path = root_dir / PROGRESS_FILE
    
    # Handle 'reveal' command immediately
    if args.command == 'reveal':
        reveal_exam_files(dest_dir)
        return

    # Handle 'done' command immediately
    if args.command == 'done':
        archive_existing_exam(dest_dir, archive_dir)
        return

    run_pb152_update()

    include_p = True if not args.only_r else False
    include_r = True if not args.only_p else False
    if args.only_p and args.only_r: include_p, include_r = True, True # Explicitly both

    logging.info(f"Root: {root_dir}")
    
    processed = load_processed_paths(progress_path)
    target_weeks = parse_week_range(args.weeks)

    candidates = get_candidates(root_dir, target_weeks, include_p, include_r, processed)
    count = min(args.num, len(candidates))
    
    if count == 0:
        logging.info("No new eligible files found. You are done!")
        return

    # 1. Archive Previous Run (Before selecting new files)
    archive_existing_exam(dest_dir, archive_dir)

    # 2. Prepare for new exam
    dest_dir.mkdir(parents=True, exist_ok=True)
    selected = random.sample(candidates, count)
    logging.info(f"Selected {len(selected)} tasks.")

    try:
        makefile_template = copy_support_files(root_dir, dest_dir)
    except Exception as e:
        logging.error(f"Error copying support files: {e}")
        return

    # 3. Generate the Intro Joke
    generate_intro_joke(root_dir, dest_dir)

    newly_processed_ids = set()
    final_filenames = []
    mapping_lines = []

    for idx, src_path in enumerate(selected):
        try:
            week = src_path.parent.name
            pristine_path = src_path.with_suffix(src_path.suffix + '.pristine')
            final_src = pristine_path if pristine_path.exists() else src_path
            
            original_basename = src_path.name
            
            if not args.show:
                dest_name = f"task_{idx + 1}.c"
                mapping_lines.append(f"{dest_name} = {week}/{original_basename}")
            else:
                dest_name = f"{week}.{original_basename}"

            shutil.copy2(final_src, dest_dir / dest_name)
            
            final_filenames.append(dest_name)
            newly_processed_ids.add(f"{week}/{original_basename}") # Always store normalized ID
            
            log_type = "pristine" if pristine_path.exists() else "standard"
            logging.info(f"Copied {log_type}: {week}/{original_basename} -> {dest_name}")

        except Exception as e:
            logging.error(f"Error copying {src_path}: {e}")

    if not args.show and mapping_lines:
        with open(dest_dir / '00_mapping.txt', 'w') as f:
            f.write("\n".join(mapping_lines) + "\n")

    create_dynamic_makefile(makefile_template, dest_dir, final_filenames)
    save_processed_paths(progress_path, processed.union(newly_processed_ids))
    logging.info(f"Exam generated in '{dest_dir.name}'.")

if __name__ == "__main__":
    main()