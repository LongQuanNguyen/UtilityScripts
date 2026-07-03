"""
Organize files into category folders based on file extension.

Files from all subdirectories are first moved into the root directory,
then sorted into category folders such as image, video, audio,
document, compressed, executable, and miscellaneous.

Usage:
    python organize_files_by_type.py DIRECTORY
"""

import os
import shutil
import argparse
import platform
import subprocess


SUPPORTED_TYPES = {
    "image": [
        ".jpg", ".jpeg", ".jfif", ".pjpeg", ".pjp",
        ".png", ".gif", ".webp", ".svg", ".apng",
        ".avif", ".psd", ".ico"
    ],

    "video": [
        ".webm", ".ts", ".mov", ".mp4",
        ".m4p", ".m4v", ".mkv"
    ],

    "audio": [
        ".aac", ".m4a", ".m4b",
        ".m4p", ".mp3", ".wav"
    ],

    "document": [
        ".doc", ".docx", ".pdf", ".rtf",
        ".txt", ".odt", ".ppt", ".pptx",
        ".pps", ".tex", ".xls", ".xlsm",
        ".xlsx"
    ],

    "compressed": [
        ".7z", ".rar", ".zip"
    ],

    "executable": [
        ".apk", ".bat", ".exe", ".jar",
        ".py", ".msi", ".sh", ".ipa"
    ]
}


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


def move_file_with_duplicate_check(src_path, dest_dir):
    base, ext = os.path.splitext(
        os.path.basename(src_path)
    )

    destination = os.path.join(
        dest_dir,
        os.path.basename(src_path)
    )

    counter = 1

    while os.path.exists(destination):
        destination = os.path.join(
            dest_dir,
            f"{base}_{counter}{ext}"
        )
        counter += 1

    shutil.move(src_path, destination)


def move_files_to_main_folder(main_folder):
    for root, dirs, files in os.walk(main_folder):
        dirs[:] = [
            d for d in dirs
            if os.path.join(root, d) != main_folder
        ]

        for file in files:
            file_path = os.path.join(root, file)

            if root != main_folder:
                move_file_with_duplicate_check(
                    file_path,
                    main_folder
                )


def get_category(file_extension):
    file_extension = file_extension.lower()

    for category, extensions in SUPPORTED_TYPES.items():
        if file_extension in extensions:
            return category

    return "miscellaneous"


def sort_files_into_subdirectories(main_folder):
    for file in os.listdir(main_folder):
        file_path = os.path.join(
            main_folder,
            file
        )

        if not os.path.isfile(file_path):
            continue

        category = get_category(
            os.path.splitext(file)[1]
        )

        category_dir = os.path.join(
            main_folder,
            category
        )

        os.makedirs(
            category_dir,
            exist_ok=True
        )

        move_file_with_duplicate_check(
            file_path,
            category_dir
        )


def organize_files(main_folder):
    print("\nProcessing...")

    move_files_to_main_folder(main_folder)

    sort_files_into_subdirectories(
        main_folder
    )

    print("\nORGANIZING COMPLETE!")

    open_folder(main_folder)


def main():
    parser = argparse.ArgumentParser(
        description="Organize files into folders by file type.",
        usage="python %(prog)s DIRECTORY"
    )

    parser.add_argument(
        "directory",
        type=check_dir,
        help="Directory containing files to organize"
    )

    args = parser.parse_args()

    organize_files(
        args.directory
    )


if __name__ == "__main__":
    main()