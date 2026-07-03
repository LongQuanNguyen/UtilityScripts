"""
Prepend each file's parent folder name to the filename.

Processes a directory recursively. For every file found,
its immediate parent folder name is added as a prefix.

Example:
    photos/
    ├── trip1/
    │   └── image.jpg
    └── trip2/
        └── image.jpg

Becomes:
    trip1_image.jpg
    trip2_image.jpg

Usage:
    python prepend_folder_name_to_files.py DIRECTORY
"""

import os
import argparse
import platform
import subprocess


def check_dir(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(
            f"'{path}' is not a valid directory"
        )
    return path


def open_folder(path):
    system = platform.system()

    if system == "Windows":
        os.startfile(path)
    elif system == "Darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])


def prepend_folder_name_to_files(folder_path):
    folder_name = os.path.basename(folder_path)

    for filename in os.listdir(folder_path):
        old_file_path = os.path.join(
            folder_path,
            filename
        )

        if not os.path.isfile(old_file_path):
            continue

        # Prevent double-prefixing
        if filename.startswith(f"{folder_name}_"):
            continue

        new_filename = (
            f"{folder_name}_{filename}"
        )

        new_file_path = os.path.join(
            folder_path,
            new_filename
        )

        os.rename(
            old_file_path,
            new_file_path
        )

        print(
            f"Renamed: {filename} -> {new_filename}"
        )


def process_directory(directory):
    for root, _, _ in os.walk(directory):
        prepend_folder_name_to_files(root)

    print("\nRENAMING COMPLETE!")

    open_folder(directory)


def main():
    parser = argparse.ArgumentParser(
        description="Prepend each file with its parent folder name.",
        usage="python %(prog)s DIRECTORY"
    )

    parser.add_argument(
        "directory",
        type=check_dir,
        help="Directory to process recursively"
    )

    args = parser.parse_args()

    process_directory(args.directory)


if __name__ == "__main__":
    main()