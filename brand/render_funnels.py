#!/usr/bin/env python3
"""Focus Funnel — funnel-first mark exploration (6 options) + simple wordmark."""
import os, math
from PIL import Image, ImageDraw, ImageFont

FONTS = os.path.expanduser("~/.claude/skills/canvas-design/canvas-fonts")
OUT   = "/Users/samxl/Documents/Claude Code/focus-funnel/brand"
SANS  = os.path.join(FONTS, "InstrumentSans-Bold.ttf")
MONO  = os.path.join(FONTS, "DMMono-Regular.ttf")

INK   = (11, 11, 13, 255)
INK2  = (15, 16, 20, 255)
LIME  = (200, 240, 0, 255)
DEEP  = (143, 184, 0, 255)
OFF   = (244, 245, 247, 255)

def thick_poly(d, pts, w, color, closed=False):
    """Polyline with round caps/joins."""
    r = w / 2
    seq = pts + [pts[0]] if closed else pts
    for a, b in zip(seq, seq[1:]):
        d.line([a, b], fill=color, width=int(w))
    for p in seq:
        d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=color)

def tile(bg):
    return Image.new("RGBA", (N, N), (0,0,0,0)), None

# each funnel drawn in 0..100 space, scaled by S = N/100
def draw_funnel(idx, d, S, fg, bg):
    def P(x, y): return (x*S, y*S)
    def rr(x0,y0,x1,y1,r,fill): d.rounded_rectangle([x0*S,y0*S,x1*S,y1*S], radius=r*S, fill=fill)
    w = 9*S
    if idx == 1:   # SOLID classic funnel + drop
        d.polygon([P(20,27),P(80,27),P(58,55),P(42,55)], fill=fg)
        rr(44,54,56,73,3,fg)
        d.ellipse([P(43.5,79)[0],P(43.5,79)[1],P(56.5,92)[0],P(56.5,92)[1]], fill=fg)
    elif idx == 2: # OPEN converging bars (V-funnel) + drop
        thick_poly(d, [P(18,29),P(50,60),P(82,29)], w, fg)
        thick_poly(d, [P(50,60),P(50,72)], w, fg)
        d.ellipse([P(43.5,79)[0],P(43.5,79)[1],P(56.5,92)[0],P(56.5,92)[1]], fill=fg)
    elif idx == 3: # MANY -> ONE (3 dots in, 1 out) + outline funnel
        for cx in (33,50,67):
            d.ellipse([P(cx-4.5,13)[0],P(cx-4.5,13)[1],P(cx+4.5,22)[0],P(cx+4.5,22)[1]], fill=fg)
        thick_poly(d, [P(25,30),P(75,30),P(56,54),P(56,66),P(44,66),P(44,54)], w*0.85, fg, closed=True)
        d.ellipse([P(43,78)[0],P(43,78)[1],P(57,92)[0],P(57,92)[1]], fill=fg)
    elif idx == 4: # NESTED chevrons (funnel of motion) — thinner + spaced
        cw = 6*S
        thick_poly(d, [P(26,31),P(50,45),P(74,31)], cw, fg)
        thick_poly(d, [P(34,45),P(50,59),P(66,45)], cw, fg)
        thick_poly(d, [P(42,59),P(50,72),P(58,59)], cw, fg)
        d.ellipse([P(45,80)[0],P(45,80)[1],P(55,90)[0],P(55,90)[1]], fill=fg)
    elif idx == 5: # DARK-TILE colorway — solid funnel, lime on ink
        d.polygon([P(20,27),P(80,27),P(58,55),P(42,55)], fill=fg)
        rr(44,54,56,73,3,fg)
        d.ellipse([P(43.5,79)[0],P(43.5,79)[1],P(56.5,92)[0],P(56.5,92)[1]], fill=fg)
    elif idx == 6: # MINIMAL thin-line funnel + solid drop
        thick_poly(d, [P(22,29),P(78,29),P(57,55),P(57,70),P(43,70),P(43,55)], 5*S, fg, closed=True)
        d.ellipse([P(43,78)[0],P(43,78)[1],P(57,92)[0],P(57,92)[1]], fill=fg)

LABELS = {1:"SOLID",2:"OPEN V",3:"MANY>ONE",4:"CHEVRON",5:"DARK TILE",6:"THIN LINE"}

def make_tile(idx, px=1024, invert=False):
    global N
    SS=4; N=px*SS; S=N/100.0
    img = Image.new("RGBA",(N,N),(0,0,0,0))
    d = ImageDraw.Draw(img)
    # idx 5 = dark colorway (ink tile, lime funnel); others = lime tile, ink funnel
    if idx==5:
        tile_fill=INK2; fg=LIME
    else:
        tile_fill = LIME if not invert else INK2
        fg = INK if not invert else LIME
    bg = tile_fill
    d.rounded_rectangle([0,0,N,N], radius=int(N*0.235), fill=tile_fill)
    draw_funnel(idx, d, S, fg, bg)
    return img.resize((px,px), Image.LANCZOS)

# individual tiles (lime tile, ink funnel)
for i in range(1,7):
    make_tile(i).save(os.path.join(OUT, f"funnel_{i:02d}.png"))

# ---- contact sheet ----
def grid():
    SS=2; W,H=1600*SS,2100*SS
    img=Image.new("RGB",(W,H),(11,11,13))
    d=ImageDraw.Draw(img)
    M=140*SS
    mono=ImageFont.truetype(MONO,26*SS)
    mono_s=ImageFont.truetype(MONO,22*SS)
    d.text((M, 70*SS), "FUNNEL MARKS / PICK ONE", font=mono, fill=DEEP, anchor="lm")
    d.text((W-M, 70*SS), "FIG. FN-01..06", font=mono_s, fill=DEEP, anchor="rm")
    tsz=440*SS
    gapx=(W-2*M-2*tsz)
    cols=[M, W-M-tsz]
    rows=[170*SS, 170*SS+(tsz+120*SS), 170*SS+2*(tsz+120*SS)]
    order=[1,2,3,4,5,6]
    for k,idx in enumerate(order):
        r=k//2; c=k%2
        x=cols[c]; y=rows[r]
        t=make_tile(idx, px=tsz).convert("RGBA")
        img.paste(t,(x,y),t)
        d.text((x+tsz//2, y+tsz+42*SS), f"{idx:02d}  {LABELS[idx]}", font=mono_s, fill=OFF, anchor="mm")
    # simple wordmark at bottom
    wf=ImageFont.truetype(SANS, 96*SS)
    y=rows[2]+tsz+150*SS
    focus="FOCUS "; fun="FUNNEL"
    fw=wf.getlength(focus); uw=wf.getlength(fun)
    total=fw+uw; sx=(W-total)//2
    d.text((sx, y), focus, font=wf, fill=OFF, anchor="lm")
    d.text((sx+fw, y), fun, font=wf, fill=LIME, anchor="lm")
    d.text((W//2, y+90*SS), "simple typography — funnel-first", font=mono_s, fill=DEEP, anchor="mm")
    img.resize((1600,2100), Image.LANCZOS).save(os.path.join(OUT,"funnel_grid.png"), quality=95)

grid()
print("done:", [f for f in sorted(os.listdir(OUT)) if f.startswith("funnel_")])
