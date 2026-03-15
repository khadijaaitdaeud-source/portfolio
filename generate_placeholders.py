"""Generate placeholder PNGs for project images referenced in index.html.

This is useful when the real image downloads fail and the PNGs are corrupted.

Usage:
  python generate_placeholders.py

Requirements:
  pip install pillow

The script will scan index.html for <img src="images/*.png"> references and
create a simple placeholder PNG for each one (if it doesn't already exist).
"""

import re
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit(
        "Pillow is required. Install it with: python -m pip install pillow"
    )

OUTPUT_DIR = Path("images")
OUTPUT_DIR.mkdir(exist_ok=True)

INDEX = Path("index.html")
if not INDEX.exists():
    raise SystemExit("index.html not found in the current directory.")

html = INDEX.read_text(encoding="utf-8")
img_paths = re.findall(r'src="(images/[^"]+?\.png)"', html)
img_paths = sorted(set(img_paths))

if not img_paths:
    print("No PNG image references found in index.html.")
    raise SystemExit(0)

print(f"Found {len(img_paths)} PNG image references.")

# Try to load a default font; fallback to built-in if missing.
try:
    font = ImageFont.truetype("arial.ttf", size=40)
except Exception:
    font = ImageFont.load_default()

for rel in img_paths:
    dest = OUTPUT_DIR / Path(rel).name
    title = Path(rel).stem.replace("-", " ")

    # Create placeholder only if missing or if file appears corrupted.
    if dest.exists():
        # quick size check
        if dest.stat().st_size > 1000:
            print(f"Skipping existing file: {dest.name}")
            continue

    img = Image.new("RGBA", (960, 680), (14, 22, 41, 255))
    draw = ImageDraw.Draw(img)

    # Gradient overlay
    for i in range(img.height):
        alpha = int(40 * (i / img.height))
        draw.line([(0, i), (img.width, i)], fill=(2, 170, 255, alpha))

    # Render title
    bbox = draw.textbbox((0, 0), title, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((img.width - w) / 2, img.height * 0.38),
        title,
        font=font,
        fill=(255, 255, 255, 255),
    )

    subtitle = "Placeholder image"
    bbox2 = draw.textbbox((0, 0), subtitle, font=font)
    w2, h2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
    draw.text(
        ((img.width - w2) / 2, img.height * 0.52),
        subtitle,
        font=font,
        fill=(255, 255, 255, 180),
    )

    img.save(dest)
    print(f"Wrote {dest.name}")

print("Done. You can now open index.html to verify the placeholders display.")
