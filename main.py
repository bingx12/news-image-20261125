#!/usr/bin/env python3
"""THE WORLD TODAY - front page of Wednesday 25 November 2026.

Pure-stdlib Python 3.13. Draws the day's world news as a one-page
newspaper front page and writes /output/entry.png (1024x1024 PNG, under
1 MiB). No network, no clock, no randomness: every run writes identical
bytes. Text comes from bitmap glyphs in font_data.py (DejaVu Sans Book +
Bold rendered once at 64px, scaled at runtime); the PNG is encoded here
with zlib. Run from anywhere: `python3 main.py`.
"""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from font_data import BASE_SIZE, BASELINE, FONT_BOOK, FONT_BOLD

W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (20, 20, 20)
RED = (179, 32, 44)
BLUE = (29, 78, 137)
NAVY = (13, 27, 62)
SKY = (38, 68, 128)
GOLD = (198, 142, 32)
GREY = (96, 96, 92)
LIGHT = (232, 226, 214)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.put(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= r * r:
                    self.put(xx, yy, c)

    def triangle(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) // (by - ay))
            if len(xs) >= 2:
                self.rect(min(xs), yy, max(xs) - min(xs) + 1, 1, c)


# ---------------------------------------------------------------- text

def glyph(font, ch):
    return font.get(ch) or font[" "]


def text_width(s, size, bold=False):
    font = FONT_BOLD if bold else FONT_BOOK
    total = 0
    for ch in s:
        total += glyph(font, ch)[0] * size // BASE_SIZE
    return total


def draw_text(cv, x, y, s, size, bold=False, color=INK):
    """Draw s with its baseline at y, starting at x. Returns end x."""
    font = FONT_BOLD if bold else FONT_BOOK
    cx = x
    for ch in s:
        adv, w, h, xoff, yoff, bits = glyph(font, ch)
        out_w = w * size // BASE_SIZE
        out_h = h * size // BASE_SIZE
        if out_w and out_h:
            raw = bytes.fromhex(bits)
            top = y + (yoff - BASELINE) * size // BASE_SIZE
            left = cx + xoff * size // BASE_SIZE
            for dy in range(out_h):
                sy0 = dy * BASE_SIZE // size
                sy1 = max(sy0 + 1, (dy + 1) * BASE_SIZE // size)
                for dx in range(out_w):
                    sx0 = dx * BASE_SIZE // size
                    sx1 = max(sx0 + 1, (dx + 1) * BASE_SIZE // size)
                    hit = False
                    for sy in range(sy0, min(sy1, h)):
                        base = sy * w
                        for sx in range(sx0, min(sx1, w)):
                            bit = base + sx
                            if raw[bit // 8] & (0x80 >> (bit % 8)):
                                hit = True
                                break
                        if hit:
                            break
                    if hit:
                        cv.put(left + dx, top + dy, color)
        cx += adv * size // BASE_SIZE
    return cx


def fit_size(s, maxw, bold=False, start=60):
    size = start
    while size > 8 and text_width(s, size, bold) > maxw:
        size -= 1
    return size


def wrap(s, size, bold, maxw):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, size, bold) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(cv, x, y, s, size, bold, maxw, lh, color=INK):
    for line in wrap(s, size, bold, maxw):
        draw_text(cv, x, y, line, size, bold, color)
        y += lh
    return y


def centered(cv, y, s, size, bold=False, color=INK):
    draw_text(cv, (W - text_width(s, size, bold)) // 2, y, s, size, bold, color)


# ---------------------------------------------------------------- art

STARS = [(52, 252), (96, 268), (150, 244), (210, 258), (268, 242),
         (330, 262), (392, 248), (448, 270), (500, 246), (556, 264),
         (74, 300), (180, 312), (300, 306), (420, 318), (520, 300),
         (120, 350), (240, 344), (360, 352), (470, 346), (560, 330),
         (90, 400), (200, 408), (330, 402), (460, 410), (540, 396)]


def draw_rocket_scene(cv, x, y, w, h):
    cv.rect(x, y, w, h, NAVY)
    for i, (sx, sy) in enumerate(STARS):
        cv.put(x + sx, y + sy, (255, 255, 255))
        if i % 3 == 0:
            cv.put(x + sx + 1, y + sy, (220, 220, 240))
    # Earth arc along the bottom, clipped to the art box
    ecx, ecy, er = x + w // 2, y + h + 150, 210
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            d = (xx - ecx) ** 2 + (yy - ecy) ** 2
            if d <= er * er:
                cv.put(xx, yy, (28, 90, 160))
            elif d <= (er + 3) ** 2:
                cv.put(xx, yy, (90, 160, 220))
    # Tiangong station, upper right
    sx, sy = x + w - 190, y + 26
    cv.rect(sx, sy + 12, 96, 14, (200, 205, 215))
    cv.rect(sx + 30, sy, 36, 38, (170, 175, 190))
    cv.rect(sx - 52, sy + 8, 52, 5, (40, 90, 180))
    cv.rect(sx + 96, sy + 8, 52, 5, (40, 90, 180))
    cv.rect(sx - 52, sy + 16, 52, 5, (40, 90, 180))
    cv.rect(sx + 96, sy + 16, 52, 5, (40, 90, 180))
    # Rocket, centre-left, climbing
    rx, ry = x + 150, y + 62
    cv.triangle([(rx, ry), (rx - 16, ry + 34), (rx + 16, ry + 34)], RED)
    cv.rect(rx - 16, ry + 34, 32, 74, (240, 240, 238))
    cv.rect(rx - 16, ry + 34, 32, 6, RED)
    cv.rect(rx - 22, ry + 74, 6, 26, (200, 200, 198))
    cv.rect(rx + 16, ry + 74, 6, 26, (200, 200, 198))
    cv.circle(rx, ry + 56, 8, (38, 68, 128))
    cv.ring(rx, ry + 56, 8, INK, 2)
    cv.triangle([(rx - 12, ry + 108), (rx + 12, ry + 108), (rx, ry + 158)],
                (255, 140, 40))
    cv.triangle([(rx - 6, ry + 108), (rx + 6, ry + 108), (rx, ry + 138)],
                (255, 210, 80))


def draw_flags(cv, x, y):
    # Australia: blue field, simplified canton, stars
    cv.rect(x, y, 58, 30, (0, 40, 104))
    cv.rect(x, y, 29, 15, (200, 16, 46))
    cv.hline(x, y + 7, 29, (255, 255, 255), 3)
    cv.vline(x + 14, y, 15, (255, 255, 255), 3)
    cv.line(x, y, x + 28, y + 14, (255, 255, 255), 2)
    cv.line(x + 28, y, x, y + 14, (255, 255, 255), 2)
    for dx, dy in ((44, 8), (50, 16), (38, 20), (48, 24)):
        cv.put(x + dx, y + dy, (255, 255, 255))
    # Solomon Islands: blue over green, yellow diagonal, stars
    fx = x + 70
    cv.rect(fx, y, 58, 30, (0, 90, 160))
    cv.triangle([(fx, y + 30), (fx + 58, y), (fx + 58, y + 30)], (0, 130, 70))
    cv.line(fx, y + 30, fx + 58, y, (255, 210, 0), 3)
    for dx, dy in ((12, 8), (22, 6), (30, 12), (16, 16), (26, 20)):
        cv.put(fx + dx, y + dy, (255, 255, 255))
    cv.rect(x - 1, y - 1, 59, 1, INK)
    cv.rect(x - 1, y + 30, 59, 1, INK)
    cv.rect(x - 1, y - 1, 1, 32, INK)
    cv.rect(x + 58, y - 1, 1, 32, INK)
    cv.rect(fx - 1, y - 1, 59, 1, INK)
    cv.rect(fx - 1, y + 30, 59, 1, INK)
    cv.rect(fx - 1, y - 1, 1, 32, INK)
    cv.rect(fx + 58, y - 1, 1, 32, INK)


def draw_chart(cv, x, y, w, h):
    pts = [(x + 4, y + 6), (x + 26, y + 12), (x + 48, y + 10),
           (x + 70, y + 22), (x + 92, y + 30), (x + w - 4, y + h - 6)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, RED, 3)
    for px, py in pts:
        cv.circle(px, py, 3, RED)


# ---------------------------------------------------------------- page

LEAD_BODY = (
    "China's Shenzhou-24 roared off its pad at Jiuquan at 00:18 UTC, "
    "carrying commander Tang Hongbo, flight engineer Wu Yi and Pakistan's "
    "Muhammad Zeeshan Ali - the first Pakistani, and the first foreign "
    "astronaut, to visit China's Tiangong station. The crew docked at "
    "11:56 Beijing time for a week of experiments in orbit."
)

PACIFIC_BODY = (
    "Anthony Albanese and Matthew Wale signed the Australia-Solomon "
    "Islands Treaty in Canberra. Honiara names Australia its primary "
    "security partner and vows no foreign military base on its soil."
)

HUAWEI_BODY = (
    "A Brooklyn jury found Huawei guilty on 10 of 12 counts - bank fraud, "
    "wire fraud, sanctions violations and conspiring to steal trade "
    "secrets, including Cisco router code. Sentencing is set for "
    "September 2027."
)

MARKETS_BODY = (
    "Nvidia fell about 7% as lawmakers questioned President Trump's role "
    "in reinstating Jensen Huang. Tokyo's Nikkei slid 2.76% and SoftBank "
    "plunged 15%."
)

SPAIN_BODY = (
    "Pedro Sanchez and Alberto Nunez Feijoo clashed in a televised debate "
    "four days before Sunday's snap election. The PP leads the polls but "
    "may need far-right Vox to govern."
)

ALSO = [
    "CARTAGENA: special forces free all hostages after a 20-hour siege; one gunman killed.",
    "SENEGAL: CAS hands back the Africa Cup title, overturning the ruling that gave it to Morocco.",
    "PUTIN vows retaliation for Ukraine's refinery strikes; ZELENSKIY confirms the Baltic ship hit.",
]


def build():
    cv = Canvas(W, H, PAPER)
    M = 28
    # masthead
    cv.hline(M, 10, W - 2 * M, INK, 3)
    size = fit_size("THE WORLD TODAY", W - 2 * M, True, 84)
    centered(cv, 84, "THE WORLD TODAY", size, True)
    cv.hline(M, 96, W - 2 * M, INK, 2)
    centered(cv, 122, "WEDNESDAY 25 NOVEMBER 2026", 26, True)
    cv.hline(M, 132, W - 2 * M, INK, 2)
    # lead kicker + headline
    draw_text(cv, M, 164, "SPACE - CHINA", 20, True, RED)
    draw_text(cv, W - M - text_width("THE DAY IN ONE PAGE", 20, True),
              164, "THE DAY IN ONE PAGE", 20, True, GREY)
    s1 = fit_size("PAKISTAN REACHES ORBIT", W - 2 * M, True, 48)
    draw_text(cv, M, 208, "PAKISTAN REACHES ORBIT", s1, True)
    s2 = fit_size("SHENZHOU-24 DOCKS AT TIANGONG", W - 2 * M, True, 48)
    draw_text(cv, M, 252, "SHENZHOU-24 DOCKS AT TIANGONG", s2, True)
    # lead art + body
    draw_rocket_scene(cv, M, 266, 572, 234)
    bx = M + 572 + 16
    para(cv, bx, 290, LEAD_BODY, 18, False, W - M - bx, 23)
    cv.hline(M, 516, W - 2 * M, INK, 2)
    # row 2: two columns
    colw = (W - 2 * M - 32) // 2
    y = 532
    draw_text(cv, M, y + 18, "THE PACIFIC", 18, True, RED)
    draw_flags(cv, M + colw - 128, y + 2)
    s = fit_size("SOLOMONS CHOOSE AUSTRALIA", colw, True, 30)
    draw_text(cv, M, y + 52, "SOLOMONS CHOOSE AUSTRALIA", s, True)
    para(cv, M, y + 86, PACIFIC_BODY, 17, False, colw, 22)
    x2 = M + colw + 32
    draw_text(cv, x2, y + 18, "JUSTICE - NEW YORK", 18, True, RED)
    s = fit_size("HUAWEI GUILTY ON 10 COUNTS", colw, True, 30)
    draw_text(cv, x2, y + 52, "HUAWEI GUILTY ON 10 COUNTS", s, True)
    para(cv, x2, y + 86, HUAWEI_BODY, 17, False, colw, 22)
    cv.hline(M, 724, W - 2 * M, INK, 2)
    # row 3: two columns
    y = 740
    draw_text(cv, M, y + 18, "MARKETS", 18, True, RED)
    draw_chart(cv, M + 348, y + 2, 120, 44)
    draw_text(cv, M, y + 52, "THE AI RALLY FADES", 30, True)
    para(cv, M, y + 86, MARKETS_BODY, 17, False, colw, 22)
    draw_text(cv, x2, y + 18, "EUROPE - SPAIN", 18, True, RED)
    s = fit_size("SPAIN'S FINAL TV CLASH", colw, True, 30)
    draw_text(cv, x2, y + 52, "SPAIN'S FINAL TV CLASH", s, True)
    para(cv, x2, y + 86, SPAIN_BODY, 17, False, colw, 22)
    cv.hline(M, 916, W - 2 * M, INK, 2)
    # also strip
    y = 932
    draw_text(cv, M, y + 16, "ALSO TODAY", 17, True, RED)
    ax = M + 132
    for item in ALSO:
        draw_text(cv, ax, y + 16, item, 16, False)
        y += 20
    cv.hline(M, 996, W - 2 * M, INK, 1)
    centered(cv, 1016, "Sources: Reuters - AP - BBC - Xinhua - pm.gov.au  |  Drawn and typeset by a program; no photograph used",
             13, False, GREY)
    return cv


def write_png(cv, path):
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)
        raw += cv.px[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    cv = build()
    path = os.path.join(outdir, "entry.png")
    n = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()
