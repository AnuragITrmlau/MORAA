"""Create a synthetic test image: a gold ring with a single round red gemstone.

Used for controlled fidelity verification — the reference has clearly
identifiable features (gold band, round red stone on top, gold bezel,
prongs) that the generated image must preserve.
"""
from PIL import Image, ImageDraw, ImageFilter

W, H = 800, 800
img = Image.new("RGB", (W, H), (26, 26, 38))
d = ImageDraw.Draw(img)

# vertical gradient background
for y in range(H):
    t = y / H
    col = (int(26 + 34 * t), int(26 + 30 * t), int(38 + 34 * t))
    d.line([(0, y), (W, y)], fill=col)

# soft warm glow behind the ring
glow = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(glow)
gd.ellipse([300, 250, 500, 520], fill=95)
glow = glow.filter(ImageFilter.GaussianBlur(70))
img = Image.composite(Image.new("RGB", (W, H), (150, 118, 62)), img, glow)
d = ImageDraw.Draw(img)

cx, cy = 400, 440  # ring centre

# shadow under the ring
d.ellipse([cx - 240, cy - 90, cx + 240, cy + 170], fill=(14, 10, 4))
d.ellipse([cx - 224, cy - 130, cx + 224, cy + 150], fill=(46, 34, 12))

# ring band — thick gold ellipse (ring viewed at an angle)
d.ellipse([cx - 205, cy - 125, cx + 205, cy + 125], outline=(214, 178, 90), width=36)
d.ellipse([cx - 188, cy - 108, cx + 188, cy + 108], outline=(118, 88, 30), width=8)
d.arc([cx - 205, cy - 125, cx + 205, cy + 125], start=-65, end=25, fill=(255, 235, 155), width=12)
d.arc([cx - 205, cy - 125, cx + 205, cy + 125], start=150, end=200, fill=(150, 112, 48), width=8)

# gold bezel (setting) around the stone at the top of the band
bezel = [cx - 64, cy - 212, cx + 64, cy - 88]
d.ellipse(bezel, outline=(214, 178, 90), width=24)

# round red gemstone
stone = [cx - 47, cy - 195, cx + 47, cy - 101]
d.ellipse(stone, fill=(168, 22, 30))
d.ellipse(stone, outline=(222, 92, 80), width=6)

# stone facets / highlight
d.ellipse([cx - 32, cy - 183, cx + 2, cy - 149], fill=(255, 142, 120))
d.ellipse([cx - 41, cy - 148, cx + 6, cy - 116], fill=(118, 8, 14))

# four gold prongs holding the stone
for px, py in [(cx - 60, cy - 150), (cx + 60, cy - 150), (cx - 46, cy - 94), (cx + 46, cy - 94)]:
    d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(234, 198, 110))
    d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 230, 150))

img.save("test_ring.png")
print("saved test_ring.png", img.size)
