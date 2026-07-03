"""
Copy all files from a directory and its subdirectories
into a single output directory.

Usage:
    python extract_files_from_directory.py INPUT_DIR -o OUTPUT_DIR
"""

import os
import shutil
import argparse
import platform
import subprocess

def check_dir(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"'{path}' is not a valid directory")
    return path

def create_output_dir_if_not_exist(output_dir):
  if not os.path.exists(output_dir):
      os.makedirs(output_dir)

def extract_and_copy_files_to_output_dir(input_dir, output_dir):
    create_output_dir_if_not_exist(output_dir)

    for root, _, files in os.walk(input_dir):
        for file in files:
            source = os.path.join(root, file)
            shutil.copy2(source, output_dir)

    print(f"Files copied to: {output_dir}")

def open_folder(path):
    system = platform.system()

    if system == "Windows":
        os.startfile(path)
    elif system == "Darwin":  # macOS
        subprocess.run(["open", path])
    else:  # Linux
        subprocess.run(["xdg-open", path])

def main():
  parser = argparse.ArgumentParser(
    description="Copy files from a directory and all subdirectories to an output directory.",
    usage="python %(prog)s INPUT_DIR -o OUTPUT_DIR"
  )

  parser.add_argument(
    "input",
    type=check_dir,
    help="Source directory"
  )

  parser.add_argument(
    "-o",
    "--output",
    required=True,
    help="Destination directory"
  )

  args = parser.parse_args()

  extract_and_copy_files_to_output_dir(
      args.input,
      args.output
  )

  open_folder(args.output)

if __name__ == "__main__":
  main()