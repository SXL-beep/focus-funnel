#!/usr/bin/env python3
"""
Generates Focus Funnel's app icons with zero dependencies (stdlib only).

Outputs:
  icon.svg            - resolution-independent favicon (browser tabs)
  icon-192.png        - PWA / Android icon
  icon-512.png        - PWA / Android splash + store icon
  apple-touch-icon.png - 180x180 iOS home-screen icon

Design: a downward funnel (brand orange) over a dark gradient, with a green
"top task" drop at the tip — echoing the app's accent colors. Full-bleed square
so iOS/Android masking looks clean.

Re-run with:  python3 make-icons.py
"""
import zlib, struct

# ---- geometry (fractions of the icon size), matched to icon.svg ----
TOP, MOUTH_L, MOUTH_R = 0.24, 0.18, 0.82
NECK_Y, NECK_L, NECK_R = 0.58, 0.45, 0.55
STEM_BOTTOM = 0.80
DOT_CX, DOT_CY, DOT_R = 0.50, 0.86, 0.07

# ---- colors ----
BG_TOP = (35, 42, 61)      # #232a3d
BG_BOT = (15, 17, 23)      # #0f1117
FN_TOP = (255, 150, 111)   # light orange
FN_BOT = (255, 106, 67)    # #ff6a43
GREEN  = (62, 207, 142)    # #3ecf8e


def lerp(a, b, t):
    return a + (b - a) * t


def lerp3(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def sample(fx, fy):
    """Return an opaque (r,g,b) for a normalized point in [0,1]x[0,1]."""
    # background vertical gradient
    color = lerp3(BG_TOP, BG_BOT, fy)

    # funnel body
    if TOP <= fy <= NECK_Y:
        t = (fy - TOP) / (NECK_Y - TOP)
        left = lerp(MOUTH_L, NECK_L, t)
        right = lerp(MOUTH_R, NECK_R, t)
        if left <= fx <= right:
            color = lerp3(FN_TOP, FN_BOT, fy)
    elif NECK_Y < fy <= STEM_BOTTOM:
        if NECK_L <= fx <= NECK_R:
            color = lerp3(FN_TOP, FN_BOT, fy)

    # green "top task" drop at the tip (drawn last, on top)
    dx, dy = fx - DOT_CX, fy - DOT_CY
    if dx * dx + dy * dy <= DOT_R * DOT_R:
        color = GREEN

    return color


def render_png(size):
    """Render an RGBA PNG with 2x2 supersampling for smooth edges."""
    rows = bytearray()
    inv = 1.0 / size
    for y in range(size):
        rows.append(0)  # PNG filter byte (none) per scanline
        for x in range(size):
            r = g = b = 0.0
            # 2x2 anti-aliasing samples
            for sy in (0.25, 0.75):
                for sx in (0.25, 0.75):
                    c = sample((x + sx) * inv, (y + sy) * inv)
                    r += c[0]; g += c[1]; b += c[2]
            rows += bytes((int(r / 4 + 0.5), int(g / 4 + 0.5), int(b / 4 + 0.5), 255))

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff))

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # 8-bit RGBA
    idat = zlib.compress(bytes(rows), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#232a3d"/><stop offset="1" stop-color="#0f1117"/>
    </linearGradient>
    <linearGradient id="fn" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ff966f"/><stop offset="1" stop-color="#ff6a43"/>
    </linearGradient>
  </defs>
  <rect width="100" height="100" rx="22" fill="url(#bg)"/>
  <path d="M18 24 L82 24 L55 58 L55 80 L45 80 L45 58 Z" fill="url(#fn)"/>
  <circle cx="50" cy="86" r="7" fill="#3ecf8e"/>
</svg>
"""


def main():
    with open("icon.svg", "w") as f:
        f.write(SVG)
    for name, size in [("icon-192.png", 192), ("icon-512.png", 512),
                       ("apple-touch-icon.png", 180)]:
        with open(name, "wb") as f:
            f.write(render_png(size))
        print(f"wrote {name} ({size}x{size})")
    print("wrote icon.svg")


if __name__ == "__main__":
    main()
