#!/usr/bin/env python3
"""
ASCII Art Generator (Pillow)

- Takes an image path from the command line.
- Resizes it to N characters wide (keeps aspect ratio) and converts to grayscale.
- Maps each pixel's brightness to a character set (default '.:-=+*#%@').
- Prints the ASCII art to the console.

Usage:
  python ascii_art.py /path/to/image.jpg
  python ascii_art.py --width 120 --char ".:-=+*#%@" image.png
"""

import argparse
import sys
from typing import Iterable
from PIL import Image, ImageOps, UnidentifiedImageError


# --- validators for argparse ---
def positive_int(x: str) -> int:
    try:
        v = int(x)
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer")
    if v <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return v

def char_string(s: str) -> str:
    if not s:
        raise argparse.ArgumentTypeError("char set must be a non-empty string")
    return s


# --- Step 1: resize & grayscale ---
def resize_to_width_grayscale(img: Image.Image, target_width: int = 100) -> Image.Image:
    """Resize to target_width (keep aspect) and convert to grayscale ('L')."""
    img = ImageOps.exif_transpose(img)
    w, h = img.size
    if w <= 0 or h <= 0:
        raise ValueError("Input image has invalid dimensions")
    scale = target_width / float(w)
    target_height = max(1, int(round(h * scale)))
    resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    return resized.convert("L")


# --- Step 2: pixel → character mapping ---
def pixel_to_char(value: int, charset: str = ".:-=+*#%@") -> str:
    """
    Map a grayscale pixel (0-255) to a character from `charset`.

    Assumes `charset` ordered lightest→darkest (so 255→charset[0], 0→charset[-1]).
    """
    if not charset:
        raise ValueError("charset must be non-empty")
    v = 0 if value < 0 else 255 if value > 255 else int(value)
    last = len(charset) - 1
    idx = last - (v * last // 255)
    return charset[idx]


def pixels_to_ascii_lines(pixels: Iterable[int], width: int, charset: str) -> Iterable[str]:
    """Convert a flat iterable of grayscale pixels to ASCII rows."""
    px = list(pixels)
    for row_start in range(0, len(px), width):
        row = px[row_start:row_start + width]
        yield "".join(pixel_to_char(p, charset) for p in row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert an image to ASCII art.")
    parser.add_argument("path", help="Path to the image file")
    parser.add_argument("--width", type=positive_int, default=100, metavar="N",
                        help="Target width in characters (default: %(default)s)")
    parser.add_argument("--char", type=char_string, default=".:-=+*#%@",
                        help="Character set (lightest→darkest). Quote it if it has spaces.")
    parser.add_argument("--invert", action="store_true",
                        help="Invert the character set (darkest→lightest)")
    parser.add_argument("--stretch", action="store_true",
                        help="Duplicate each row (compensate console aspect ratio)")
    args = parser.parse_args()

    charset = args.char[::-1] if args.invert else args.char

    try:
        with Image.open(args.path) as im:
            gray = resize_to_width_grayscale(im, args.width)
            lines = list(pixels_to_ascii_lines(gray.getdata(), gray.width, charset))
    except FileNotFoundError:
        print(f"Error: file not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    except UnidentifiedImageError:
        print(f"Error: not a recognized image file: {args.path}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error processing image: {e}", file=sys.stderr)
        sys.exit(3)

    if args.stretch:
        for line in lines:
            print(line)
            print(line)
    else:
        for line in lines:
            print(line)


if __name__ == "__main__":
    main()
