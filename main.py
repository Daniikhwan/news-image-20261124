#!/usr/bin/env python3
"""news-image-20261124 -- one image summing up world news of 24 Nov 2026.

Draws a 1024x1024 newspaper front page with a pure-stdlib PNG encoder.
No network, no external assets: every pixel is computed here, so the
output is byte-for-byte deterministic across runs.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 242, 231)
CARD = (255, 255, 255)
INK = (22, 26, 34)
NAVY = (20, 33, 61)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
GREEN = (31, 122, 62)
BLUE = (28, 96, 168)
ORANGE = (214, 96, 24)
TEAL = (14, 122, 110)
GREY = (110, 114, 122)
LIGHT = (232, 228, 218)

# ------------------------------------------------------------- 5x7 font
# Each glyph: 7 row bitmasks, bit 4 = leftmost column.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x04, 0x04, 0, 0x04, 0x04, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "'": (0x02, 0x02, 0x04, 0, 0, 0, 0),
    '-': (0, 0, 0, 0x0E, 0, 0, 0),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    '%': (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '+': (0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    '_': (0, 0, 0, 0, 0, 0, 0x1F),
    '*': (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '@': (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
}


class Canvas:
    """An RGB pixel buffer with small drawing primitives."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg[0] for _ in range(w * h * 3))
        for i in range(w * h):
            self.px[i * 3:i * 3 + 3] = bytes(bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i:i + 3] = bytes(c)

    def border(self, x, y, w, h, c, t=2):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.fill(cx - dx, yy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = math.hypot(xx - cx, yy - cy)
                if r - t < d <= r:
                    self.set(xx, yy, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        xs = sorted([x0, x1, x2])
        for yy in range(min(y0, y1, y2), max(y0, y1, y2) + 1):
            pts = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2),
                                     (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by) or yy == max(y0, y1, y2):
                    t = (yy - ay) / (by - ay)
                    pts.append(ax + t * (bx - ax))
            if len(pts) >= 2:
                a, b = int(min(pts)), int(max(pts))
                self.fill(a, yy, b - a + 1, 1, c)

    # ------------------------------------------------------------ text
    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx - x

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_center(self, y, s, scale, c):
        self.text((self.w - self.text_w(s, scale)) // 2, y, s, scale, c)

    def wrap(self, s, scale, max_w):
        words, lines, cur = s.split(), [], ''
        for wd in words:
            trial = (cur + ' ' + wd).strip()
            if self.text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------- icons
def draw_chip(cv, x, y, s, body, pin):
    cv.fill(x, y, s, s, body)
    cv.border(x, y, s, s, INK, 3)
    m = s // 4
    cv.fill(x + m, y + m, s - 2 * m, s - 2 * m, PAPER)
    cv.border(x + m, y + m, s - 2 * m, s - 2 * m, INK, 2)
    for i in range(3):
        off = s // 4 + i * (s // 4)
        cv.fill(x + off, y - 10, 6, 10, pin)
        cv.fill(x + off, y + s, 6, 10, pin)
        cv.fill(x - 10, y + off, 10, 6, pin)
        cv.fill(x + s, y + off, 10, 6, pin)


def draw_blast(cv, cx, cy, r, c1, c2):
    for k in range(8):
        a = k * math.pi / 4
        tx, ty = int(cx + math.cos(a) * r), int(cy + math.sin(a) * r)
        ax, ay = int(cx + math.cos(a + 0.35) * r * 0.45), \
            int(cy + math.sin(a + 0.35) * r * 0.45)
        bx, by = int(cx + math.cos(a - 0.35) * r * 0.45), \
            int(cy + math.sin(a - 0.35) * r * 0.45)
        cv.triangle(tx, ty, ax, ay, bx, by, c1)
    cv.disc(cx, cy, int(r * 0.42), c2)


def draw_flame(cv, cx, cy, s, outer, inner):
    cv.triangle(cx - s // 2, cy + s // 3, cx, cy - s, cx + s // 2, cy + s // 3,
                outer)
    cv.disc(cx, cy + s // 6, s // 2, outer)
    cv.triangle(cx - s // 4, cy + s // 3, cx, cy - s // 2,
                cx + s // 4, cy + s // 3, inner)
    cv.disc(cx, cy + s // 4, s // 4, inner)


def draw_globe(cv, cx, cy, r, c):
    cv.ring(cx, cy, r, c, 4)
    cv.hline(cx - r + 6, cy - r // 2, 2 * r - 12, c, 3)
    cv.hline(cx - r + 2, cy, 2 * r - 4, c, 3)
    cv.hline(cx - r + 6, cy + r // 2, 2 * r - 12, c, 3)
    for t in range(0, 361, 6):
        a = math.radians(t)
        x = int(cx + math.cos(a) * r * 0.45)
        y = int(cy + math.sin(a) * r)
        cv.fill(x, y, 3, 3, c)


def draw_flag(cv, x, y, s, c1, c2):
    cv.vline(x, y, s + 18, INK, 4)
    cv.disc(x, y - 4, 4, GOLD)
    sq = s // 4
    for r in range(3):
        for col in range(4):
            cv.fill(x + 4 + col * sq, y + r * sq, sq, sq,
                    INK if (r + col) % 2 == 0 else CARD)
    cv.border(x + 4, y, 4 * sq, 3 * sq, INK, 2)


# -------------------------------------------------------------- layout
def kicker(cv, x, y, label, c):
    cv.fill(x, y, 8, 16, c)
    cv.text(x + 16, y + 1, label, 1, c)


def story_card(cv, x, y, w, h, accent, tag, headline, sub, icon):
    cv.fill(x, y, w, h, CARD)
    cv.border(x, y, w, h, INK, 2)
    cv.fill(x, y, w, 6, accent)
    kicker(cv, x + 18, y + 20, tag, accent)
    tw = w - 36 - (150 if icon else 0)
    lines = cv.wrap(headline, 2, tw)
    yy = y + 52
    for ln in lines[:3]:
        cv.text(x + 18, yy, ln, 2, INK)
        yy += 20
    if sub:
        sub_lines = cv.wrap(sub, 1, tw)
        yy += 8
        for ln in sub_lines[:3]:
            cv.text(x + 18, yy, ln, 1, (64, 68, 76))
            yy += 12
    if icon:
        icon(x + w - 132, y + h - 128)


def build():
    cv = Canvas(W, H, PAPER)

    # masthead
    cv.fill(0, 0, W, 150, NAVY)
    cv.text_center(26, 'THE WORLD IN ONE IMAGE', 4, CARD)
    cv.hline(212, 74, 600, GOLD, 3)
    cv.text_center(92, 'TUESDAY, 24 NOVEMBER 2026', 2, GOLD)
    cv.text_center(120, "THE DAY'S WORLD NEWS, SUMMED UP", 1, (200, 206, 216))

    # lead story: NVIDIA
    story_card(cv, 24, 170, 976, 226, GREEN, 'TECHNOLOGY',
               'HUANG IS BACK: NVIDIA CHIEF RETURNS, SHARES SOAR 31% IN A DAY',
               'Jensen Huang is reinstated after a board inquiry clears him; '
               'a US Senate hearing is set for 3 December.',
               lambda ix, iy: (draw_chip(cv, ix, iy, 92, GREEN, INK),
                               cv.text(ix + 26, iy + 34, 'NV', 2, INK)))

    # row two: war + Indonesia
    story_card(cv, 24, 416, 476, 236, RED, 'WAR IN EUROPE',
               'DRONES STRIKE KYIV REGION AS WAR GRINDS ON',
               'Russian attacks hit homes in Dymer; cargo ship Sparta II '
               'ablaze off Finland after a drone strike.',
               lambda ix, iy: draw_blast(cv, ix + 62, iy + 60, 46, RED, GOLD))
    story_card(cv, 524, 416, 476, 236, ORANGE, 'INDONESIA',
               'FACTORY FIRE IN BANTEN KILLS 24',
               'Rescue teams search for missing workers after a blaze '
               'at a candy factory in Banten province.',
               lambda ix, iy: draw_flame(cv, ix + 62, iy + 66, 84, ORANGE, GOLD))

    # row three: climate + sport
    story_card(cv, 24, 672, 476, 208, TEAL, 'CLIMATE',
               'COP31 SPLIT OVER FOSSIL FUELS',
               'Climate talks in Antalya, Turkiye, divided as nations '
               'weigh curbs on warming.',
               lambda ix, iy: draw_globe(cv, ix + 62, iy + 56, 48, TEAL))
    story_card(cv, 524, 672, 476, 208, BLUE, 'SPORT',
               'VERSTAPPEN WINS IN VEGAS; ALCARAZ TAKES ATP FINALS',
               'Red Bull star triumphs under the lights; Spaniard beats '
               'Zverev in Turin.',
               lambda ix, iy: draw_flag(cv, ix + 30, iy + 30, 72, BLUE, CARD))

    # ticker strip
    cv.fill(24, 900, 976, 56, INK)
    cv.text(40, 910, "ALSO TODAY:", 1, GOLD)
    cv.text(40, 928, 'INDIA-CHINA HOLD BORDER TALKS - O\'HARE GROUND STOP - '
                     'LISBON MARCHES OVER LIVING COSTS', 1, CARD)

    # footer
    cv.text_center(978, 'SUMMARY OF WORLD NEWS - 24 NOVEMBER 2026', 1, INK)
    cv.text_center(994, 'DRAWN FROM PUBLIC NEWS REPORTS OF THE DAY', 1, GREY)
    return cv


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        return out + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))


def main():
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(outdir, exist_ok=True)
    data = encode_png(build())
    path = os.path.join(outdir, 'entry.png')
    with open(path, 'wb') as f:
        f.write(data)
    print('wrote %s (%d bytes, %dx%d)' % (path, len(data), W, H))


if __name__ == '__main__':
    main()
