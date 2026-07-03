"""
Move duplicate files in a directory tree into a DUPLICATE folder.

Files are considered duplicates if their contents are identical
(MD5 hash match). The first occurrence is kept in place; subsequent
duplicates are moved to the DUPLICATE folder.

Usage:
    python separate_duplicate_files.py DIRECTORY
"""

import os
import hashlib
import shutil
import argparse
import platform
import subprocess


def check_dir(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(
            f"'{path}' is not a valid directory"
        )
    return path


def hash_file(file_path):
    hasher = hashlib.md5()

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()


def create_duplicate_dir(directory):
    duplicate_dir = os.path.join(directory, "DUPLICATE")
    os.makedirs(duplicate_dir, exist_ok=True)

    return duplicate_dir


def get_unique_destination_file_path(duplicate_dir, filename):
    destination = os.path.join(duplicate_dir, filename)

    if not os.path.exists(destination):
        return destination

    base, ext = os.path.splitext(filename)
    counter = 1

    while os.path.exists(destination):
        destination = os.path.join(
            duplicate_dir,
            f"{base}_{counter}{ext}"
        )
        counter += 1

    return destination


def move_duplicate_file(file_path, duplicate_dir):
    filename = os.path.basename(file_path)

    destination = get_unique_destination_file_path(
        duplicate_dir,
        filename
    )

    shutil.move(file_path, destination)

    print(f"Moved duplicate: {file_path}")


def check_duplicate_and_move(file_path, duplicate_dir, seen_hashes):
    file_hash = hash_file(file_path)

    if file_hash in seen_hashes:
        move_duplicate_file(file_path, duplicate_dir)
        return 1

    seen_hashes[file_hash] = file_path
    return 0


def open_folder(path):

    system = platform.system()

    if system == "Windows":
        os.startfile(path)
    elif system == "Darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])


def find_duplicates(directory):
    duplicate_dir = create_duplicate_dir(directory)

    seen_hashes = {}
    duplicates_found = 0

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != "DUPLICATE"]

        for filename in files:
            file_path = os.path.join(root, filename)

            duplicates_found += check_duplicate_and_move(
                file_path,
                duplicate_dir,
                seen_hashes
            )

    print(
        f"\nCompleted. {duplicates_found} duplicate file(s) moved to {duplicate_dir}"
    )

    if duplicates_found:
        open_folder(duplicate_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Move duplicate files into a DUPLICATE folder.",
        usage="python %(prog)s DIRECTORY"
    )

    parser.add_argument(
        "directory",
        type=check_dir,
        help="Directory to scan recursively for duplicate files"
    )

    args = parser.parse_args()

    find_duplicates(args.directory)


if __name__ == "__main__":
    main()