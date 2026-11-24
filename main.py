#!/usr/bin/env python3
"""Tuesday 24 November 2026 - the world in one image.

Draws a one-page newspaper front page that sums up the day's world news
and writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Pure standard library: the PNG is encoded by hand (zlib + struct) and
every shape and letter is rasterised by this file - no fonts, no PIL,
no network, no randomness, so two runs write identical bytes.

Stories (all first reported on 23-24 November 2026):
  - Strait of Hormuz: three tankers hit sea mines and catch fire,
    Iran's Revolutionary Guard says; Tehran warns EU military bases
    are in range of its missiles; the US Treasury sanctions two dozen
    Iranian exchange houses; Iran says it shot down a US drone over
    the Gulf. (Al Jazeera / IRGC, 24 Nov)
  - Kyiv region: Russian airstrikes kill at least 12, hitting homes
    and power infrastructure. (AP, 24 Nov)
  - Nvidia: Jensen Huang returns as CEO after an inquiry into his
    conduct; the board reinstates him and the shares surge 31% in a
    day. (24 Nov)
  - Gaza: Oxfam and CEOBS report the war left Gaza's air, soil and
    water contaminated with heavy metals and toxins for decades.
    (24 Nov)
  - South Korea: the education minister steps down over an AI
    exam-cheating scandal. (24 Nov)
  - Balkh, Afghanistan: the Taliban order women's names struck from
    official documents and replaced with the word "Bibi". (24 Nov)
Ticker: FIFA confirms the 2031 Women's World Cup for the US, Mexico,
Costa Rica and Jamaica; Lahore tops the pollution ranking with AQI
over 500; a Chinese official is sentenced to death for leaking state
secrets; O'Hare faces a brief ground stop in the Thanksgiving rush.
"""

import os
import struct
import zlib
from math import sqrt

W, H = 1024, 1024

# ---- palette ---------------------------------------------------------
PAPER = (246, 241, 230)
INK = (24, 32, 54)
INK_SOFT = (58, 70, 96)
RED = (178, 38, 30)
RED_DARK = (132, 26, 20)
TEAL = (14, 110, 104)
GOLD = (198, 150, 40)
SKY = (176, 212, 233)
SKY_PALE = (216, 233, 242)
SEA = (24, 96, 124)
SEA_DARK = (16, 68, 94)
ORANGE = (232, 116, 28)
YELLOW = (244, 196, 66)
GREEN = (46, 125, 70)
GREY = (120, 124, 128)
GREY_DARK = (88, 92, 96)
GREY_LIGHT = (208, 206, 198)
WHITE = (255, 255, 255)
CREAM = (232, 222, 198)
SMOKE = (150, 148, 142)
BROWN = (146, 108, 66)
DIRT = (196, 164, 120)

# ---- 5x7 bitmap font, authored here: each glyph is 7 rows of 5 bits --
_GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}
FONT = {ch: tuple(int(row, 2) for row in rows) for ch, rows in _GLYPHS.items()}
CHAR_W = 6  # 5 px glyph + 1 px gap, before scaling


class Canvas:
    """An RGB framebuffer with small filled-shape helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        r, g, b = color
        self.buf[0::3] = bytes([r]) * (self.w * self.h)
        self.buf[1::3] = bytes([g]) * (self.w * self.h)
        self.buf[2::3] = bytes([b]) * (self.w * self.h)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            span = (x1 - x0) * 3
            self.buf[base:base + span] = bytes(color) * (x1 - x0)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int(sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
                if r - thick <= d <= r:
                    self.px(xx, yy, color)

    def poly(self, pts, color):
        """Scanline fill of a simple polygon."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, color)

    def tri(self, a, b, c, color):
        self.poly([a, b, c], color)

    # ---- text --------------------------------------------------------
    def text(self, s, x, y, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += CHAR_W * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * CHAR_W * scale

    def text_center(self, s, cx, y, scale, color):
        self.text(s, cx - self.text_w(s, scale) // 2, y, scale, color)

    def wrap(self, text, max_w, scale):
        """Greedy word wrap; returns a list of lines."""
        lines, cur = [], ""
        for word in text.split(" "):
            trial = word if not cur else cur + " " + word
            if self.text_w(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def encode_png(canvas):
    """Hand-rolled PNG: filter 0 on every row, zlib level 9."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * stride:(y + 1) * stride]
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---- illustrations ---------------------------------------------------
# Each draws inside the rectangle (x, y, w, h) given to it.

def _mine(cv, mx, my):
    """A spiked sea mine bobbing on the water."""
    cv.circle(mx, my, 7, INK)
    for dx, dy in ((-9, 0), (9, 0), (0, -9), (0, 9),
                   (-6, -6), (6, -6), (-6, 6), (6, 6)):
        cv.line(mx, my, mx + dx, my + dy, INK, 2)


def art_hormuz(cv, x, y, w, h):
    """A tanker burning in the Strait of Hormuz; mines in the water."""
    cv.rect(x, y, w, h, SKY_PALE)
    cv.circle(x + w - 52, y + 34, 22, YELLOW)
    cv.circle(x + w - 52, y + 34, 16, GOLD)
    cv.rect(x, y + h - 78, w, 78, SEA)
    cv.rect(x, y + h - 78, w, 6, SEA_DARK)
    cv.rect(x, y + h - 52, w, 4, SEA_DARK)
    cv.rect(x, y + h - 26, w, 4, SEA_DARK)
    # mines drifting in the foreground water
    _mine(cv, x + 52, y + h - 40)
    _mine(cv, x + w - 70, y + h - 34)
    # tanker hull with a pointed bow
    hx, hy = x + 24, y + h - 118
    cv.poly([(hx, hy + 26), (hx + 34, hy), (hx + w - 84, hy),
             (hx + w - 52, hy + 26), (hx + w - 52, hy + 44),
             (hx, hy + 44)], INK)
    cv.rect(hx + 8, hy - 30, 46, 30, RED)
    cv.rect(hx + 60, hy - 30, 46, 30, TEAL)
    cv.rect(hx + 112, hy - 30, 46, 30, GOLD)
    cv.rect(hx + 164, hy - 30, 46, 30, GREY_DARK)
    cv.rect(hx + 216, hy - 46, 26, 46, WHITE)
    cv.rect(hx + 216, hy - 46, 26, 8, RED)
    # flames above the mid-deck
    fx = hx + 130
    cv.tri((fx, hy - 28), (fx + 14, hy - 78), (fx + 30, hy - 28), ORANGE)
    cv.tri((fx + 22, hy - 28), (fx + 34, hy - 64), (fx + 48, hy - 28), YELLOW)
    cv.tri((fx + 42, hy - 28), (fx + 52, hy - 56), (fx + 64, hy - 28), ORANGE)
    # smoke puffs drifting up
    cv.circle(fx + 20, hy - 92, 12, SMOKE)
    cv.circle(fx + 38, hy - 108, 15, GREY_LIGHT)
    cv.circle(fx + 58, hy - 122, 12, SMOKE)
    # distant second ship and a gull
    cv.rect(x + w - 120, y + h - 96, 74, 10, INK_SOFT)
    cv.rect(x + w - 104, y + h - 106, 12, 10, INK_SOFT)
    cv.line(x + 40, y + 26, x + 52, y + 20, INK_SOFT, 2)
    cv.line(x + 52, y + 20, x + 64, y + 26, INK_SOFT, 2)


def art_kyiv(cv, x, y, w, h):
    """A five-storey block, its right half collapsed, a drone above."""
    cv.rect(x, y, w, h, SKY_PALE)
    cv.circle(x + 34, y + 24, 14, YELLOW)
    bx, by = x + 18, y + h - 78
    bw, bh = 150, 78
    cv.rect(bx, by, bw, bh, GREY_LIGHT)
    cv.rect(bx, by, bw, 6, GREY_DARK)
    for r in range(4):
        for c in range(5):
            cv.rect(bx + 10 + c * 28, by + 14 + r * 16, 14, 9,
                    INK_SOFT if (r + c) % 2 else GOLD)
    # collapsed right section: jagged ruin and rubble
    rx = bx + bw
    cv.poly([(rx, by), (rx + 66, by + 8), (rx + 58, by + 30),
             (rx + 70, by + 52), (rx + 52, by + bh), (rx, by + bh)],
            GREY_DARK)
    cv.tri((rx + 4, by + bh), (rx + 26, by + bh - 22), (rx + 48, by + bh), GREY)
    cv.tri((rx + 30, by + bh), (rx + 52, by + bh - 16), (rx + 74, by + bh), SMOKE)
    cv.rect(rx + 8, by + 18, 10, 7, ORANGE)
    cv.rect(rx + 8, by + 34, 8, 6, YELLOW)
    # quadcopter drone with four rotors
    dx, dy = x + w - 62, y + 30
    cv.rect(dx - 10, dy - 5, 20, 10, INK)
    cv.line(dx - 22, dy - 8, dx - 2, dy - 2, INK, 2)
    cv.line(dx + 2, dy - 2, dx + 22, dy - 8, INK, 2)
    cv.line(dx - 22, dy + 8, dx - 2, dy + 2, INK, 2)
    cv.line(dx + 2, dy + 2, dx + 22, dy + 8, INK, 2)
    for px_, py_ in ((dx - 24, dy - 9), (dx + 24, dy - 9),
                     (dx - 24, dy + 9), (dx + 24, dy + 9)):
        cv.hline(px_ - 8, py_, 17, INK)
    cv.circle(dx, dy + 12, 2, RED)


def art_nvidia(cv, x, y, w, h):
    """A green chip with a steep rising arrow and +31%."""
    cv.rect(x, y, w, h, SKY_PALE)
    # the chip, centre-left
    cx, cy = x + 78, y + h // 2 - 4
    cv.rect(cx - 46, cy - 34, 92, 68, GREEN)
    cv.rect(cx - 46, cy - 34, 92, 68, INK)
    cv.rect(cx - 34, cy - 22, 68, 44, (58, 160, 90))
    cv.text("NVDA", cx - 30, cy - 8, 2, WHITE)
    for i in range(5):
        cv.vline(cx - 36 + i * 18, cy - 46, 12, INK)
        cv.vline(cx - 36 + i * 18, cy + 34, 12, INK)
        cv.hline(cx - 58, cy - 24 + i * 12, 12, INK)
        cv.hline(cx + 46, cy - 24 + i * 12, 12, INK)
    # rising arrow, bottom-left to top-right
    ax0, ay0 = x + 150, y + h - 18
    ax1, ay1 = x + w - 24, y + 26
    cv.line(ax0, ay0, ax1, ay1, GREEN, 5)
    cv.tri((ax1, ay1), (ax1 - 26, ay1 + 2), (ax1 - 4, ay1 + 24), GREEN)
    # dashed steps under the arrow
    cv.rect(x + 168, y + h - 34, 34, 6, GREY)
    cv.rect(x + 216, y + h - 52, 34, 6, GREY)
    cv.rect(x + 264, y + h - 70, 34, 6, GREY)
    cv.text("+31%", x + w - 96, y + h - 22, 2, GREEN)


def art_gaza(cv, x, y, w, h):
    """Cracked dry earth with a poisoned water drop."""
    cv.rect(x, y, w, h, SKY_PALE)
    # dry ground
    gy = y + 52
    cv.rect(x, gy, w, h - gy, DIRT)
    cv.rect(x, gy, w, 4, BROWN)
    # jagged cracks across the ground
    cv.line(x + 20, gy + 8, x + 60, gy + 26, BROWN, 3)
    cv.line(x + 60, gy + 26, x + 44, gy + 44, BROWN, 3)
    cv.line(x + 44, gy + 44, x + 84, gy + 58, BROWN, 3)
    cv.line(x + w - 90, gy + 10, x + w - 56, gy + 30, BROWN, 3)
    cv.line(x + w - 56, gy + 30, x + w - 76, gy + 52, BROWN, 3)
    cv.line(x + 130, gy + 30, x + 160, gy + 52, BROWN, 2)
    cv.line(x + 160, gy + 52, x + 148, gy + 66, BROWN, 2)
    # a water drop, ringed in red
    dx, dy = x + w // 2, y + 26
    cv.circle(dx, dy + 10, 16, SEA)
    cv.tri((dx - 14, dy + 4), (dx, dy - 16), (dx + 14, dy + 4), SEA)
    cv.ring(dx, dy + 6, 24, RED, 3)
    cv.text("TOXIC", x + 12, y + 8, 1, RED)


def art_korea(cv, x, y, w, h):
    """An exam paper stamped AI, crossed out in red."""
    cv.rect(x, y, w, h, SKY_PALE)
    # the paper
    px, py = x + 30, y + 8
    pw, ph = w - 60, h - 16
    cv.rect(px, py, pw, ph, WHITE)
    cv.rect(px, py, pw, ph, INK)
    for i in range(5):
        cv.rect(px + 14, py + 14 + i * 14, pw - 28, 3, GREY_LIGHT)
    cv.text("EXAM", px + 14, py + 6, 1, INK_SOFT)
    # red cross over the paper
    cv.line(px + 6, py + 6, px + pw - 6, py + ph - 6, RED, 4)
    cv.line(px + pw - 6, py + 6, px + 6, py + ph - 6, RED, 4)
    # AI stamp
    sx, sy = x + w - 92, y + h - 44
    cv.rect(sx, sy, 76, 30, WHITE)
    cv.rect(sx, sy, 76, 30, RED)
    cv.text("AI", sx + 24, sy + 8, 2, RED)


def art_afghan(cv, x, y, w, h):
    """An official document with the name line blacked out."""
    cv.rect(x, y, w, h, SKY_PALE)
    # the document
    px, py = x + 34, y + 8
    pw, ph = w - 68, h - 16
    cv.rect(px, py, pw, ph, WHITE)
    cv.rect(px, py, pw, ph, INK)
    cv.text("NAME:", px + 12, py + 12, 1, INK_SOFT)
    # the name, struck through and blacked out
    cv.rect(px + 62, py + 10, pw - 74, 12, INK)
    cv.line(px + 12, py + 34, px + pw - 12, py + 34, GREY_LIGHT, 2)
    cv.line(px + 12, py + 48, px + pw - 12, py + 48, GREY_LIGHT, 2)
    cv.line(px + 12, py + 62, px + pw - 40, py + 62, GREY_LIGHT, 2)
    # replacement stamp
    sx, sy = px + 14, py + ph - 34
    cv.rect(sx, sy, 92, 24, WHITE)
    cv.rect(sx, sy, 92, 24, RED)
    cv.text("BIBI", sx + 12, sy + 7, 2, RED)


# ---- page layout -----------------------------------------------------

def panel(cv, x, y, w, h, accent, kicker, headline, body, art, art_h):
    """One story panel: illustration on top, kicker, headline, body."""
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK)  # border via four thin rects below
    cv.rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    cv.rect(x, y, w, 6, accent)
    art(cv, x + 8, y + 12, w - 16, art_h)
    ty = y + 12 + art_h + 8
    cv.text(kicker, x + 12, ty, 1, accent)
    ty += 14
    for line in cv.wrap(headline, w - 24, 2):
        cv.text(line, x + 12, ty, 2, INK)
        ty += 17
    ty += 3
    for line in cv.wrap(body, w - 24, 1):
        cv.text(line, x + 12, ty, 1, INK_SOFT)
        ty += 11


def draw_page():
    cv = Canvas(W, H, PAPER)
    # outer frame
    cv.rect(0, 0, W, 4, INK)
    cv.rect(0, H - 4, W, 4, INK)
    cv.rect(0, 0, 4, H, INK)
    cv.rect(W - 4, 0, 4, H, INK)

    # ---- masthead ----------------------------------------------------
    cv.rect(20, 20, 984, 96, INK)
    cv.rect(20, 20, 984, 4, RED)
    cv.text_center("THE WORLD TODAY", 512, 32, 4, WHITE)
    cv.text_center("TUESDAY 24 NOVEMBER 2026  -  ONE DAY IN THE NEWS",
                   512, 74, 2, GOLD)
    cv.hline(36, 100, 952, RED)

    # ---- lead story: the Gulf ---------------------------------------
    lx, ly, lw, lh = 20, 128, 984, 268
    cv.rect(lx, ly, lw, lh, WHITE)
    cv.rect(lx, ly, lw, 6, RED)
    cv.rect(lx, ly, lw, lh, INK)
    cv.rect(lx + 2, ly + 2, lw - 4, lh - 4, WHITE)
    cv.rect(lx, ly, lw, 6, RED)
    cv.text("THE GULF  -  LEAD STORY", lx + 16, ly + 18, 1, RED)
    ty = ly + 40
    for line in cv.wrap("THREE TANKERS HIT MINES AND BURN IN HORMUZ",
                        500, 3):
        cv.text(line, lx + 16, ty, 3, INK)
        ty += 24
    ty += 6
    lead_body = [
        "THREE TANKERS STRUCK SEA MINES IN THE STRAIT",
        "AND CAUGHT FIRE, IRAN'S GUARDS SAY. TEHRAN",
        "WARNS EU BASES ARE IN RANGE OF ITS MISSILES;",
        "THE US SANCTIONS IRANIAN EXCHANGE HOUSES.",
    ]
    for line in lead_body:
        cv.text(line, lx + 16, ty, 2, INK_SOFT)
        ty += 19
    ty += 6
    cv.text("SOURCE: IRGC / AL JAZEERA, 24 NOV", lx + 16, ty, 1, GREY)
    art_hormuz(cv, lx + 540, ly + 16, 428, 236)

    # ---- second row: Kyiv and Nvidia --------------------------------
    panel(cv, 20, 408, 484, 232, INK, "UKRAINE",
          "12 KILLED AS STRIKES HIT KYIV REGION",
          "RUSSIAN AIRSTRIKES HIT HOMES AND POWER LINES "
          "ACROSS THE KYIV REGION; AT LEAST 12 DEAD.",
          art_kyiv, 84)
    panel(cv, 520, 408, 484, 232, GREEN, "TECH  -  NVIDIA",
          "HUANG BACK AS NVIDIA CEO AS SHARES SURGE",
          "JENSEN HUANG RETURNS AFTER AN INQUIRY INTO HIS "
          "CONDUCT; THE BOARD REINSTATES HIM AND THE "
          "STOCK SOARS 31% IN A DAY.",
          art_nvidia, 84)

    # ---- third row: Gaza, South Korea, Afghanistan ------------------
    panel(cv, 20, 652, 320, 232, RED, "GAZA",
          "WAR LEFT GAZA'S LAND AND WATER POISONED",
          "OXFAM AND CEOBS: EXPLOSIVES LEFT HEAVY METALS "
          "AND TOXINS ACROSS THE STRIP, A DANGER FOR "
          "DECADES.",
          art_gaza, 80)
    panel(cv, 352, 652, 320, 232, TEAL, "SOUTH KOREA",
          "MINISTER QUITS OVER AI EXAM CHEATING",
          "THE EDUCATION MINISTER STEPS DOWN AFTER AN AI "
          "CHEATING SCANDAL IN THE NATIONAL EXAMS.",
          art_korea, 80)
    panel(cv, 684, 652, 320, 232, GOLD, "AFGHANISTAN",
          "TALIBAN ERASE WOMEN'S NAMES FROM PAPERS",
          "IN BALKH, WOMEN'S NAMES ARE STRUCK FROM OFFICIAL "
          "DOCUMENTS AND REPLACED WITH THE WORD BIBI.",
          art_afghan, 80)

    # ---- ticker: the rest of the day --------------------------------
    tx, ty, tw, th = 20, 896, 984, 64
    cv.rect(tx, ty, tw, th, INK)
    cv.text("ALSO TODAY", tx + 12, ty + 10, 1, GOLD)
    ticker1 = ("FIFA: 2031 WOMEN'S WORLD CUP IN US, MEXICO, COSTA RICA, "
               "JAMAICA  .  LAHORE TOPS POLLUTION RANKING, AQI OVER 500")
    ticker2 = ("CHINA OFFICIAL SENTENCED TO DEATH FOR LEAKING SECRETS  .  "
               "O'HARE GROUND STOP AMID THANKSGIVING RUSH")
    cv.text(ticker1, tx + 12, ty + 26, 1, WHITE)
    cv.text(ticker2, tx + 12, ty + 42, 1, WHITE)

    # ---- footer ------------------------------------------------------
    cv.text_center("SOURCES: AL JAZEERA  .  AP  .  REUTERS  .  AFP  .  OXFAM",
                   512, 972, 1, INK_SOFT)
    cv.text_center("DRAWN BY AN AI NEWS ARTIST - NO PHOTOGRAPHS USED",
                   512, 988, 1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = encode_png(draw_page())
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
