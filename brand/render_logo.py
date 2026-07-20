#!/usr/bin/env python3
"""Kinetic Reduction — Focus Funnel logo render (Pillow, no external renderer)."""
import os
from PIL import Image, ImageDraw, ImageFont

FONTS = os.path.expanduser("~/.claude/skills/canvas-design/canvas-fonts")
OUT   = "/Users/samxl/Documents/Claude Code/focus-funnel/brand"
BIG   = os.path.join(FONTS, "BigShoulders-Bold.ttf")
MONO  = os.path.join(FONTS, "DMMono-Regular.ttf")

INK   = (11, 11, 13, 255)      # #0b0b0d
INK2  = (15, 16, 20, 255)      # #0f1014
LIME  = (200, 240, 0, 255)     # #c8f000
DEEP  = (143, 184, 0, 255)     # #8fb800
PALE  = (238, 248, 192, 255)   # #eef8c0
OFF   = (244, 245, 247, 255)   # #f4f5f7

K = 0.15  # forward shear (~8.5 deg)

def rr(d, x0, y0, w, h, r, fill):
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=r, fill=fill)

def funnelF(size, color, bg=None, pad=0):
    """Custom funnel-F glyph as its own RGBA image (unsheared).
    Glyph units 0..46 x 0..72; bars step inward (34 -> 23) = F + funnel."""
    s = size / 72.0
    W = int(46 * s) + pad * 2
    H = int(72 * s) + pad * 2
    img = Image.new("RGBA", (W, H), bg if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    def X(gx): return pad + gx * s
    def Y(gy): return pad + gy * s
    rad = max(1, int(1.7 * s))
    # spine, top bar (wide), mid bar (narrower) -> funnel taper
    rr(d, X(5),  Y(3),  12 * s, 66 * s, rad, color)   # spine
    rr(d, X(5),  Y(3),  34 * s, 12 * s, rad, color)   # top bar (mouth)
    rr(d, X(5),  Y(30), 23 * s, 12 * s, rad, color)   # mid bar (narrowed)
    return img

def shear(img, k=K):
    W, H = img.size
    dx = int(abs(k) * H)
    new_w = W + dx
    # output(x,y) samples input(x + k*y - k*H, y)
    return img.transform((new_w, H), Image.AFFINE, (1, k, -k * H, 0, 1, 0),
                         resample=Image.BICUBIC)

# ---------- 1. ICON MARK (square) ----------
def icon(px, sq_fill, glyph_color, fname):
    SS = 4
    N = px * SS
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(N * 0.235)
    d.rounded_rectangle([0, 0, N, N], radius=r, fill=sq_fill)
    g_h = int(N * 0.60)
    g = shear(funnelF(g_h, glyph_color, pad=SS))
    gx = (N - g.width) // 2 + int(N * 0.02)
    gy = (N - g.height) // 2
    img.alpha_composite(g, (gx, gy))
    img = img.resize((px, px), Image.LANCZOS)
    img.save(os.path.join(OUT, fname))
    return img

icon(1024, LIME, INK, "icon_mark.png")            # lime tile, ink F  (primary)
icon(1024, INK2, LIME, "icon_mark_dark.png")      # ink tile, lime F  (inverted)

# ---------- 2. WORDMARK ----------
def wordmark(fname, on_dark=True):
    SS = 4
    cap = 150 * SS
    font = ImageFont.truetype(BIG, cap)
    focus_col = OFF if on_dark else INK
    fun_col   = LIME if on_dark else DEEP
    # measure the non-F letters via the font
    def tw(s): return font.getbbox(s)[2]
    # baseline geometry
    fbb = font.getbbox("H")
    capH = fbb[3] - fbb[1]          # cap height in px
    baseline = capH + int(capH * 0.12)
    Fw = int(capH * (37 / 66.0))    # advance for our funnel-F
    track = int(cap * 0.02)
    word_gap = int(cap * 0.34)
    # layout: [F]OCUS  [F]UNNEL
    x = 0
    positions = []  # (type, payload, x, color)
    positions.append(("F", None, x, focus_col)); x += Fw + track
    positions.append(("T", "OCUS", x, focus_col)); x += tw("OCUS") + word_gap
    fstart = x
    positions.append(("F", None, x, fun_col)); x += Fw + track
    positions.append(("T", "UNNEL", x, fun_col)); x += tw("UNNEL")
    total_w = x
    H = baseline + int(capH * 0.30)
    img = Image.new("RGBA", (total_w + 8, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for typ, payload, px_, col in positions:
        if typ == "T":
            d.text((px_, baseline), payload, font=font, fill=col, anchor="ls")
        else:
            g = funnelF(capH, col, pad=SS)
            g_top = baseline - capH - fbb[1]  # align glyph top to cap top
            img.alpha_composite(g, (int(px_), int(g_top)))
    img = shear(img)
    # trim & downscale
    bbox = img.getbbox()
    img = img.crop(bbox)
    scale = 300.0 / img.height
    img = img.resize((int(img.width * scale), 300), Image.LANCZOS)
    img.save(os.path.join(OUT, fname))
    return img

wm_dark = wordmark("wordmark_on_dark.png", on_dark=True)
wm_light = wordmark("wordmark_on_light.png", on_dark=False)

# ---------- 3. BRAND PLATE (canvas-design hero) ----------
def plate():
    SS = 2
    W, H = 1600 * SS, 2000 * SS
    img = Image.new("RGBA", (W, H), INK)
    d = ImageDraw.Draw(img)
    M = 120 * SS
    grid = (200, 240, 0, 16)  # faint lime ticks
    # clinical baseline grid — fine ticks along the margins
    step = 40 * SS
    for gx in range(M, W - M + 1, step):
        d.line([gx, M, gx, M + 10 * SS], fill=grid, width=SS)
        d.line([gx, H - M - 10 * SS, gx, H - M], fill=grid, width=SS)
    for gy in range(M, H - M + 1, step):
        d.line([M, gy, M + 10 * SS, gy], fill=grid, width=SS)
        d.line([W - M - 10 * SS, gy, W - M, gy], fill=grid, width=SS)
    # frame hairline
    d.rectangle([M, M, W - M, H - M], outline=(200, 240, 0, 40), width=SS)
    # corner registration crosshairs
    def cross(cx, cy):
        L = 22 * SS
        d.line([cx - L, cy, cx + L, cy], fill=DEEP, width=SS)
        d.line([cx, cy - L, cx, cy + L], fill=DEEP, width=SS)
        d.ellipse([cx - 7 * SS, cy - 7 * SS, cx + 7 * SS, cy + 7 * SS], outline=DEEP, width=SS)
    for cx in (M, W - M):
        for cy in (M, H - M):
            cross(cx, cy)
    mono_s = ImageFont.truetype(MONO, 22 * SS)
    mono_m = ImageFont.truetype(MONO, 26 * SS)
    # top clinical header
    d.text((M + 30 * SS, M + 26 * SS), "IDENTITY SYSTEM / 01", font=mono_m, fill=DEEP, anchor="lm")
    d.text((W - M - 30 * SS, M + 26 * SS), "FIG. FF-01", font=mono_s, fill=DEEP, anchor="rm")
    # the icon mark, monumental, upper-center
    mark = Image.open(os.path.join(OUT, "icon_mark.png")).convert("RGBA")
    mk = 560 * SS
    mark = mark.resize((mk, mk), Image.LANCZOS)
    mx = (W - mk) // 2
    my = M + 150 * SS
    img.alpha_composite(mark, (mx, my))
    # spec ticks flanking the mark
    d.text((mx - 30 * SS, my), "0,0", font=mono_s, fill=DEEP, anchor="rm")
    d.text((mx + mk + 30 * SS, my + mk), "1024²", font=mono_s, fill=DEEP, anchor="lm")
    # caption under mark
    cap_y = my + mk + 44 * SS
    d.text((W // 2, cap_y), "FUNNEL-F  ·  MARK", font=mono_m, fill=OFF, anchor="mm")
    # wordmark, centered lower
    wm = Image.open(os.path.join(OUT, "wordmark_on_dark.png")).convert("RGBA")
    ww = int(W * 0.66)
    wh = int(wm.height * (ww / wm.width))
    wm = wm.resize((ww, wh), Image.LANCZOS)
    wy = cap_y + 90 * SS
    img.alpha_composite(wm, ((W - ww) // 2, wy))
    # thin lime rule
    ry = wy + wh + 80 * SS
    d.line([W // 2 - 300 * SS, ry, W // 2 + 300 * SS, ry], fill=LIME, width=2 * SS)
    # swatches + hex, bottom
    sw = 46 * SS
    sy = ry + 70 * SS
    swatches = [("#C8F000", LIME), ("#0B0B0D", INK2), ("#8FB800", DEEP), ("#F4F5F7", OFF)]
    total = len(swatches) * (sw + 190 * SS)
    sx = (W - total) // 2 + 30 * SS
    for hexc, col in swatches:
        d.rounded_rectangle([sx, sy, sx + sw, sy + sw], radius=8 * SS, fill=col,
                            outline=(200, 240, 0, 50), width=SS)
        d.text((sx + sw + 18 * SS, sy + sw // 2), hexc, font=mono_s, fill=OFF, anchor="lm")
        sx += sw + 190 * SS
    # footer tagline
    d.text((W // 2, H - M - 34 * SS), "FUNNEL MANY  >  FOCUS ONE",
           font=mono_m, fill=DEEP, anchor="mm")
    img = img.convert("RGB").resize((1600, 2000), Image.LANCZOS)
    img.save(os.path.join(OUT, "brand_plate.png"), quality=95)

plate()
print("done:", sorted(os.listdir(OUT)))
