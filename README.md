# Image Size Reducer

A tiny script that shrinks a photo until it's under a size you choose, in KB.

## What you need first

1. **Python** installed. Check by opening a terminal and typing:
   ```
   python --version
   ```
   If that prints a version number (e.g. `Python 3.14.7`), you're set. If not, install Python from [python.org](https://www.python.org/downloads/) first.

2. **Pillow** (the image library this script uses). Install it with:
   ```
   pip install Pillow
   ```

## How to run it

1. Open a terminal.
2. Go to the folder with the script:
   ```
   cd path/to/this/folder
   ```
3. Run it:
   ```
   python reduce_image.py
   ```
4. It will ask you two questions:
   ```
   Path to the image: photo.jpg
   Target size in KB: 100
   ```
   Type the path to your image, press Enter, type the size you want in KB, press Enter.
5. Done. It writes a new file next to the original, e.g. `photo_reduced.jpg`, and tells you the final size.

## Skip the questions (optional, for scripting)

You can pass everything as arguments instead of typing it interactively:

```
python reduce_image.py photo.jpg --target-kb 100
```

Options:
- `--target-kb 100` — max size in KB (asked interactively if left out)
- `-o output.jpg` — where to save the result (default: `<name>_reduced.<ext>`)

## What it supports

- **JPEG / WebP** — reduces quality until the file fits your target size.
- **PNG** — tries lossless optimization first, then reduces colors if it's still too big.
- Other formats save as-is with basic optimization.

If your target is so small that even the lowest quality setting can't hit it, the script tells you and keeps the smallest version it could make — it won't fail silently.

## Checking it works

```
python test_reduce_image.py
```
Should print `OK`.
