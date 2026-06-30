#!/usr/bin/env python3
"""Crop the real photos out of the original reference screenshots into assets/.

No standalone source photos exist on disk -- only the reference screenshots in
`betina website maping/`. The _1109.png files are exactly 1109x691, i.e. a 1:1
match to the measurement frame, so photo regions crop with their frame pixels
directly. The home hero is the 1536x1024 original, a uniform 1536/1109 upscale of
the frame (origin 0,0), so its boxes are frame-px * 1.385.
"""
import pathlib
from PIL import Image

HERE = pathlib.Path(__file__).parent
REF = pathlib.Path("/Users/alonbenzion/Downloads/betina website maping")
OUT = HERE / "assets"
OUT.mkdir(exist_ok=True)

H = 1536 / 1109  # home hero upscale factor

def crop(src, box, name, q=90):
    x, y, w, h = box
    im = Image.open(REF / src).convert("RGB")
    x2 = min(x + w, im.width); y2 = min(y + h, im.height)
    im.crop((x, y, x2, y2)).save(OUT / name, quality=q)
    print("%-22s <- %-16s (%d,%d %dx%d)" % (name, src, x, y, x2 - x, y2 - y))

# ---- home hero (1536x1024): frame-px * 1.385 ----
def hb(fx, fy, fw, fh):
    return (round(fx * H), round(fy * H), round(fw * H), round(fh * H))
crop("website home2.png", hb(30, 214, 422, 460), "home-portrait.jpg")
crop("website home2.png", hb(461, 215, 197, 203), "home-swatch.jpg")
crop("website home2.png", hb(616, 417, 192, 270), "home-airbrush.jpg")
crop("website home2.png", hb(809, 417, 301, 270), "home-group.jpg")

# ---- reviews (2_1109) ----
crop("2_1109.png", (3, 43, 523, 644), "reviews-community.jpg")

# ---- methods (3_1109) ----
crop("3_1109.png", (464, 475, 308, 216), "methods-bronzed.jpg")

# ---- glimpse (4_1109) ----
crop("4_1109.png", (507, 0, 297, 228), "glimpse-studio.jpg")
crop("4_1109.png", (0, 242, 799, 449), "glimpse-group.jpg")

# ---- colors (5_1109): portrait + 5 shade swatches down the right column ----
crop("5_1109.png", (1, 104, 402, 552), "colors-portrait.jpg")
for i, y in enumerate((116, 226, 336, 446, 556), start=1):
    crop("5_1109.png", (951, y, 126, 92), "colors-swatch%02d.jpg" % i)

# ---- pricing (6_1109) ----
crop("6_1109.png", (486, 140, 372, 328), "pricing-custom.jpg")

# ---- group (7_1109) ----
crop("7_1109.png", (0, 23, 1109, 668), "group-squad.jpg")

print("\nDone ->", OUT)
