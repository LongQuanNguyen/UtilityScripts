"""
Merge images into a single PDF, one image per page.
Each page is sized to exactly match its image's aspect ratio/pixel size
(scaled to a chosen DPI) — no white padding, no stretching/distortion.

Usage:
    python images_to_pdf.py -o output.pdf image1.jpg image2.png image3.jpg
    python images_to_pdf.py -o output.pdf ./folder_of_images
    python images_to_pdf.py -o output.pdf ./folder_of_images --dpi 150

Requirements:
    pip install pillow
"""

import argparse
import sys
import re
from pathlib import Path
from PIL import Image

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".gif"}

def natural_key(p: Path):
    parts = re.split(r"(\d+)", p.name)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def collect_images(paths):
    files = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files.extend(
                f for f in path.iterdir()
                if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
            )
        elif path.is_file():
            if path.suffix.lower() in SUPPORTED_EXTS:
                files.append(path)
            else:
                print(f"Skipping unsupported file: {path}", file=sys.stderr)
        else:
            print(f"Warning: path not found: {path}", file=sys.stderr)
    files.sort(key=natural_key)
    return files


def load_as_rgb(path: Path) -> Image.Image:
    """Load image, flatten transparency onto white only if it has alpha,
    otherwise keep as-is. Converts to RGB for PDF saving without altering
    the visible content or aspect ratio."""
    img = Image.open(path)

    # Respect EXIF orientation (common with phone photos)
    try:
        from PIL import ImageOps
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        return background
    else:
        return img.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description="Merge images into a PDF, one image per page, page size = image size.")
    parser.add_argument("inputs", nargs="+", help="Image files and/or folders containing images")
    parser.add_argument("-o", "--output", default="output.pdf", help="Output PDF path (default: output.pdf)")
    parser.add_argument("--dpi", type=int, default=200,
                         help="DPI used to convert pixel size to page size (default: 200). "
                              "Doesn't change image quality — only how 'big' the page appears when printed.")
    args = parser.parse_args()

    files = collect_images(args.inputs)
    if not files:
        print("No supported images found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(files)} image(s):")
    for f in files:
        print(f"  - {f}")

    images = [load_as_rgb(f) for f in files]

    first, rest = images[0], images[1:]
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    first.save(
        out_path,
        save_all=True,
        append_images=rest,
        resolution=args.dpi,
    )

    print(f"\nDone. Wrote {len(images)} page(s) to {out_path.resolve()}")


if __name__ == "__main__":
    main()