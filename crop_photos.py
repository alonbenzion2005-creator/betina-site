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

# ---- high-res originals dropped into Downloads (upgrades over screenshot crops) ----
DL = pathlib.Path("/Users/alonbenzion/Downloads")

def crop_abs(src_path, box, name, q=92):
    x, y, w, h = box
    im = Image.open(src_path).convert("RGB")
    x2 = min(x + w, im.width); y2 = min(y + h, im.height)
    im.crop((x, y, x2, y2)).save(OUT / name, quality=q)
    print("%-22s <- %-32s (%d,%d %dx%d)" % (name, src_path.name, x, y, x2 - x, y2 - y))

# glimpse big group: color hi-res (5472x3648). Box aspect 799/449=1.78 -> full width, bottom-aligned.
crop_abs(DL / "Everybody looking down color.jpg", (0, 573, 5472, 3075), "glimpse-group.jpg")

# Finny portrait (2962x4698): one tall photo split across the methods/glimpse seam.
# top band -> methods .pic (aspect 308/216=1.426); lower band continues into glimpse .pic-top (~1.35).
crop_abs(DL / "Finny bw ( 2 Pages).jpg", (30, 420, 2900, 2034), "methods-bronzed.jpg")
crop_abs(DL / "Finny bw ( 2 Pages).jpg", (30, 2454, 2900, 2148), "glimpse-studio.jpg")

# home hero portrait (p1, aspect 0.917): Betina seated with the gun (1510x2117)
crop_abs(DL / "First page me.jpg", (0, 120, 1510, 1646), "home-portrait.jpg")
# home airbrush detail (p3, aspect 0.711): hand + spray gun (2672x3875)
crop_abs(DL / "Me with gun.jpg", (0, 58, 2672, 3758), "home-airbrush.jpg")
# reviews community (aspect 0.812): the three of them, B&W (2344x2532)
crop_abs(DL / "Me, sienna Finny bw.jpg", (144, 0, 2056, 2532), "reviews-community.jpg")
# colors portrait (aspect 0.728): single B&W portrait (811x1273)
crop_abs(DL / "Sienna bw.jpg", (0, 80, 811, 1114), "colors-portrait.jpg")
# the squad lying in a circle (5472x3648): full-bleed group page + hero thumbnail
crop_abs(DL / "Lying in circle color.jpg", (0, 175, 5472, 3297), "group-squad.jpg")
crop_abs(DL / "Lying in circle color.jpg", (702, 0, 4068, 3648), "home-group.jpg")

print("\nDone ->", OUT)
