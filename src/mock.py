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
from typing import List, Set, Dict, NamedTuple

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

# --- Progress Display Constants ---
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

BAR_WIDTH = 20
TOPIC_WIDTH = 25

class WeekStats(NamedTuple):
    week: str
    topic: str
    total: int
    completed: int
    completed_names: List[str]


def get_root_dir() -> Path:
    """
    Determines the root directory for pb152 assignments, prioritizing ~/pb152.
    """
    # The script is installed in a hidden folder, so CWD is not the source of truth.
    # The user's work is always in ~/pb152.
    home_path = Path.home() / 'pb152'
    if home_path.is_dir():
        return home_path
    
    # Fallback to CWD only if ~/pb152 doesn't exist, for local testing.
    cwd = Path.cwd()
    if (cwd / '01').exists() or (cwd / 'pb152.cpp').exists():
        return cwd
    
    # If neither is valid, we can't proceed.
    logging.error("Could not find the '~/pb152' directory.")
    logging.error("Please make sure your assignments are located there.")
    exit(1)


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

def show_progress(root_dir: Path, only_p: bool, only_r: bool):
    """Displays a table of completed assignments."""
    include_p = not only_r
    include_r = not only_p
    
    progress_path = root_dir / PROGRESS_FILE
    completed_set = load_processed_paths(progress_path)

    all_stats = []

    week_dirs = sorted([p for p in root_dir.iterdir() if p.is_dir() and MONTH_DIR_PATTERN.match(p.name)])

    for week_dir in week_dirs:
        week = week_dir.name
        
        # Get topic
        topic = "???"
        intro_file = week_dir / "00_intro.txt"
        if intro_file.exists():
            try:
                with open(intro_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    # Topic is usually '# <Topic Name>'
                    if first_line.startswith("#"):
                        topic = first_line[1:].strip()
            except Exception: 
                pass
        
        # Get all tasks for this week
        total_tasks = []
        if include_p:
            total_tasks.extend(p for p in week_dir.glob("p*.c") if not p.name.endswith('.pristine'))
        if include_r:
            total_tasks.extend(p for p in week_dir.glob("r*.c") if not p.name.endswith('.pristine'))

        if not total_tasks:
            continue

        # Check which are completed
        completed_tasks = []
        for task_path in total_tasks:
            task_id = f"{week}/{task_path.name}"
            if task_id in completed_set:
                completed_tasks.append(task_path.name)
        
        all_stats.append(WeekStats(
            week=week,
            topic=topic,
            total=len(total_tasks),
            completed=len(completed_tasks),
            completed_names=sorted(completed_tasks)
        ))

    # --- Print Header ---
    title_p = "P" if include_p else ""
    title_r = "R" if include_r else ""
    title = f"Progress ({title_p}{'&' if include_p and include_r else ''}{title_r} tasks)"
    
    print(f"\n{Colors.BOLD}{title.center(TOPIC_WIDTH + 35)}{Colors.RESET}")
    print("-" * (TOPIC_WIDTH + 40))
    print(
        f"{Colors.BOLD}{'Week':<5} | {'Topic':<{TOPIC_WIDTH}} | {'Progress':<{BAR_WIDTH + 2}} | {'Done'}{Colors.RESET}"
    )
    print("-" * (TOPIC_WIDTH + 40))

    # --- Print Body ---
    for stats in all_stats:
        # Progress Bar
        if stats.total > 0:
            filled = int((stats.completed / stats.total) * BAR_WIDTH)
            empty = BAR_WIDTH - filled
            bar = f"[{Colors.GREEN}{'#' * filled}{Colors.RESET}{'.' * empty}]"
        else:
            bar = f"[{'.' * BAR_WIDTH}]"

        # Topic truncation
        topic_str = stats.topic
        if len(topic_str) > TOPIC_WIDTH:
            topic_str = topic_str[:TOPIC_WIDTH - 3] + "..."
            
        # Completed names
        completed_str = ", ".join(stats.completed_names)

        print(
            f"{stats.week:<5} | {topic_str:<{TOPIC_WIDTH}} | {bar} | {Colors.GREEN}{completed_str}{Colors.RESET}"
        )
    print("-" * (TOPIC_WIDTH + 40))
    print()


def archive_existing_exam(exam_dir: Path, archive_root: Path):
    if not exam_dir.exists(): return
    archive_root.mkdir(parents=True, exist_ok=True)
    if not any(exam_dir.iterdir()): return

    existing = [p for p in archive_root.iterdir() if p.is_dir()]
    index = len(existing) + 1
    prefix = f"{index:02d}"

    makefile_path = exam_dir / 'makefile'
    mtime = makefile_path.stat().st_mtime if makefile_path.exists() else datetime.now().timestamp()
    dt_object = datetime.fromtimestamp(mtime)

    timestamp = dt_object.strftime("%a %-d.%-m. %-I%p")
    dest_dir = archive_root / f"exam{prefix} {timestamp}"
    
    mapping = {}
    mapping_file = exam_dir / '00_mapping.txt'
    if mapping_file.exists():
        try:
            with open(mapping_file, 'r') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.strip().split('=')
                        mapping[k.strip()] = v.strip()
        except Exception as e: logging.warning(f"Could not read mapping file: {e}")

    files_moved = 0
    for file_path in exam_dir.glob("*.c"):
        if file_path.name in ['pb152io.c', 'pb152.c'] or file_path.name.startswith('.'): continue
            
        original_path_str = mapping.get(file_path.name)
        if original_path_str:
            parts = original_path_str.split('/')
            target_name = f"{parts[0]}.{parts[1]}" if len(parts) == 2 else parts[-1]
        else:
            target_name = file_path.name

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(dest_dir / target_name))
            files_moved += 1
        except Exception as e: logging.error(f"Failed to archive {file_path.name}: {e}")

    if files_moved > 0: logging.info(f"Archived {files_moved} assignments to {dest_dir.name}")

    try:
        shutil.rmtree(exam_dir)
        exam_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e: logging.error(f"Failed to cleanup exam directory: {e}")

def generate_intro_joke(root_dir: Path, dest_dir: Path):
    ref_file = root_dir / TEXT_SOURCE_FILE
    words = []
    if ref_file.exists():
        try:
            with open(ref_file, 'r', encoding='utf-8') as f:
                content = f.read()
                words = [w for w in re.findall(r'\w+', content) if len(w) > 2]
        except Exception: pass
    
    if not words:
        words = ["void", "int", "char", "struct", "pointer", "segmentation", "fault", 
                 "core", "dump", "buffer", "overflow", "stack", "heap", "malloc", "free"]

    output_lines = []
    for _ in range(3): # 3 Paragraphs
        paragraph = []
        for _ in range(4): # 4 Lines
            line_words = random.sample(words, 10) if len(words) >= 10 else [random.choice(words) for _ in range(10)]
            paragraph.append(" ".join(line_words))
        output_lines.append("\n".join(paragraph))

    preambule = '# Good luck u stupid\n\nPokud něčemu nerozumíte, stačí si vzpomenout na jednoduchá faktická tvrzení.\n\nJako podklad máte k dispozici učební materiál:\n\n\n'
    final_text = preambule + "\n\n".join(output_lines)
    
    try:
        with open(dest_dir / '00_intro.txt', 'w', encoding='utf-8') as f:
            f.write(final_text + "\n")
        logging.info("Generated a very serious 00_intro.txt")
    except Exception as e: logging.warning(f"Failed to generate intro joke: {e}")

def copy_support_files(root: Path, dest_dir: Path) -> Path:
    weeks = sorted([d for d in root.iterdir() if d.is_dir() and MONTH_DIR_PATTERN.match(d.name)], 
                   key=lambda x: x.name, reverse=True)
    best_week = next((w for w in weeks if (w / 'makefile').exists()), None)
    
    if not best_week: raise FileNotFoundError("No makefile found in any week directory.")

    for filename in SUPPORT_FILES:
        src = best_week / filename
        if not src.exists(): src = root / filename # Fallback to root
        if src.exists(): shutil.copy2(src, dest_dir / filename)

    return best_week / 'makefile'

def create_dynamic_makefile(template_path: Path, dest_dir: Path, active_filenames: List[str]):
    active_filenames.sort()
    with open(template_path, 'r') as f: content = f.read()

    for v in ['SRC_D', 'SRC_E', 'SRC_T', 'SRC_R']:
        content = re.sub(fr'^({v}\s*=).*$', r'\1', content, flags=re.MULTILINE)

    files_str = ' '.join(active_filenames)
    if re.search(r'^SRC_P\s*=', content, re.MULTILINE):
        content = re.sub(r'^(SRC_P\s*=).*$', f'\\1 {files_str}', content, flags=re.MULTILINE)
    else:
        content = f"SRC_P = {files_str}\n" + content

    with open(dest_dir / 'makefile', 'w') as f: f.write(content)

def reveal_exam_files(exam_dir: Path):
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
                    k, v = line.strip().split('=')
                    mapping[k.strip()] = v.strip()
    except Exception as e:
        logging.error(f"Failed to read mapping file: {e}")
        return

    for task_name, original_path_str in mapping.items():
        src_file = exam_dir / task_name
        if src_file.exists():
            parts = original_path_str.split('/')
            final_name = f"{parts[0]}.{parts[1]}" if len(parts) == 2 else parts[-1]
            dest_file = exam_dir / final_name
            try:
                shutil.move(str(src_file), str(dest_file))
                new_filenames.append(final_name)
                logging.info(f"Revealed: {task_name} -> {final_name}")
            except Exception as e: logging.error(f"Failed to rename {task_name}: {e}")
        else: logging.warning(f"File {task_name} in mapping not found.")

    if makefile_path := exam_dir / 'makefile':
        if makefile_path.exists() and new_filenames:
            create_dynamic_makefile(makefile_path, exam_dir, new_filenames)
            logging.info("Makefile updated with revealed names.")
    
    try:
        os.remove(mapping_file)
        logging.info("Mapping file removed.")
    except Exception as e: logging.error(f"Failed to remove mapping file: {e}")

def run_pb152_update():
    logging.info("Running pb152 update.")
    try:
        subprocess.run("cd ~/pb152 && pb152 update", shell=True, check=True, capture_output=True)
        logging.info("pb152 update finished.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logging.warning(f"'pb152 update' failed: {e}. Continuing without update.")


def main():
    parser = argparse.ArgumentParser(description="Generate a mock PB152 exam.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Existing subparsers
    subparsers.add_parser('reveal', help='Reveal anonymized file names in the current exam')
    subparsers.add_parser('done', help='Archive last exam')

    # New 'progress' subparser
    progress_parser = subparsers.add_parser('progress', help='Show assignment completion progress')
    progress_parser.add_argument('-p', '--only-p', action='store_true', help="Show only P assignments")
    progress_parser.add_argument('-r', '--only-r', action='store_true', help="Show only R assignments")
    
    # Main parser arguments
    parser.add_argument('-n', '--num', type=int, default=5, help="Number of files")
    parser.add_argument('-w', '--weeks', type=str, default="all", help="Weeks filter (e.g., '04-08,11')")
    parser.add_argument('-p', '--only-p', action='store_true', help="Only P assignments for exam generation")
    parser.add_argument('-r', '--only-r', action='store_true', help="Only R assignments for exam generation")
    parser.add_argument('-s', '--show', action='store_true', help="Show true filenames in exam (no anonymization)")
    
    args = parser.parse_args()

    root_dir = get_root_dir()
    dest_dir = root_dir / DEST_DIR_NAME
    archive_dir = root_dir / ARCHIVE_DIR_NAME
    
    # --- Command Handling ---
    if args.command == 'reveal':
        reveal_exam_files(dest_dir)
        return
    if args.command == 'done':
        archive_existing_exam(dest_dir, archive_dir)
        return
    if args.command == 'progress':
        show_progress(root_dir, args.only_p, args.only_r)
        return

    # --- Default Action: Exam Generation ---
    run_pb152_update()

    # Note: argparse naming conflict. We need to distinguish flags for exam-gen from progress.
    # The main parser flags are used here.
    include_p_exam = not args.only_r
    include_r_exam = not args.only_p
    
    logging.info(f"Root: {root_dir}")
    
    progress_path = root_dir / PROGRESS_FILE
    processed = load_processed_paths(progress_path)
    target_weeks = parse_week_range(args.weeks)

    candidates = get_candidates(root_dir, target_weeks, include_p_exam, include_r_exam, processed)
    count = min(args.num, len(candidates))
    
    if count == 0:
        logging.info("No new eligible files found. You are done!")
        return

    archive_existing_exam(dest_dir, archive_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    selected = random.sample(candidates, count)
    logging.info(f"Selected {len(selected)} tasks.")

    try:
        makefile_template = copy_support_files(root_dir, dest_dir)
    except Exception as e:
        logging.error(f"Error copying support files: {e}")
        return

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
            newly_processed_ids.add(f"{week}/{original_basename}")
            
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
