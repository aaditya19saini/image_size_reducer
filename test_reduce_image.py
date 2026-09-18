"""Runnable self-check for reduce_image.py: python test_reduce_image.py"""
import io
import tempfile
from pathlib import Path

from PIL import Image

from reduce_image import reduce_to_size


def test_jpeg_hits_target():
    img = Image.new("RGB", (800, 800))
    for y in range(800):
        for x in range(0, 800, 8):
            img.putpixel((x, y), (x % 256, y % 256, (x * y) % 256))

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src.jpg"
        img.save(src, format="JPEG", quality=95)
        original_kb = src.stat().st_size / 1024

        target_kb = max(5, int(original_kb / 3))
        out = Path(tmp) / "out.jpg"
        result = reduce_to_size(src, out, target_kb)

        assert out.exists(), "output file was not written"
        actual_kb = out.stat().st_size / 1024
        assert actual_kb <= target_kb + 1, f"{actual_kb}KB exceeds target {target_kb}KB"
        assert result["hit_target"]


def test_png_quantize_fallback():
    img = Image.new("RGB", (400, 400))
    for y in range(400):
        for x in range(400):
            img.putpixel((x, y), (x % 256, y % 256, (x + y) % 256))

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src.png"
        img.save(src, format="PNG")

        out = Path(tmp) / "out.png"
        target_kb = 10
        reduce_to_size(src, out, target_kb)

        assert out.exists()
        Image.open(out).verify()


if __name__ == "__main__":
    test_jpeg_hits_target()
    test_png_quantize_fallback()
    print("OK")
