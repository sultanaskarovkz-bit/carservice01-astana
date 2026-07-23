# -*- coding: utf-8 -*-
"""Генерация фавиконов и OG-картинки для CarService 01 (без внешних растеризаторов)."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ASSETS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ASSETS)

RED   = (255, 46, 51)
AMBER = (255, 176, 32)
STEEL = (90, 103, 116)
DARK  = (10, 13, 18)
LINE  = (42, 51, 63)

def font(sz, bold=True):
    p = "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
    return ImageFont.truetype(p, sz)

# ---------- ICON (master 512, supersampled x2) ----------
def make_icon(pad_ratio=0.0):
    S = 1024
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # vertical gradient background inside rounded square
    grad = Image.new("RGB", (1, S))
    for y in range(S):
        t = y / S
        c = (int(20 + (10-20)*t), int(25 + (13-25)*t), int(34 + (18-34)*t))
        grad.putpixel((0, y), c)
    grad = grad.resize((S, S))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S-1, S-1], radius=int(S*0.22), fill=255)
    img.paste(grad, (0, 0), mask)
    # border
    d.rounded_rectangle([int(S*0.02), int(S*0.02), S-int(S*0.02), S-int(S*0.02)],
                        radius=int(S*0.205), outline=LINE, width=int(S*0.016))
    # gauge geometry
    cx, cy, r = S*0.5, S*0.58, S*0.30
    bbox = [cx-r, cy-r, cx+r, cy+r]
    w = int(S*0.066)
    # arc segments: steel -> amber -> red (redline on the right end)
    d.arc(bbox, 160, 330, fill=STEEL, width=w)
    d.arc(bbox, 330, 352, fill=AMBER, width=w)
    d.arc(bbox, 352, 380, fill=RED, width=w)
    # needle to redline (up-right)
    ang = math.radians(312)
    nx, ny = cx + math.cos(ang)*r*0.72, cy + math.sin(ang)*r*0.72
    d.line([cx, cy, nx, ny], fill=RED, width=int(S*0.043))
    # hub
    hr = S*0.062
    d.ellipse([cx-hr, cy-hr, cx+hr, cy+hr], fill=DARK, outline=RED, width=int(S*0.03))
    if pad_ratio:
        inset = int(S*pad_ratio)
        base = Image.new("RGBA", (S, S), DARK+(255,))
        small = img.resize((S-2*inset, S-2*inset), Image.LANCZOS)
        base.paste(small, (inset, inset), small)
        img = base
    return img

master = make_icon()
mask_master = make_icon(pad_ratio=0.14)

sizes = {
    "favicon-16.png": 16, "favicon-32.png": 32, "favicon-48.png": 48,
    "apple-touch-icon.png": 180, "icon-192.png": 192, "icon-512.png": 512,
}
for name, sz in sizes.items():
    im = master.resize((sz, sz), Image.LANCZOS)
    if name == "apple-touch-icon.png":  # iOS: no alpha
        bg = Image.new("RGB", (sz, sz), DARK); bg.paste(im, (0, 0), im); im = bg
    im.save(os.path.join(ASSETS, name))
mask_master.resize((512, 512), Image.LANCZOS).save(os.path.join(ASSETS, "maskable-512.png"))

# favicon.ico with multiple sizes (root)
master.resize((256, 256), Image.LANCZOS).save(
    os.path.join(ROOT, "favicon.ico"), sizes=[(16,16),(32,32),(48,48)])

# ---------- OG IMAGE 1200x630 ----------
W, H = 1200, 630
try:
    bg = Image.open(os.path.join(ROOT, "video", "head.jpg")).convert("RGB")
except Exception:
    bg = Image.new("RGB", (W, H), DARK)
# cover-fit
br = max(W/bg.width, H/bg.height)
bg = bg.resize((int(bg.width*br), int(bg.height*br)), Image.LANCZOS)
bg = bg.crop(((bg.width-W)//2, (bg.height-H)//2, (bg.width-W)//2+W, (bg.height-H)//2+H))
bg = bg.filter(ImageFilter.GaussianBlur(2))
# dark left-to-right + bottom gradient overlay
ov = Image.new("RGBA", (W, H), (0,0,0,0))
od = ImageDraw.Draw(ov)
for x in range(W):
    a = int(235 - 150*(x/W))          # darker on the left where text sits
    od.line([(x,0),(x,H)], fill=(6,8,11,max(a,60)))
for y in range(H):
    a = int(180*(y/H))
    od.line([(0,y),(W,y)], fill=(6,8,11,a))
base = Image.alpha_composite(bg.convert("RGBA"), ov)
d = ImageDraw.Draw(base)
# top status strip
d.line([(64,70),(64+150,70)], fill=RED, width=3)
d.text((64,84), "БОРТОВАЯ ДИАГНОСТИКА · АСТАНА", font=font(24), fill=(150,163,177))
# brand
f_brand = font(112)
d.text((60,150), "CarService ", font=f_brand, fill=(238,240,246))
w_cs = d.textlength("CarService ", font=f_brand)
d.text((60+w_cs,150), "01", font=f_brand, fill=RED)
# tagline
d.text((64,300), "СТО полного цикла · ремонт двигателей любой сложности", font=font(34, False), fill=(224,230,236))
# service chips
chips = ["Двигатель","Ходовая","Электрика","Инжектор","Диагностика"]
x = 64; y = 372
for c in chips:
    tw = d.textlength(c, font=font(26))
    d.rounded_rectangle([x, y, x+tw+34, y+50], radius=10, outline=LINE, width=2, fill=(15,20,27))
    d.text((x+17, y+11), c, font=font(26), fill=(180,190,200))
    x += tw + 34 + 12
# bottom bar: phone + site
d.line([(64,H-92),(W-64,H-92)], fill=LINE, width=2)
d.text((64,H-70), "+7 707 696 9305", font=font(38), fill=(255,255,255))
site = "carservice01.kz"
d.text((W-64-d.textlength(site, font=font(34)), H-66), site, font=font(34), fill=RED)
base.convert("RGB").save(os.path.join(ASSETS, "og-image.jpg"), quality=86, optimize=True)

print("OK", sorted(os.listdir(ASSETS)))
