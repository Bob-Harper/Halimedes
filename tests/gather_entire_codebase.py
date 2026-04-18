#!/usr/bin/env python3
import os
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------
# CONFIG: Directories to scan (non-recursive)
# ---------------------------------------------------------
DIRECTORIES = [
    "/home/msutt/hal",
    "/home/msutt/hal/body",
    "/home/msutt/hal/helpers",
    "/home/msutt/hal/cortex",
]

# ---------------------------------------------------------
# OUTPUT FILE
# ---------------------------------------------------------
OUTPUT_FILE = "/home/msutt/hal/hal_code_dump.txt"

# ---------------------------------------------------------
# FILE EXTENSIONS TO INCLUDE
# ---------------------------------------------------------
EXTENSIONS = {".py", ".txt"}

# ---------------------------------------------------------
# SCRIPT
# ---------------------------------------------------------
def collect_files():
    output_path = Path(OUTPUT_FILE).expanduser()

    # If the output file already exists, remove it before doing anything.
    if output_path.exists():
        try:
            output_path.unlink()
            print(f"Removed existing output file: {output_path}")
        except Exception as e:
            print(f"Could not remove existing output file: {e}")
            return

    output_lines = []

    for directory in DIRECTORIES:
        directory = Path(directory).expanduser()
        if not directory.exists():
            print(f"Skipping missing directory: {directory}")
            continue

        # NON-RECURSIVE: only list files directly inside this directory
        for file in sorted(directory.iterdir()):
            # Skip the output file if it happens to be in the scanned directory
            try:
                if file.resolve() == output_path.resolve():
                    continue
            except Exception:
                # If resolve fails for some reason, just continue normally
                pass

            if file.is_file() and file.suffix.lower() in EXTENSIONS:

                # Add a clear separator
                output_lines.append("\n" + "=" * 80)
                output_lines.append(f"FILE: {file}")
                output_lines.append("=" * 80 + "\n")

                try:
                    with open(file, "r", encoding="utf-8", errors="ignore") as f:
                        output_lines.append(f.read())
                except Exception as e:
                    output_lines.append(f"[ERROR READING FILE: {e}]")

    # Write everything to the output file
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output_lines.insert(0, f"CODE DUMP GENERATED: {timestamp}\n")

        with open(output_path, "w", encoding="utf-8") as out:
            out.write("\n".join(output_lines))

        print(f"\nDone! Output written to: {output_path}")
    except Exception as e:
        print(f"Failed to write output file: {e}")


if __name__ == "__main__":
    collect_files()