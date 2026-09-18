#!/usr/bin/env python3
"""Shrink an image to fit under a target size in KB."""
import argparse
import io
from pathlib import Path

from PIL import Image


def _binary_search_quality(img: Image.Image, fmt: str, target_bytes: int, **save_kwargs):
    lo, hi = 1, 95
    best_buf, best_q = None, lo
    while lo <= hi:
        mid = (lo + hi) // 2
        buf = io.BytesIO()
        img.save(buf, format=fmt, quality=mid, optimize=True, **save_kwargs)
        if len(buf.getvalue()) <= target_bytes:
            best_buf, best_q = buf, mid
            lo = mid + 1
        else:
            hi = mid - 1
    if best_buf is None:
        buf = io.BytesIO()
        img.save(buf, format=fmt, quality=1, optimize=True, **save_kwargs)
        best_buf, best_q = buf, 1
    return best_buf, best_q


def _binary_search_colors(img: Image.Image, target_bytes: int):
    rgb = img.convert("RGB")
    lo, hi = 2, 256
    best_buf, best_colors = None, hi
    while lo <= hi:
        mid = (lo + hi) // 2
        quantized = rgb.quantize(colors=mid)
        buf = io.BytesIO()
        quantized.save(buf, format="PNG", optimize=True)
        if len(buf.getvalue()) <= target_bytes:
            best_buf, best_colors = buf, mid
            lo = mid + 1
        else:
            hi = mid - 1
    if best_buf is None:
        quantized = rgb.quantize(colors=2)
        buf = io.BytesIO()
        quantized.save(buf, format="PNG", optimize=True)
        best_buf, best_colors = buf, 2
    return best_buf, best_colors


def reduce_to_size(input_path, output_path, target_kb: int) -> dict:
    target_bytes = target_kb * 1024
    img = Image.open(input_path)
    fmt = (Path(output_path).suffix.lstrip(".").upper() or img.format).replace("JPG", "JPEG")

    if fmt in ("JPEG", "WEBP"):
        if img.mode in ("RGBA", "P") and fmt == "JPEG":
            img = img.convert("RGB")
        buf, setting = _binary_search_quality(img, fmt, target_bytes)
        setting_name = "quality"
    elif fmt == "PNG":
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        if len(buf.getvalue()) <= target_bytes:
            setting = 256
        else:
            buf, setting = _binary_search_colors(img, target_bytes)
        setting_name = "colors"
    else:
        buf = io.BytesIO()
        try:
            img.save(buf, format=fmt, optimize=True)
        except TypeError:
            buf = io.BytesIO()
            img.save(buf, format=fmt)
        setting = None
        setting_name = None

    data = buf.getvalue()
    Path(output_path).write_bytes(data)
    size_kb = len(data) / 1024
    return {
        "size_kb": size_kb,
        "setting_name": setting_name,
        "setting_value": setting,
        "hit_target": size_kb <= target_kb,
    }


def _prompt_target_kb() -> int:
    while True:
        raw = input("Target size in KB: ").strip()
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("Enter a positive whole number.")


def _prompt_input_path() -> Path:
    while True:
        raw = input("Path to the image: ").strip().strip('"')
        path = Path(raw)
        if path.is_file():
            return path
        print(f"No file at {path!s}, try again.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="path to the source image (prompts if omitted)")
    parser.add_argument("--target-kb", type=int, help="max output size in KB (prompts if omitted)")
    parser.add_argument("-o", "--output", help="output path (default: <name>_reduced<ext>)")
    args = parser.parse_args()

    in_path = Path(args.input) if args.input else _prompt_input_path()
    out_path = Path(args.output) if args.output else in_path.with_name(f"{in_path.stem}_reduced{in_path.suffix}")
    target_kb = args.target_kb if args.target_kb else _prompt_target_kb()

    result = reduce_to_size(in_path, out_path, target_kb)

    print(f"Wrote {out_path} ({result['size_kb']:.1f} KB)")
    if result["setting_name"]:
        print(f"  {result['setting_name']}={result['setting_value']}")
    if not result["hit_target"]:
        print(f"  WARNING: could not reach {target_kb} KB target at the smallest allowed setting")


if __name__ == "__main__":
    main()
