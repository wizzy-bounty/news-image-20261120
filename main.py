#!/usr/bin/env python3
"""
ONE DAY, ONE PLANET -- the world's news of Friday 20 November 2026,
drawn as a single 1024x1024 broadsheet front page.

The program renders the page with Pillow at 2x supersampling and
downsamples with Lanczos.  It writes entry.png to $MAKEFUN_OUTPUT_DIR
(or /output when the variable is unset).  Output is deterministic:
two runs produce byte-identical files.

If Pillow is not importable, the program instead copies the bundled
entry.png (the artifact committed next to this file) byte-for-byte to
the output path.
"""

import os
import shutil

# ---------------------------------------------------------------------------
# Canvas and palette (all coordinates in final-image pixels; SS = supersample)
# ---------------------------------------------------------------------------

SS = 2
W = H = 1024
MARGIN = 26
CONTENT_W = W - 2 * MARGIN  # 972

PAPER = (247, 243, 233)        # warm cream newsprint
PAPER_DARK = (238, 231, 214)   # shaded band
CARD = (253, 251, 245)         # panel card
INK = (18, 32, 54)             # ink navy
INK_SOFT = (58, 72, 96)        # softened ink
TEAL = (0, 100, 106)           # deep teal
TEAL_DARK = (0, 74, 80)
CRIMSON = (176, 32, 50)
GOLD = (196, 142, 40)
GREEN = (28, 128, 74)
MAP_DOT = (122, 148, 148)
MAP_LABEL = (139, 154, 158)
RULE_SOFT = (196, 190, 172)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

# ---------------------------------------------------------------------------
# Story index data: (group, [(number, town, headline), ...])
# ---------------------------------------------------------------------------

GROUPS = [
    ("WORLD", [
        (1, "THE HAGUE",
         "ICJ rules Myanmar committed genocide against the Rohingya, "
         "9\u20136; 1.3 million displaced."),
        (2, "SHENZHEN",
         "Trump, Xi and Putin hold first three-way summit; four-point "
         "peace declaration signed."),
        (10, "BERLIN",
         "Ukraine's allies say Europe is ready to talk with Russia; "
         "NATO-style guarantee floated."),
        (13, "BRUSSELS",
         "UK\u2013EU reset: \u00a35.1bn food-trade deal, carbon link, "
         "100,000 youth places a year."),
        (18, "WASHINGTON",
         "IMF warns global public debt will soon hit 100% of world GDP, "
         "highest since WWII."),
        (22, "PYONGYANG",
         "IAEA says North Korea is expanding uranium enrichment at "
         "Yongbyon."),
        (25, "ULAANBAATAR",
         "Mongolia's President Kh\u00fcrels\u00fckh resigns; speaker "
         "becomes acting president."),
    ]),
    ("EUROPE", [
        (8, "KYIV",
         "Russian overnight strikes target bridges, kill eight; 28 hurt "
         "across nine regions."),
        (9, "CRIMEA",
         "Ukraine hits Kerch Bridge for third time in a week; rail "
         "halted, Putin vows reply."),
        (11, "WARSAW",
         "Russia violates Poland's airspace overnight with two missiles "
         "and a drone."),
        (12, "TALLINN",
         "Estonia to close Russia border for six months; Moscow cries "
         "new Iron Curtain."),
        (14, "ANTALYA",
         "COP31 draft drops fossil-fuel phase-out call; Pacific nations "
         "demand it back."),
        (48, "ROME",
         "Italy fines Meta \u20ac805 million over Android photo access."),
    ]),
    ("MIDDLE EAST & AFRICA", [
        (6, "RIYADH",
         "Houthi missile damages PIF tower in financial district; more "
         "missiles intercepted."),
        (7, "HORMUZ",
         "Iran war enters ninth month: tanker hits mine, burns; US cost "
         "put at $48.3bn."),
        (20, "GAZA",
         "Israeli troops cross Yellow Line first time since truce; baby "
         "dies of cold in tents."),
        (21, "IRAQ",
         "Iraqi forces deploy against Kataib Hezbollah stronghold over "
         "oil smuggling."),
        (28, "NAIROBI",
         "Kenya discharges its last Ebola patient, 37 days after its "
         "first case."),
        (29, "KENYA",
         "US consortium wins Mrima Hill minerals deal, deposits put "
         "above $60bn."),
        (30, "SUDAN",
         "Drone strike kills 10 at South Kordofan gold mine; Amnesty "
         "flags RSF attacks."),
        (31, "ETHIOPIA\u2013ERITREA",
         "Drone and artillery strikes near Badme as both sides mass "
         "troops."),
        (32, "MOGADISHU",
         "Somalia expels UAE ambassador, accusing Abu Dhabi of "
         "undermining sovereignty."),
        (33, "SENEGAL",
         "Migrant boat capsizes: dozens missing, four bodies found; "
         "Canary arrivals up."),
    ]),
    ("ASIA-PACIFIC", [
        (5, "TOKYO",
         "Nikkei falls 4.8%; SoftBank sinks 16%; Korea exchange triggers "
         "sell-side halt."),
        (23, "SEOUL",
         "Court orders retrial of ex-PM Han Duck-soo in the martial-law "
         "case."),
        (24, "SHENZHEN",
         "Japan's PM Takaichi gets cool APEC reception; first China "
         "visit since 2019."),
        (26, "DHAKA",
         "Violence flares ahead of ousted premier Hasina's planned "
         "return."),
        (27, "JAKARTA",
         "Bank Indonesia lifts benchmark rate 25 basis points to 6% to "
         "defend the rupiah."),
        (34, "FIJI",
         "Fiji and Tonga declare disasters as El Ni\u00f1o drought "
         "worsens; cyclone nears."),
    ]),
    ("AMERICAS", [
        (3, "NEW YORK",
         "Anthropic closes +17% on Nasdaq debut; record $81.3bn IPO."),
        (4, "NEW YORK",
         "S&P 500 falls 2.0%, fifth straight loss; Dow drops 1,101 "
         "points below 50,000."),
        (15, "SANTA CLARA",
         "California subpoenas Nvidia over China chip sales after CEO "
         "Huang resigns."),
        (16, "WASHINGTON",
         "White House fires cyber director after outage week; 1.5m "
         "travellers stranded."),
        (17, "WASHINGTON",
         "Senate passes energy-permitting overhaul 62\u201333 for "
         "plants, grid, data centres."),
        (19, "WASHINGTON",
         "Fed's Waller signals possible 50-point December hike; odds "
         "priced near 90%."),
        (35, "LOS ANGELES",
         "El Ni\u00f1o storm threatens LA floods; Florida river hits "
         "record flood stage."),
        (36, "PORT-AU-PRINCE",
         "Haitian forces kill 34 gang members retaking the Martissant "
         "corridor."),
        (37, "SAN SALVADOR",
         "President Bukele registers to run for a third term."),
        (38, "CARACAS",
         "US and Venezuela sign military cooperation deal; Hegseth "
         "visits Caracas."),
        (39, "BRAS\u00cdLIA",
         "Central bank sells $1bn to curb dollar; real nears 5.93, "
         "down 18% in a month."),
        (40, "BRAZIL",
         "Lula recognises Kayapo and Yudja ancestral lands with Chief "
         "Raoni, 94."),
        (41, "BOGOT\u00c1",
         "Thousands protest tax plans and call a national strike."),
        (47, "LAS VEGAS",
         "F1's Las Vegas Grand Prix weekend: teams fight over "
         "prize-money jackpot."),
    ]),
    ("SCIENCE, MONEY & CULTURE", [
        (42, "DEEP SPACE",
         "Voyager 1 reaches one light-day from Earth: 26 billion km, "
         "49 years on."),
        (43, "MERCURY",
         "BepiColombo enters Mercury orbit after eight years; second "
         "mission ever."),
        (44, "WORLDWIDE",
         "GTA VI goes on sale, tops $2.3bn \u2014 biggest entertainment "
         "launch ever."),
        (45, "NASHVILLE",
         "Ella Langley sweeps the CMA Awards: Entertainer, Female "
         "Vocalist, Song, Single."),
        (46, "SYDNEY",
         "Marathon champion Jepchirchir banned three years for doping, "
         "loses Sydney title."),
    ]),
]

# ---------------------------------------------------------------------------
# The day in numbers: (big value, small label)
# ---------------------------------------------------------------------------

NUMBERS = [
    ("9\u20136", "ICJ genocide verdict"),
    ("$81.3bn", "record IPO raised"),
    ("\u22121,101", "Dow points lost"),
    ("\u22124.8%", "Nikkei's fall"),
    ("$48.3bn", "US Iran-war cost"),
    ("100,000", "youth places a year"),
    ("26bn km", "Voyager 1, a light-day out"),
    ("$2.3bn", "GTA VI first-day sales"),
    ("100%", "debt-to-GDP warning"),
    ("51\u201348", "Senate war-powers vote"),
]

# ---------------------------------------------------------------------------
# Map pins: (story, lon, lat, nudge_x, nudge_y) -- nudges in final pixels,
# applied only where pins would otherwise collide.
# ---------------------------------------------------------------------------

PINS = [
    (1, 4.9, 52.1, 0, 0),
    (2, 114.1, 22.5, 0, 0),
    (3, -74.0, 40.7, 7, -7),
    (5, 139.7, 35.7, 0, 0),
    (6, 46.7, 24.6, 6, 2),
    (7, 56.3, 26.5, 0, 0),
    (8, 30.5, 50.4, 0, -6),
    (14, 30.7, 36.9, -8, 5),
    (15, -122.0, 37.4, -7, -6),
    (16, -77.0, 38.9, -7, 7),
    (20, 34.3, 31.4, 0, -2),
    (22, 125.8, 39.0, 0, 0),
    (26, 90.4, 23.8, 0, 0),
    (27, 106.8, -6.2, 0, 0),
    (28, 36.8, -1.3, 3, 4),
    (30, 30.5, 11.0, -2, 6),
    (31, 39.8, 14.7, 5, -3),
    (33, -17.4, 14.7, 0, 0),
    (34, 178.4, -17.6, 0, 0),
    (35, -118.2, 34.0, 6, 7),
    (36, -72.3, 18.5, 0, 0),
    (39, -47.9, -15.8, 0, 0),
    (41, -74.1, 4.6, 5, 8),
    (46, 151.2, -33.9, 0, 0),
    (47, -115.1, 36.2, 10, -8),
    (48, 12.5, 41.9, 0, 0),
]

# ---------------------------------------------------------------------------
# Dotted world map: land spans on a 120 x 28 grid.
# Column c covers lon [-170 + 3c, -167 + 3c]; row r covers
# lat [78 - 4.857r, 78 - 4.857(r+1)].  Each entry: row -> [(c0, c1), ...]
# ---------------------------------------------------------------------------

MAP_COLS = 120
MAP_ROWS = 28
MAP_SPANS = {
    0:  [(8, 14), (18, 28), (39, 45), (70, 84), (90, 104), (108, 116)],
    1:  [(2, 9), (12, 31), (38, 47), (60, 116)],
    2:  [(2, 11), (13, 34), (40, 45), (52, 52), (58, 115)],
    3:  [(3, 11), (14, 35), (55, 57), (58, 113)],
    4:  [(15, 37), (55, 56), (57, 110)],
    5:  [(16, 37), (55, 107)],
    6:  [(18, 35), (55, 102), (103, 105)],
    7:  [(18, 34), (55, 101), (103, 104)],
    8:  [(19, 33), (54, 100), (102, 103)],
    9:  [(19, 30), (53, 99)],
    10: [(20, 28), (29, 30), (52, 72), (79, 86), (89, 97)],
    11: [(21, 26), (51, 66), (69, 74), (80, 85), (89, 94), (96, 97)],
    12: [(23, 25), (51, 70), (80, 84), (89, 93), (96, 97)],
    13: [(31, 38), (51, 72), (81, 81), (88, 93)],
    14: [(31, 40), (54, 71), (87, 96)],
    15: [(31, 41), (56, 70), (89, 101)],
    16: [(32, 42), (58, 68), (92, 108)],
    17: [(32, 43), (59, 67), (95, 100), (104, 109)],
    18: [(33, 43), (60, 68), (95, 107)],
    19: [(33, 43), (60, 68), (71, 72), (95, 108)],
    20: [(34, 42), (61, 67), (96, 107)],
    21: [(34, 41), (61, 66), (97, 106)],
    22: [(35, 40), (62, 66), (98, 105), (112, 113)],
    23: [(35, 38), (113, 114)],
    24: [(35, 37), (112, 113)],
    25: [(35, 37)],
    26: [(35, 36)],
    27: [(35, 35)],
}


# ---------------------------------------------------------------------------
# Painter: thin wrapper over ImageDraw working in final-image pixels.
# ---------------------------------------------------------------------------


class Painter:
    def __init__(self, image, draw):
        self.img = image
        self.d = draw
        self._fonts = {}

    def font(self, path, size):
        from PIL import ImageFont
        key = (path, round(size * SS))
        if key not in self._fonts:
            self._fonts[key] = ImageFont.truetype(path, int(round(size * SS)))
        return self._fonts[key]

    def text_len(self, s, path, size):
        return self.d.textlength(s, font=self.font(path, size)) / SS

    def text(self, x, y, s, path, size, fill):
        self.d.text((x * SS, y * SS), s, font=self.font(path, size),
                    fill=fill)

    def text_center(self, cx, y, s, path, size, fill):
        w = self.text_len(s, path, size)
        self.text(cx - w / 2, y, s, path, size, fill)
        return w

    def tracked(self, cx, y, s, path, size, fill, tracking):
        """Letter-spaced text, horizontally centred at cx. Returns width."""
        widths = [self.text_len(ch, path, size) for ch in s]
        total = sum(widths) + tracking * max(0, len(s) - 1)
        x = cx - total / 2
        for ch, wch in zip(s, widths):
            self.text(x, y, ch, path, size, fill)
            x += wch + tracking
        return total

    def tracked_left(self, x, y, s, path, size, fill, tracking):
        widths = [self.text_len(ch, path, size) for ch in s]
        total = sum(widths) + tracking * max(0, len(s) - 1)
        cx = x
        for ch, wch in zip(s, widths):
            self.text(cx, y, ch, path, size, fill)
            cx += wch + tracking
        return total

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1.0):
        self.d.rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS],
                         fill=fill, outline=outline,
                         width=max(1, int(round(width * SS))))

    def line(self, points, fill, width=1.0):
        pts = [(x * SS, y * SS) for x, y in points]
        self.d.line(pts, fill=fill, width=max(1, int(round(width * SS))),
                    joint="curve")

    def ellipse(self, cx, cy, r, fill=None, outline=None, width=1.0):
        self.d.ellipse([(cx - r) * SS, (cy - r) * SS,
                        (cx + r) * SS, (cy + r) * SS],
                       fill=fill, outline=outline,
                       width=max(1, int(round(width * SS))))

    def polygon(self, points, fill=None, outline=None):
        pts = [(x * SS, y * SS) for x, y in points]
        self.d.polygon(pts, fill=fill, outline=outline)

    def fit_size(self, s, path, start, max_w, minimum=6.0):
        """Largest font size <= start at which s fits max_w (0.5 steps)."""
        size = start
        while size > minimum and self.text_len(s, path, size) > max_w:
            size -= 0.5
        return size

    def wrap_plain(self, s, path, size, max_w):
        """Greedy word wrap of a single-style string. Returns line list."""
        words = s.split()
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if self.text_len(trial, path, size) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------------------
# Story index layout: rich-text wrap + balanced 3-column packing.
# ---------------------------------------------------------------------------

_STYLES = {
    "n": (SANS_B, CRIMSON),   # story number
    "t": (SANS_B, INK),       # town
    "b": (SANS, INK_SOFT),    # headline body
}


def _story_words(p, num, town, head, size):
    runs = [("%d " % num, "n"), (town + " \u2014 ", "t"), (head, "b")]
    words = []
    for txt, style in runs:
        for piece in txt.split(" "):
            if piece:
                words.append((piece, style))
    return words


def _wrap_story(p, words, size, col_w):
    space_w = p.text_len(" ", SANS, size)
    lines = []
    cur = []
    cur_w = 0.0
    for word, style in words:
        path, _ = _STYLES[style]
        ww = p.text_len(word, path, size)
        add = ww if not cur else ww + space_w
        if cur and cur_w + add > col_w:
            lines.append(cur)
            cur = [(word, style)]
            cur_w = ww
        else:
            cur.append((word, style))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


INDEX_LEADING = 1.10     # index line height as a multiple of font size
INDEX_STORY_GAP = 1.4    # vertical gap after each index story


def _index_blocks(p, size, col_w):
    """Return blocks: ('h', group) or ('s', lines) with heights."""
    lh = size * INDEX_LEADING
    blocks = []
    for name, stories in GROUPS:
        blocks.append(("h", name, 6.0 + size * 1.24))
        for num, town, head in stories:
            words = _story_words(p, num, town, head, size)
            lines = _wrap_story(p, words, size, col_w)
            blocks.append(("s", lines, len(lines) * lh + INDEX_STORY_GAP))
    return blocks


def _pack_columns(blocks, avail_h):
    """Split blocks into 3 sequential columns, balanced, never ending a
    column on a group header. Returns (splits, max_height) or None."""
    n = len(blocks)
    prefix = [0.0]
    for _, _, h in blocks:
        prefix.append(prefix[-1] + h)
    best = None
    for i in range(1, n - 1):
        if blocks[i - 1][0] == "h":
            continue
        for j in range(i + 1, n):
            if blocks[j - 1][0] == "h":
                continue
            h1 = prefix[i]
            h2 = prefix[j] - prefix[i]
            h3 = prefix[n] - prefix[j]
            m = max(h1, h2, h3)
            if m <= avail_h and (best is None or m < best[1]):
                best = ((i, j), m)
    return best


def _draw_story_lines(p, lines, x, y, size):
    lh = size * INDEX_LEADING
    space_w = p.text_len(" ", SANS, size)
    for line in lines:
        cx = x
        for word, style in line:
            path, fill = _STYLES[style]
            p.text(cx, y, word, path, size, fill)
            cx += p.text_len(word, path, size) + space_w
        y += lh
    return y


# ---------------------------------------------------------------------------
# Lead-panel scenes.  Each draws inside (x0, y0, w, h) local box.
# ---------------------------------------------------------------------------


def _skyline(p, x0, base, w, heights, colour):
    """Simple blocky skyline sitting on the baseline `base`."""
    n = len(heights)
    step = w / n
    for i, hgt in enumerate(heights):
        bx = x0 + i * step + 1.5
        p.rect(bx, base - hgt, bx + step - 3, base, fill=colour)


def _flag_us(p, x, y, w, h):
    stripe = h / 7.0
    for i in range(7):
        fill = CRIMSON if i % 2 == 0 else WHITE
        p.rect(x, y + i * stripe, x + w, y + (i + 1) * stripe, fill=fill)
    p.rect(x, y, x + w * 0.45, y + stripe * 4, fill=(40, 60, 140))
    for r in range(3):
        for c in range(4):
            p.ellipse(x + 3 + c * (w * 0.45 - 6) / 3,
                      y + 3 + r * (stripe * 4 - 6) / 2, 0.8, fill=WHITE)


def _flag_china(p, x, y, w, h):
    p.rect(x, y, x + w, y + h, fill=CRIMSON)
    p.ellipse(x + w * 0.24, y + h * 0.28, 3.2, fill=GOLD)
    for dx, dy in [(0.52, 0.14), (0.58, 0.34), (0.52, 0.52)]:
        p.ellipse(x + w * dx, y + h * dy, 1.4, fill=GOLD)


def _flag_russia(p, x, y, w, h):
    third = h / 3.0
    p.rect(x, y, x + w, y + third, fill=WHITE)
    p.rect(x, y + third, x + w, y + 2 * third, fill=(60, 90, 160))
    p.rect(x, y + 2 * third, x + w, y + h, fill=CRIMSON)


def scene_summit(p, x0, y0, w, h):
    base = y0 + h - 16
    _skyline(p, x0, base - 14, w,
             [22, 32, 18, 27, 36, 20, 30, 24, 34, 19, 28, 23], TEAL_DARK)
    _skyline(p, x0, base - 14, w,
             [10, 15, 8, 13, 17, 9, 14, 11, 16, 8, 12, 10], TEAL)
    # Three flag poles with flags.
    flag_w, flag_h = 37, 24
    pole_top = y0 + 4
    for i, draw_flag in enumerate((_flag_us, _flag_china, _flag_russia)):
        px = x0 + w * (0.25 + 0.25 * i)
        p.line([(px, pole_top), (px, base - 12)], INK, 1.6)
        draw_flag(p, px + 1.5, pole_top, flag_w, flag_h)
    # Conference table band with three name plates.
    p.rect(x0 + 26, base - 12, x0 + w - 26, base - 2, fill=INK)
    for i in range(3):
        cx = x0 + w * (0.25 + 0.25 * i)
        p.rect(cx - 12, base - 9.5, cx + 12, base - 4.5, fill=WHITE)
    # Harbour reflections: short wavy dashes below the table.
    for row in range(3):
        yy = base + 2.5 + row * 4.5
        x = x0 + 14 + row * 9
        while x < x0 + w - 34:
            p.line([(x, yy), (x + 20, yy)], TEAL, 1.2)
            x += 34


def scene_court(p, x0, y0, w, h):
    cx = x0 + w / 2
    base = y0 + h - 4
    # Entrance steps.
    for i, half in enumerate((112, 100, 88)):
        p.rect(cx - half, base - 4 - i * 4, cx + half, base - i * 4,
               fill=INK_SOFT)
    col_top = y0 + 24
    col_bot = base - 12
    # Columns with capitals and bases.
    for i in range(4):
        colx = cx - 82 + i * 55
        p.rect(colx - 5, col_top, colx + 5, col_bot, fill=INK)
        p.rect(colx - 8, col_top - 4, colx + 8, col_top, fill=INK)
        p.rect(colx - 8, col_bot, colx + 8, col_bot + 3.5, fill=INK)
    # Entablature and pediment with gold disc.
    p.rect(cx - 108, col_top - 9, cx + 108, col_top - 4, fill=INK)
    p.polygon([(cx - 118, col_top - 9), (cx + 118, col_top - 9),
               (cx, y0 + 1)], fill=TEAL_DARK)
    p.ellipse(cx, col_top - 12.5, 4.6, fill=GOLD)
    # Scales silhouette at the left.
    sx = x0 + 26
    stop = y0 + 16
    sbot = y0 + h - 20
    p.line([(sx, stop), (sx, sbot)], INK, 1.8)
    p.line([(sx - 15, stop + 3), (sx + 15, stop + 3)], INK, 1.8)
    for side in (-15, 15):
        tipx = sx + side
        p.line([(tipx, stop + 3), (tipx - 6, stop + 17)], GOLD, 1.2)
        p.line([(tipx, stop + 3), (tipx + 6, stop + 17)], GOLD, 1.2)
        p.line([(tipx - 7, stop + 17), (tipx + 7, stop + 17)], GOLD, 1.8)
    p.rect(sx - 8, sbot, sx + 8, sbot + 3, fill=INK)
    # Gavel at the right: diagonal handle, head, sound block.
    gx = x0 + w - 40
    gy = y0 + 22
    p.line([(gx - 10, gy + 26), (gx + 12, gy + 2)], INK, 3.2)
    p.rect(gx + 4, gy - 5, gx + 24, gy + 5, fill=INK)
    p.rect(gx - 16, gy + 30, gx + 14, gy + 34, fill=INK_SOFT)


def scene_markets(p, x0, y0, w, h):
    base = y0 + h - 6
    _skyline(p, x0, base, w,
             [16, 26, 12, 30, 20, 34, 15, 25, 18, 29, 13, 22], INK)
    # Falling crimson line and rising green line, crossing mid-panel.
    p.line([(x0 + 4, y0 + 8), (x0 + w * 0.38, y0 + 24),
            (x0 + w * 0.68, y0 + 36), (x0 + w - 4, y0 + 50)],
           CRIMSON, 2.6)
    p.line([(x0 + 4, y0 + 54), (x0 + w * 0.36, y0 + 42),
            (x0 + w * 0.66, y0 + 28), (x0 + w - 4, y0 + 10)],
           GREEN, 2.6)
    # Six candlesticks across the front.
    candles = [  # (centre offset, body top, body bottom, colour)
        (0.10, 18, 34, GREEN), (0.25, 26, 44, CRIMSON),
        (0.42, 20, 33, GREEN), (0.58, 32, 50, CRIMSON),
        (0.74, 24, 40, CRIMSON), (0.90, 14, 30, GREEN),
    ]
    for frac, top, bot, colour in candles:
        cxp = x0 + w * frac
        p.line([(cxp, y0 + top - 6), (cxp, y0 + bot + 6)], colour, 1.4)
        p.rect(cxp - 6, y0 + top, cxp + 6, y0 + bot, fill=colour)


# ---------------------------------------------------------------------------
# Page sections
# ---------------------------------------------------------------------------


def draw_masthead(p):
    cx = W / 2
    p.tracked(cx, 28, "THE WORLD'S NEWS \u00b7 ON ONE PAGE",
              SANS_B, 10.5, INK_SOFT, 4.0)
    title = "ONE DAY, ONE PLANET"
    size = p.fit_size(title, SERIF_B, 96, 950)
    p.text_center(cx, 44, title, SERIF_B, size, INK)
    p.text_center(cx, 116, "Friday 20 November 2026", SERIF_B, 23, CRIMSON)
    p.tracked(cx, 148, "48 STORIES \u00b7 7 REGIONS \u00b7 ONE DAY",
              SANS_B, 11, INK, 3.0)
    p.line([(MARGIN, 170), (W - MARGIN, 170)], INK, 2.6)
    p.line([(MARGIN, 175), (W - MARGIN, 175)], INK, 0.9)


def draw_ticker(p):
    band_y, band_h = 184, 24
    p.rect(MARGIN, band_y, W - MARGIN, band_y + band_h, fill=PAPER_DARK)
    segments = [
        ("S&P 500 ", INK), ("\u25bc 2.0%", CRIMSON), ("   \u00b7   ", INK_SOFT),
        ("DOW ", INK), ("\u25bc 1,101 BELOW 50,000", CRIMSON),
        ("   \u00b7   ", INK_SOFT),
        ("NIKKEI ", INK), ("\u25bc 4.8%", CRIMSON), ("   \u00b7   ", INK_SOFT),
        ("SOFTBANK ", INK), ("\u25bc 16%", CRIMSON),
        ("   \u00b7   ", INK_SOFT),
        ("ANTHROPIC ", INK), ("\u25b2 17%", GREEN), (" NASDAQ DEBUT", INK),
    ]
    size = 11.5
    total = sum(p.text_len(t, SANS_B, size) for t, _ in segments)
    while total > CONTENT_W - 14 and size > 9.0:
        size -= 0.5
        total = sum(p.text_len(t, SANS_B, size) for t, _ in segments)
    x = (W - total) / 2
    y = band_y + (band_h - size) / 2 - 1.5
    for txt, fill in segments:
        p.text(x, y, txt, SANS_B, size, fill)
        x += p.text_len(txt, SANS_B, size)


LEADS = [
    ("SHENZHEN \u00b7 SUMMIT", scene_summit,
     "Trump, Xi and Putin hold first three-way summit",
     "Four-point peace declaration signed after ~70 minutes of talks."),
    ("THE HAGUE \u00b7 WORLD COURT", scene_court,
     "ICJ rules Myanmar committed genocide against the Rohingya",
     "First state ever held responsible \u2014 verdict 9\u20136; "
     "1.3m displaced."),
    ("NEW YORK \u00b7 MARKETS", scene_markets,
     "Anthropic's record $81.3bn IPO closes +17%",
     "But the Dow falls 1,101 points as an AI sell-off bites."),
]


def draw_lead(p, x, y, w, h, label, scene_fn, headline, deck):
    p.rect(x, y, x + w, y + h, fill=CARD, outline=RULE_SOFT, width=1.0)
    p.rect(x, y, x + w, y + 22, fill=TEAL_DARK)
    p.tracked_left(x + 12, y + 5.5, label, SANS_B, 11, WHITE, 1.5)
    scene_fn(p, x + 12, y + 28, w - 24, 68)
    hy = y + 103
    size = 18.0
    lines = p.wrap_plain(headline, SERIF_B, size, w - 24)
    while len(lines) > 3 and size > 13.0:
        size -= 0.5
        lines = p.wrap_plain(headline, SERIF_B, size, w - 24)
    for ln in lines:
        p.text(x + 12, hy, ln, SERIF_B, size, INK)
        hy += size * 1.18
    hy += 3
    for ln in p.wrap_plain(deck, SANS, 11.5, w - 24)[:2]:
        p.text(x + 12, hy, ln, SANS, 11.5, INK_SOFT)
        hy += 14.5


def draw_leads(p):
    y, h, w = 216, 200, 316
    for i, (label, fn, head, deck) in enumerate(LEADS):
        draw_lead(p, MARGIN + i * (w + 12), y, w, h, label, fn, head, deck)


def draw_map(p):
    x0, y0, w, h = MARGIN, 446, CONTENT_W, 84
    p.tracked_left(MARGIN, 428, "THE DAY ON THE MAP", SANS_B, 12.5, INK, 2.0)
    note = "numbered pins mark index stories"
    nw = p.text_len(note, SANS, 10)
    p.text(W - MARGIN - nw, 430, note, SANS, 10, INK_SOFT)
    cell_w = w / MAP_COLS
    cell_h = h / MAP_ROWS
    for row, spans in MAP_SPANS.items():
        cy = y0 + (row + 0.5) * cell_h
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cx = x0 + (c + 0.5) * cell_w
                p.ellipse(cx, cy, 1.4, fill=MAP_DOT)

    def project(lon, lat):
        return (x0 + (lon + 170) / 360.0 * w,
                y0 + (78 - lat) / 136.0 * h)

    for label, lon, lat in [("N. AMERICA", -152, 30), ("EUROPE", -28, 50),
                            ("AFRICA", 78, -22), ("ASIA-PACIFIC", 158, 8)]:
        lx, ly = project(lon, lat)
        p.tracked(lx, ly - 4, label, SANS_B, 8.5, MAP_LABEL, 2.0)
    for num, lon, lat, dx, dy in PINS:
        cx, cy = project(lon, lat)
        cx += dx
        cy += dy
        p.ellipse(cx, cy, 7.5, fill=CRIMSON)
        s = str(num)
        tw = p.text_len(s, SANS_B, 8)
        p.text(cx - tw / 2, cy - 3.4, s, SANS_B, 8, WHITE)


def draw_index(p):
    x0, y0, avail_h = MARGIN, 546, 380
    col_w, gap = 316, 12
    chosen = None
    for size in (10.0, 9.5, 9.25, 9.0, 8.75, 8.5, 8.25, 8.0, 7.75, 7.5):
        blocks = _index_blocks(p, size, col_w)
        packed = _pack_columns(blocks, avail_h)
        if packed is not None:
            chosen = (size, blocks, packed[0])
            break
    if chosen is None:
        size = 8.0
        blocks = _index_blocks(p, size, col_w)
        packed = _pack_columns(blocks, avail_h + 100000)
        chosen = (size, blocks, packed[0])
    size, blocks, (i, j) = chosen
    columns = [blocks[:i], blocks[i:j], blocks[j:]]
    for ci, col_blocks in enumerate(columns):
        x = x0 + ci * (col_w + gap)
        y = y0
        for bi, (kind, payload, bh) in enumerate(col_blocks):
            if kind == "h":
                if bi > 0:
                    p.line([(x, y + 3), (x + col_w, y + 3)], RULE_SOFT, 0.8)
                    p.tracked_left(x, y + 8, payload, SANS_B,
                                   size + 0.5, TEAL_DARK, 1.2)
                else:
                    p.tracked_left(x, y, payload, SANS_B,
                                   size + 0.5, TEAL_DARK, 1.2)
            else:
                _draw_story_lines(p, payload, x, y, size)
            y += bh


def draw_numbers(p):
    y_rule = 930
    p.line([(MARGIN, y_rule), (W - MARGIN, y_rule)], INK, 1.1)
    p.tracked_left(MARGIN, y_rule + 8, "THE DAY IN NUMBERS",
                   SANS_B, 11, CRIMSON, 3.0)
    cell_w = CONTENT_W / len(NUMBERS)
    val_y = y_rule + 26
    for i, (value, label) in enumerate(NUMBERS):
        cx = MARGIN + cell_w * (i + 0.5)
        if i > 0:
            sx = MARGIN + cell_w * i
            p.line([(sx, val_y + 2), (sx, val_y + 40)], RULE_SOFT, 0.8)
        size = p.fit_size(value, SERIF_B, 22, cell_w - 6)
        p.text_center(cx, val_y, value, SERIF_B, size, INK)
        ly = val_y + 27
        for ln in p.wrap_plain(label.upper(), SANS_B, 6.8, cell_w - 8)[:2]:
            lw = p.text_len(ln, SANS_B, 6.8)
            p.text(cx - lw / 2, ly, ln, SANS_B, 6.8, INK_SOFT)
            ly += 8.6


def render():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W * SS, H * SS), PAPER)
    p = Painter(img, ImageDraw.Draw(img))
    draw_masthead(p)
    draw_ticker(p)
    draw_leads(p)
    draw_map(p)
    draw_index(p)
    draw_numbers(p)
    p.rect(12, 12, W - 12, H - 12, outline=INK, width=1.6)
    p.rect(17.5, 17.5, W - 17.5, H - 17.5, outline=INK, width=0.7)
    return img.resize((W, H), Image.LANCZOS)


def _output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, "entry.png")


def main():
    out = _output_path()
    try:
        from PIL import Image, ImageDraw  # noqa: F401
    except ImportError:
        bundled = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "entry.png")
        shutil.copyfile(bundled, out)
        return
    render().save(out, format="PNG")


if __name__ == "__main__":
    main()
