"""News Image 22 Nov 2026 — one-day world news poster, 1024x1024 PNG.

Draws 49 verified stories from Sunday 22 November 2026 (1 hero, 6 cards,
42 briefs) plus a UTC timeline strip. Python 3.13 standard library only,
no network, deterministic: two runs write byte-identical PNGs.

The text is rendered from a compact 1-bit bitmap font (DejaVu Sans Bold,
28 px em) embedded below as base64; glyphs are box-downsampled to any
target size, so every size stays crisp and legible.
"""

import base64
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font data
# 1-bit bitmap font: header (em size, glyph count), then per-glyph records
# (advance, width, height, top, data offset, data length), then packed bits.
# Generated at build time from DejaVu Sans Bold; see research-22-nov.md.
FONT_B64 = (
    "ABwAXwoAAAAAAAAADQYUBgAAAA8PCggGAA8AChcVFAYAGQA1ExAZBQBOADIcHBQGAIAARhgXFAYAxgA6CQQIBgEAAAQNCRkFAQQAHQ0JGQUBIQAdDw8NBgE+ABkXExEJAVcAKQsHCRUBgAAIDAoEEAGIAAULBgUVAY0ABAoLFwYBkQAgExIUBgGxAC0TDxQGAd4AJhMQFAYCBAAoExEUBgIsACsTEhQGAlcALRMQFAYChAAoExEUBgKsACsTERQGAtcAKxMRFAYDAgArExEUBgMtACsLBg8LA1gADAsIEwsDZAATFxMQCQN3ACYXEwkNA50AFhcTEAkDswAmEA4UBgPZACMcGRkGA/wATxYWFAYESwA3FRIUBgSCAC0VEhQGBK8ALRcUFAYE3AAyExAUBgUOACgTDxQGBTYAJhcUFAYFXAAyFxMUBgWOADAKBhQGBb4ADwoKGgYFzQAhFhUUBgXuADUSEBQGBiMAKBwYFAYGSwA8FxMUBgaHADAYFhQGBrcANxUSFAYG7gAtGBYYBgcbAEIWExQGB10AMBQRFAYHjQArExMUBge4ADAXExQGB+gAMBYWFAYIGAA3Hx4UBghPAEsWFRQGCJoANRQWFAYIzwA3FBMUBgkGADANCRkFCTYAHQoLFwYJUwAgDQoZBQlzACAXEwgGCZMAEw4OAh4JpgAEDggFBAmqAAUTEA8LCa8AHhQRFQUJzQAtEQ4PCwn6ABsUERUFChUALRMRDwsKQgAgDA0VBQpiACMUERULCoUALRQQFQUKsgAqCgYVBQrcABAKCRsFCuwAHxMSFQULCwAwCgYVBQs7ABAdGQ8LC0sALxQQDwsLegAeExIPCwuYACIUERULC7oALRQRFQsL5wAtDgwPCwwUABcRDw8LDCsAHQ0NFAYMSAAhFBAPCwxpAB4SEg8LDIcAIhoYDwsMqQAtEhIPCwzWACISEhULDPgAMBAODwsNKAAbFA4aBQ1DAC4KBBsFDXEADhQOGgUNfwAuFxMHDg2tABF9999999999544AB99999x3Hcdx3Hcdx3HAOHABw4AOOADxwAcOB///P//5///A4cAHDgA44AHHAf//j//8f//gOOADhwAcOADjgAccAABgAGAAYAP/D/8f/x5jPmA+YD/gH/gf/w//g/+Af4BnwGewZ7//v/8//ABgAGAAYABgA+AHAP8A4A54HAHjwcAcPDgBw8cAHDxwAePOAA554AD/HHwD44/wADnnAAcceADjw4AOPDgBw8OAOBx4A4HnAHAP8A4AfAB/AAP/AA/+AB8MAD4AAHwAAPwAAPgAB/geH/g8Pvh4+Pnx8f/Dwf+Hwf4Pgfgfg/gf//gf//gP8fgd3d3dw8Hh4PD4eHw+Hg8Hh8Ph8Hg8Hg+HweD4PB4Hg8A+DwfB4Pg8Hg+HweDweDweDweHw+Hg8Ph4fDw+AADAAYBDCOZ5/+D/AHwD/B/+OZ5DCAYADAAAOAAHAADgABwAA4AAcAAOAP//3//7//8A4AAcAAOAAHAADgABwAA4AA+fPnzz544cH+f5/n+fffffAHAOA4BwDgPAcA4BwHAOAcBwDgHAcA4BwHAOAcBwDgAA/AD/wH/4P/8fj8fB8fA+fA+/A+/A+/A+/A+fA+fA+fB8fj8P/8H/4D/wA/AH8H/g/8H/g58APgB8APgB8APgB8APgB8APgB8APg//////////Af4P/4//z//MD+AH4APgB+AHwA+AHwB+APwB+APwB+AP/+//7//v/+D/Af/g//h//iB/AB+AD8APwP/Af8A/8B/8AD8AD4AHzAfn//P/8f/wP+AAD8AH8AH8AP8Af8Ad8A98B58Dx8Dh8Hh8PB8P//v//v//v//gB8AB8AB8AB8H/8f/x//H/8eAB4AH/gf/h//H/+YP4APgA+AD4APsD+//7//P/4P+AB/AP/g//D/+PwMfAB8+D//H//P/+fh+/B98D74H34Pnw+P/8P/wP/AH4Af/8//5//z//gA/AB8AD4APgAfAB8AD4APgAfAB8AD4APgAfAB8AD4APwAAf4D/8P/4//5+Hz4PnwfHw+P/4H/Af/B//n4fPgffA+/D9//x//h/+A/wAH4A/8D/8P/8fj8+D58H34P3wfvx/f/+f/8f/wPvgAfED8P/4f/g/+AfgA+++++AAAAA+++++APj4+Pj4AAAAAAD4+Pj4+PHh4cAAAQAB8AD+AP+A/4D/wH/AD8AB+AA/4AH/gAf8AB/wAH8AA+AACf//v//3//4AAAAAAAAAf//v//3//4EAADwAB/AA/8AD/gAP+AA/wAD8AB+AH+Af8B/wH/gD+AB4AAgAAf8H/x/+YPgD4A+APgPwH4B8A+APgD4AAAAAD4A+APgD4A+AAP4AA//AA//4A+B+A8AHg8ABw8POccP3GMP/juHnx3Hh47DgcdhwOO44HHceHnOHn3nD//hw/fg8PPAPAAADwAQA+B8AP/8AD/8AAPwAAAPwAB/gAH+AA/4AD/wAPfAB88AHz4A+PgD4fAPh8B8HwH//gf/+D//4P//x+AfHwB+fAD78APn/4H/+H//H//Hw/HwfnwfHwfH//H/8H/+H//HwfnwPnwPnwfn//n//H//H/4AD+Af/g//x//z+B38AX4AHwAHwAPwAPwAHwAHwAH4AH8AT+Bx//w//wf/gD+H/wB//gf/8H//x8H8fAfnwH58A+fAP3wD98A/fAP3wD98B+fAfnwfx//8f/8H/+B/8Af/5//n/+f/58AHwAfAB8AH/8f/x//H/8fAB8AHwAfAB//n/+f/5//n/+//3/+//3wA+AHwA+AH/8//n/8//nwA+AHwA+AHwA+AHwA+AAAP8Af/4P/+H//j+A5/ACfgAHwAB8AA/A//wP98D/fA/34B9/AfP4Hx//8P//B//gD/B8A++AffAPvgH3wD74B98A++Aff//v//3//7//98A++AffAPvgH3wD74B98A++AfB99999999999999999998HwfB8HwfB8HwfB8HwfB8HwfB8HwfB8Hw/D8fv+/z+PgB8B+Pgfh8H4Ph+B8fgPn4B9+AP/gB/4AP+AB/4AP/gB/+APv4B8/gPj+B8P4Pg/h8D+PgP4HwAfAB8AHwAfAB8AHwAfAB8AHwAfAB8AHwAfAB8AHwAf/5//n/+f/5+AP5/AP5/Af5/gf5/gf5/w/5/w/59575957597z58/z58/z58fj58fj58PD58PD58AD58AD58AD58AD5+A+/AffwPv4H3+D7/B9/w+/8ffePvvn3zz75998e++P/fD/vg/3wf74H98D++A/AB/gAf/gH//A//+D+H8fgH5+AfnwA+fAD78APvwA+fAD58APn4B+fgH4/h/D//4H//AH/4AH+Af/gf/4f/8f/+fB+fA+fA+fA+fB+f/+f/8f/4f/gfAAfAAfAAfAAfAAfAAfAAAf4AH/4B//wP//g/h/H4B+fgH58APnwA+/AD78APnwA+fAD5+Afn4B8P4fw//+B//wB/+AB/wAAPgAAfAAA+AAD4f/gP/8H//D//h8Pw+D4fB8Pg+Hw/D//B//A//gf/4Pj8Hw/D4Px8H4+B+fAfPgPwD/Af/x//j//PwefAE+AB+AB/wD/8B/+Af+AD8AD6AH3gfv//f/8f/wH+AP////////////AfAAPgAHwAD4AB8AA+AAfAAPgAHwAD4AB8AA+AAfAAPgAHwAD4AHwHz4D58B8+A+fAfPgPnwHz4D58B8+A+fAfPgPnwHz4D58D8/D+P/+H/+A/+AH8APwA+fAD58Afn4B8PgHw+A+B8D4HwPgfh8A+HwD4/APz4AfPgB98AD/wAP/AA/4AB/gAH+AAPwB8B8B98B8B98D+D4+D+D4+D+D4+D+D4+HvHwfHvHwfHvHwfHHHwfPHvgPvHvgPvHvgP+D/gP+D/gH+D/AH+D/AH8B/AH8B/AD8B+B+AfHwH4fA+D8PgPj8A+/AH/wAf+AB/gAP4AB/AAf8AD/wA//APz4B8fgfB+H4Hw+A/PgD8H4B+PgH4/A/B+H4D4fgPz8AfvgA/+AD/wAH+AAPwAA/AAD8AAPwAA/AAD8AAPwAA/AAD8AAPwB//8//+f//P//AAfgAfgAfgAfgAfgAPgAPgAPwAPwAPwAPwAPwAH//3//7//9//+D/////D4fD4fD4fD4fD4fD4fD4fD4fD4fD////gOAcAcA4BwBwDgHAHAOAcAcA4BwBwDgHAPAOAcA4A4Bwf5/n+B4HgeB4HgeB4HgeB4HgeB4HgeB4HgeB5/n+f4AA8AA/AA/wA/8A+eA8Hg8B48AO////8Hg4HA4HD/A//D/+ID4AHw//P/9///wf+B/4P/x/f/8/3x8f+AB8AD4AHwAPgAfAA+Ph8/j//n8fvwffA/+A/8B/4D/wP/wffx+//58/j4+AB/B/8//fgXwD8A+APgD4A/AHwB+DP/x/8H8AAA+AB8AD4AHwAPgAfD4+P58//78f3wf/gf+A/8B/4D/4H3wfvx/P/+P58Pj4B/AP/g//j8fnwffAe/////////wAHwAPwGP/8P/4H/AD8H+H/D4B8A+B/8/+f/D4B8A+AfAPgHwD4B8A+AfAPgHwAA+Pj+fP/+/H98H/4P/gP/Af+A/+D98H78fz//j+fD4+AD4AHxgfj/+H/4D+APgA+AD4APgA+AD4APj4+fz//v4+/B/8H/gf+B/4H/gf+B/4H/gf+B/4H/vvvgAPvvvvvvvvvvvvvvgfD4fD4AAAfD4fD4fD4fD4fD4fD4fD4fD4fD7+fz4A+AA+AA+AA+AA+AA+AA+D8+H4+Pw+fg+/A/+A/8A/8A/+A+/A+fg+Pw+H4+D8+B+A+++++++++++++++++++++PjwfH38f7//f9/P8//D8P/B8H/g+D/wfB/4Pg/8Hwf+D4P/B8H/g+D/wfB/4Pg++Pj5/P/+/j78H/wf+B/4H/gf+B/4H/gf+B/4H/gfB/AH/wP/4fj8fB8/A++A++A++A+/A+fB8fj8P/4H/wB/APj4fP4//5/H78H3wP/gP/Af+A/8D/8H38fv/+fP4+Ph8AD4AHwAPgAfAA+AAA+Pj+fP/+/H98H/4H/gP/Af+A/+B98H78fz//j+fD4+AB8AD4AHwAPgAfAA+Pj/v/////4fwPwPgPgPgPgPgPgPgPgAD+B/8f/jwM+AD8Af/B/8H/wB+ADzA+f/z/8H+AAfAPgHwD4B8H//////HwD4B8A+AfAPgHwD4B8A/4P8D+D4H/gf+B/4H/gf+B/4H/gf+B/4P/g//H9//z+fHx94B98D58D4+Dw+HweHwfHgfPgPPAP/AH/AH+AH+AD8AD8A+Dwf+DweeH4efH4+fH4+fH48PO88Pud8Pud8H+f4H8f4H8P4H8P4D8PwD4PwfA+Ph8Hz4Hz4D/wB/gA/AA/AB/gB/wD/wHz4Ph8Ph+fA+HgH3wPnwPj4PD4fB4fB8eA8+A+8A/8Af8Af4AP4AP4AHwAHwAHgAPgB/AB/AB8AAH/9//f/wD8B+A/AfgPwH4D8B+A/AP//////wAH4D+B/gfAHwB4AeAHgB4AeAPgD4P8D+A/4A+APgB4AeAHgB4AfAHwB/gP4B+B3d3d3d3d3d3d3d3d3cP4D/A/4A+APgD4AeAHgB4AeAHwB8AP4B+B/gfAHgB4AeAHgB4A+APg/4P8D+AAAAAHwCP+Dv//nD/yAPgAAAA=="
)


def _load_font():
    blob = base64.b64decode(FONT_B64)
    em, count = struct.unpack_from(">HH", blob, 0)
    glyphs = {}
    off = 4
    for i in range(count):
        adv, w, h, top, doff, ln = struct.unpack_from(">BBBBHH", blob, off)
        off += 8
        glyphs[chr(32 + i)] = (adv, w, h, top, doff, ln)
    return em, glyphs, blob, off


EM, GLYPHS, _BLOB, _DATA_OFF = _load_font()
_GLYPH_CACHE = {}


def _glyph_rows(ch):
    """Unpack a glyph's 1-bit bitmap into rows of 0/1."""
    adv, w, h, top, doff, ln = GLYPHS[ch]
    if w == 0 or h == 0:
        return adv, w, h, top, None
    bits = _BLOB[_DATA_OFF + doff:_DATA_OFF + doff + ln]
    rows = []
    pos = 0
    for _y in range(h):
        row = []
        for _x in range(w):
            row.append((bits[pos >> 3] >> (7 - (pos & 7))) & 1)
            pos += 1
        rows.append(row)
    return adv, w, h, top, rows


def render_glyph(ch, target_h):
    """Render one glyph to a grayscale bitmap of height target_h.

    Box-downsamples the 28 px source so small sizes stay smooth.
    Returns (advance, width, height, top, bitmap rows of 0..255).
    """
    key = (ch, target_h)
    hit = _GLYPH_CACHE.get(key)
    if hit is not None:
        return hit
    adv, w, h, top, rows = _glyph_rows(ch)
    scale = target_h / EM
    if rows is None:
        out = (int(round(adv * scale)), 0, 0, 0, [])
        _GLYPH_CACHE[key] = out
        return out
    tw = max(1, int(round(w * scale)))
    th = max(1, int(round(h * scale)))
    bmp = [[0] * tw for _ in range(th)]
    for oy in range(th):
        sy0 = oy / scale
        sy1 = (oy + 1) / scale
        for ox in range(tw):
            sx0 = ox / scale
            sx1 = (ox + 1) / scale
            x0i = int(sx0)
            x1i = min(w, int(sx1) + 1)
            y0i = int(sy0)
            y1i = min(h, int(sy1) + 1)
            ink = 0.0
            area = 0.0
            for sy in range(y0i, y1i):
                wy = min(sy1, sy + 1) - max(sy0, sy)
                if wy <= 0:
                    continue
                rrow = rows[sy]
                for sx in range(x0i, x1i):
                    wx = min(sx1, sx + 1) - max(sx0, sx)
                    if wx <= 0:
                        continue
                    ink += rrow[sx] * wx * wy
                    area += wx * wy
            bmp[oy][ox] = int(255 * ink / area) if area else 0
    out = (int(round(adv * scale)), tw, th, int(round(top * scale)), bmp)
    _GLYPH_CACHE[key] = out
    return out


def text_width(s, size):
    return sum(render_glyph(c, size)[0] for c in s)


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg * (w * h))

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                o = base + (xx - x0) * 3
                self.buf[o] = r
                self.buf[o + 1] = g
                self.buf[o + 2] = b

    def draw_text(self, x, y, s, size, color, clip=None):
        """Draw text with top of the em box at y. Never draws outside clip.

        clip is (x0, y0, x1, y1); the canvas bounds always apply too.
        Returns the width drawn.
        """
        cx0, cy0, cx1, cy1 = clip if clip else (0, 0, self.w, self.h)
        cx0 = max(cx0, 0)
        cy0 = max(cy0, 0)
        cx1 = min(cx1, self.w)
        cy1 = min(cy1, self.h)
        cr, cg, cb = color
        cx = x
        for ch in s:
            adv, tw, th, ttop, bmp = render_glyph(ch, size)
            if bmp:
                for oy in range(th):
                    yy = y + ttop + oy
                    if yy < cy0 or yy >= cy1:
                        continue
                    row = bmp[oy]
                    base = (yy * self.w + cx) * 3
                    for ox in range(tw):
                        a = row[ox]
                        if not a:
                            continue
                        xx = cx + ox
                        if xx < cx0 or xx >= cx1:
                            continue
                        o = base + ox * 3
                        self.buf[o] = self.buf[o] + (cr - self.buf[o]) * a // 255
                        self.buf[o + 1] = self.buf[o + 1] + (cg - self.buf[o + 1]) * a // 255
                        self.buf[o + 2] = self.buf[o + 2] + (cb - self.buf[o + 2]) * a // 255
            cx += adv
        return cx - x


def fit_line(s, size, max_w):
    """Shorten s with '...' until it fits max_w at size. Never overflows."""
    if text_width(s, size) <= max_w:
        return s
    ell = "..."
    while s and text_width(s + ell, size) > max_w:
        s = s[:-1]
    return s + ell


def wrap_lines(s, size, max_w, max_lines):
    """Greedy word wrap; if text needs more than max_lines, the last
    line is shortened with '...' so nothing ever overflows."""
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, size) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = fit_line(lines[-1] + "...", size, max_w)
    return lines


# ---------------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = bytearray()
    out += struct.pack(">I", len(data))
    out += kind
    out += data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return bytes(out)


def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.buf[y * stride:(y + 1) * stride]
    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)

# ------------------------------------------------------------------ content
# All 49 stories verified for Sunday 22 November 2026; see research-22-nov.md.
# Text is ASCII only so the embedded font covers every glyph.

PAPER = (251, 248, 241)
NAVY = (19, 42, 69)
GOLD = (201, 162, 39)
RED = (180, 35, 24)
INK = (26, 26, 26)
GRAY = (110, 110, 108)
WHITE = (255, 255, 255)
RULE = (210, 205, 195)

CAT_COLORS = {
    "CONFLICT": (180, 35, 24),
    "CLIMATE": (30, 122, 70),
    "POLITICS": (29, 78, 137),
    "ECONOMY": (14, 124, 123),
    "ENERGY": (138, 109, 0),
    "SPORT": (30, 107, 58),
    "SCIENCE": (107, 63, 160),
    "CULTURE": (138, 90, 43),
    "DISASTER": (194, 94, 0),
    "TECH": (51, 65, 85),
    "SOCIETY": (122, 59, 110),
    "MIGRATION": (15, 118, 110),
}

HERO = {
    "kicker": "TOP STORY - CLIMATE - ANTALYA, TURKEY",
    "title": "COP31 climate talks collapse with no deal on fossil fuels",
    "summary": (
        "The UN summit ends with no agreement after the EU and about 130 parties "
        "reject a draft that never mentions fossil fuels. The longest COP ever, "
        "and the first big breakdown since Copenhagen 2009."
    ),
    "source": "SOURCES: CNN - NPR - LE MONDE - IPS",
}

CARDS = [
    {
        "tag": "CONFLICT - UKRAINE",
        "title": "Russian drone hits Kyiv block; 14 missing",
        "summary": "A drone partly destroys a block in Dymer; six die across the Kyiv region.",
        "source": "BBC - SCMP - THE HINDU",
    },
    {
        "tag": "CONFLICT - LIBYA",
        "title": "Russian warship hit at Benghazi; 2nd ship hit",
        "summary": "Eastern Libya says a Russian corvette was hit by a suspected sea drone.",
        "source": "FRANCE 24 - BBC - AL JAZEERA",
    },
    {
        "tag": "POLITICS - USA",
        "title": "Democrats win largest House majority since 1992",
        "summary": "Hubbard beats Foxx by 330 votes in a recount; four races remain uncalled.",
        "source": "AP - REUTERS - BBC",
    },
    {
        "tag": "ENERGY - GULF",
        "title": "Two tankers burn after hitting Hormuz mines",
        "summary": "Two tankers burn after hitting mines; Trump dares Iran to defy the blockade.",
        "source": "FOX NEWS - CBS - EURONEWS",
    },
    {
        "tag": "SPORT - F1",
        "title": "Verstappen wins thrilling Las Vegas Grand Prix",
        "summary": "Thirty-five lead changes in 50 laps: Verstappen holds off Norris by 0.639s.",
        "source": "FORMULA1.COM - FIA",
    },
    {
        "tag": "SPORT - FOOTBALL",
        "title": "Liverpool thrash Man Utd 4-0 at Anfield",
        "summary": "Szoboszlai, Wirtz, Ngumoha and Munoz score in Pochettino's debut game.",
        "source": "NBC SPORTS - TALKSPORT",
    },
]

# (category, title) — one line each, shortened to fit its column.
BRIEFS = [
    ("CONFLICT", "Houthis say they hit Saudi refinery"),
    ("CONFLICT", "Drones hit Khartoum homes, UN building"),
    ("CONFLICT", "Settlers torch vehicles in West Bank"),
    ("POLITICS", "Likud-Eisenkot talks end with no deal"),
    ("POLITICS", "S. Korea minister quits over AI cheating"),
    ("DISASTER", "Candy factory fire: 3 dead, 36 missing"),
    ("CONFLICT", "Iran unveils underground 'missile city'"),
    ("ENERGY", "Iran starts rationing electricity"),
    ("ECONOMY", "Iran truck drivers begin strike"),
    ("TECH", "China spy drive to obtain AI chips"),
    ("POLITICS", "Taiwan wary of Canada-China trade ties"),
    ("TECH", "Indian Youth Congress protests at Meta"),
    ("POLITICS", "Pakistan minister's Delhi visit ends"),
    ("POLITICS", "Trump wary of China's nuclear build-up"),
    ("CONFLICT", "Zelensky presses US over Patriots"),
    ("SOCIETY", "Lewis Pugh swims Strait of Hormuz"),
    ("POLITICS", "Pro-Hasina unrest rocks Bangladesh"),
    ("POLITICS", "Thousands march in Istanbul over Sozcu"),
    ("POLITICS", "May tells Burnham: move on from Brexit"),
    ("POLITICS", "Aoun blames Israel and Iran"),
    ("CONFLICT", "Israeli strikes kill two more in Gaza"),
    ("MIGRATION", "ICE arrests at Seattle airport"),
    ("POLITICS", "Hong Kong Election Committee vote"),
    ("POLITICS", "Haiti, El Salvador to build 3 prisons"),
    ("SOCIETY", "Phumzile Mlambo-Ngcuka dies at 71"),
    ("ECONOMY", "Belgium air strike to ground flights"),
    ("DISASTER", "Cyclone Xavier weakens off Cook Is."),
    ("SPORT", "Skubal agrees $450m Mets deal"),
    ("SPORT", "Alcaraz wins first ATP Finals title"),
    ("SPORT", "Gerwyn Price wins Grand Slam of Darts"),
    ("SPORT", "Thitikul wins LPGA finale again"),
    ("SPORT", "Marquez seals record 8th MotoGP title"),
    ("SPORT", "KC Current win first NWSL title"),
    ("SPORT", "UK set to host 2035 Women's World Cup"),
    ("SPORT", "Wembanyama scores 50 in Spurs win"),
    ("SPORT", "Harden scores 51, passes Kobe Bryant"),
    ("SPORT", "Gukesh-Sindarov chess match begins"),
    ("SCIENCE", "Sanxingdui silk hints at ancient writing"),
    ("CULTURE", "Miley Cyrus marries Maxx Morando"),
    ("CULTURE", "Ateez earn fourth Billboard 200 No. 1"),
    ("CULTURE", "Hong Kong film wins at Golden Horse"),
    ("CULTURE", "Molly Meldrum, Countdown host, dies at 83"),
]

TIMELINE = [
    ("04:00", "VERSTAPPEN WINS IN VEGAS"),
    ("13:57", "MARQUEZ SEALS 8TH TITLE"),
    ("15:50", "HULL STUN BRIGHTON 2-0"),
    ("17:03", "ISTANBUL MARCHES"),
    ("18:20", "LIVERPOOL THRASH MAN UTD"),
    ("19:42", "DEMOCRATS TAKE 258"),
    ("23:02", "COP31 COLLAPSE CONFIRMED"),
]

# ------------------------------------------------------------------- layout
MARGIN = 24
COL_W = 317
COL_X = [24, 353, 682]


def _right_text(cv, x_right, y, s, size, color):
    w = text_width(s, size)
    cv.draw_text(x_right - w, y, s, size, color)


def draw():
    cv = Canvas(W, H, PAPER)

    # Masthead: navy band, big date, story count at right.
    cv.fill_rect(0, 0, W, 72, NAVY)
    cv.draw_text(MARGIN, 16, "SUNDAY 22 NOVEMBER 2026", 40, WHITE)
    _right_text(cv, W - MARGIN, 18, "49 VERIFIED STORIES", 16, GOLD)
    _right_text(cv, W - MARGIN, 42, "EVERY STORY SOURCED", 11, (200, 205, 215))
    cv.fill_rect(0, 72, W, 4, GOLD)

    # Hero: white panel, red spine, kicker + title + summary + sources.
    cv.fill_rect(MARGIN, 88, 976, 172, WHITE)
    cv.fill_rect(MARGIN, 88, 8, 172, RED)
    cv.draw_text(48, 100, HERO["kicker"], 13, RED)
    cv.draw_text(48, 124, HERO["title"], 28, INK,
                 clip=(48, 124, 976, 160))
    for i, line in enumerate(wrap_lines(HERO["summary"], 16, 928, 2)):
        cv.draw_text(48, 166 + i * 20, line, 16, INK,
                     clip=(48, 166, 976, 212))
    cv.draw_text(48, 224, HERO["source"], 11, GRAY)

    # Six cards: 3 columns x 2 rows.
    for idx, card in enumerate(CARDS):
        col = idx % 3
        row = idx // 3
        x = COL_X[col]
        y = 276 + row * 144
        cat = card["tag"].split(" - ")[0]
        color = CAT_COLORS.get(cat, NAVY)
        cv.fill_rect(x, y, COL_W, 132, WHITE)
        cv.fill_rect(x, y, COL_W, 4, color)
        cv.draw_text(x + 12, y + 12, card["tag"], 11, color)
        for i, line in enumerate(wrap_lines(card["title"], 19, COL_W - 24, 2)):
            cv.draw_text(x + 12, y + 30 + i * 22, line, 19, INK,
                         clip=(x + 12, y + 30, x + COL_W - 12, y + 78))
        for i, line in enumerate(wrap_lines(card["summary"], 13, COL_W - 24, 2)):
            cv.draw_text(x + 12, y + 80 + i * 16, line, 13, (60, 60, 60),
                         clip=(x + 12, y + 80, x + COL_W - 12, y + 114))
        cv.draw_text(x + 12, y + 114, card["source"], 10, GRAY)

    # Briefs header.
    cv.draw_text(MARGIN, 566, "THE WORLD IN BRIEF", 15, NAVY)
    _right_text(cv, W - MARGIN, 568, "42 MORE STORIES", 12, GRAY)
    cv.fill_rect(MARGIN, 588, 976, 2, RULE)

    # Briefs grid: 3 columns x 14 rows, one line each, clipped to its cell.
    for idx, (cat, title) in enumerate(BRIEFS):
        col = idx % 3
        row = idx // 3
        x = COL_X[col]
        y = 596 + row * 25
        color = CAT_COLORS.get(cat, NAVY)
        cv.fill_rect(x, y + 4, 8, 8, color)
        shown = fit_line(title, 12, COL_W - 18)
        cv.draw_text(x + 16, y + 4, shown, 12, INK,
                     clip=(x + 16, y, x + COL_W, y + 22))

    # Timeline strip: navy band, UTC moments of the day.
    cv.fill_rect(0, 956, W, 68, NAVY)
    cv.draw_text(MARGIN, 964, "UTC TIMELINE", 12, GOLD)
    for line_no, group in enumerate((TIMELINE[:3], TIMELINE[3:])):
        cx = MARGIN
        y = 986 + line_no * 22
        for j, (t, label) in enumerate(group):
            if j:
                cx += 26
            cx += cv.draw_text(cx, y, t + "  ", 12, GOLD,
                               clip=(MARGIN, y, W - MARGIN, y + 16))
            cx += cv.draw_text(cx, y, label, 12, WHITE,
                               clip=(MARGIN, y, W - MARGIN, y + 16))

    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = draw()
    write_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
