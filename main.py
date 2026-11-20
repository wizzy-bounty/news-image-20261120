#!/usr/bin/env python3
"""ONE DAY, ONE PLANET — a one-page broadsheet of Friday 20 November 2026.

Entry program for the make.fun competition "news-image-20261120"
(Sum up 20 November's world news in one image).

The program writes a single 1024x1024 PNG to /output/entry.png (or to
$MAKEFUN_OUTPUT_DIR/entry.png when that variable is set).  It draws the
front page itself with Pillow when Pillow and suitable fonts are
available; on any failure it falls back to copying the bundled
entry.png byte-for-byte, so the output is always a valid image.

Deterministic: no network, no clock, no randomness — two runs in the
same environment write identical bytes.  Standard library only, apart
from the optional Pillow import, which is guarded.

v2 refinement (same day, same 48 stories): a markets ticker strip
under the masthead, richer lead-panel scenes, a larger story index
(tighter leading and gutters), four more map pins with faint region
labels, and a tenth Day-in-Numbers figure.
"""

import os
import shutil
import sys

# --------------------------------------------------------------------------
# Canvas / palette (all layout numbers are in final-image pixels; the page
# is drawn at SS x supersampling and downsampled with Lanczos).
# --------------------------------------------------------------------------

SS = 2
W = H = 1024

PAPER = (247, 243, 233)        # warm cream newsprint
PAPER_DARK = (238, 231, 214)   # shaded band
CARD = (253, 251, 245)         # panel card
INK = (18, 32, 54)             # ink navy
INK_SOFT = (58, 72, 96)        # softened ink for body text
TEAL = (0, 100, 106)           # deep teal
TEAL_DARK = (0, 74, 80)
CRIMSON = (176, 32, 50)
CRIMSON_DARK = (140, 24, 40)
GOLD = (196, 142, 40)
GREEN = (28, 128, 74)
MAP_DOT = (122, 148, 148)
RULE = (18, 32, 54)

MARGIN = 26
CONTENT_W = W - 2 * MARGIN     # 972

# --------------------------------------------------------------------------
# The day's stories.  (number, place tag, headline) — facts as reported on
# Friday 20 November 2026.  Grouped by region for the index.
# --------------------------------------------------------------------------

GROUPS = [
    ("WORLD", [
        (1, "THE HAGUE",
         "ICJ rules Myanmar committed genocide against the Rohingya, 9\u20136; "
         "1.3 million displaced."),
        (2, "SHENZHEN",
         "Trump, Xi and Putin hold first three-way summit; four-point peace "
         "declaration signed."),
        (10, "BERLIN",
         "Ukraine's allies say Europe is ready to talk with Russia; "
         "NATO-style guarantee floated."),
        (13, "BRUSSELS",
         "UK\u2013EU reset: \u00a35.1bn food-trade deal, carbon link, 100,000 "
         "youth places a year."),
        (18, "WASHINGTON",
         "IMF warns global public debt will soon hit 100% of world GDP, "
         "highest since WWII."),
        (22, "PYONGYANG",
         "IAEA says North Korea is expanding uranium enrichment at Yongbyon."),
        (25, "ULAANBAATAR",
         "Mongolia's President Kh\u00fcrels\u00fckh resigns; speaker becomes "
         "acting president."),
    ]),
    ("EUROPE", [
        (8, "KYIV",
         "Russian overnight strikes target bridges, kill eight; 28 hurt "
         "across nine regions."),
        (9, "CRIMEA",
         "Ukraine hits Kerch Bridge for third time in a week; rail halted, "
         "Putin vows reply."),
        (11, "WARSAW",
         "Russia violates Poland's airspace overnight with two missiles "
         "and a drone."),
        (12, "TALLINN",
         "Estonia to close Russia border for six months; Moscow cries new "
         "Iron Curtain."),
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
         "Senate passes energy-permitting overhaul 62\u201333 for plants, "
         "grid, data centres."),
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

# The day in numbers: (big value, small label)
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

# --------------------------------------------------------------------------
# Dotted world map: land spans per row of a 100 x 26 grid.
# Row 0 is ~77N, row 25 is ~-48; column 0 is 180W, column 99 is ~176E.
# Each entry maps a row index to a list of (first_col, last_col) land runs.
# --------------------------------------------------------------------------

MAP_ROWS = 26
MAP_COLS = 100
MAP_SPANS = {
    0:  [(10, 13), (17, 20), (23, 25), (31, 37), (58, 61), (66, 69),
         (76, 80), (85, 89)],
    1:  [(3, 9), (12, 27), (31, 37), (48, 51), (55, 92)],
    2:  [(2, 10), (13, 30), (32, 36), (42, 42), (47, 92)],
    3:  [(3, 10), (14, 31), (33, 35), (48, 52), (55, 91)],
    4:  [(15, 32), (44, 45), (48, 89)],
    5:  [(16, 31), (44, 44), (46, 53), (55, 86)],
    6:  [(15, 30), (45, 53), (55, 62), (63, 72), (73, 86), (89, 90)],
    7:  [(14, 29), (45, 52), (55, 60), (62, 72), (74, 87), (88, 90)],
    8:  [(13, 28), (44, 56), (58, 63), (64, 70), (71, 76), (77, 88)],
    9:  [(12, 26), (42, 58), (58, 63), (65, 71), (71, 77), (78, 89)],
    10: [(11, 22), (40, 58), (59, 63), (70, 76), (79, 84), (85, 88)],
    11: [(11, 19), (24, 27), (40, 52), (53, 59), (70, 75), (79, 83),
         (86, 88)],
    12: [(12, 16), (26, 32), (39, 48), (55, 61), (71, 74), (79, 83),
         (85, 88)],
    13: [(25, 33), (40, 50), (53, 58), (79, 82), (83, 86), (89, 91)],
    14: [(24, 33), (44, 54), (80, 84), (87, 90), (92, 94)],
    15: [(25, 32), (45, 53), (79, 83), (86, 89), (92, 94)],
    16: [(25, 33), (46, 54), (82, 86), (89, 93)],
    17: [(26, 33), (47, 55), (88, 95)],
    18: [(26, 34), (47, 56), (82, 90)],
    19: [(27, 34), (48, 56), (58, 58), (80, 91)],
    20: [(27, 33), (48, 55), (57, 58), (80, 90)],
    21: [(28, 33), (49, 54), (81, 89)],
    22: [(28, 32), (49, 52), (82, 88), (95, 95)],
    23: [(28, 31), (94, 95)],
    24: [(28, 30), (93, 94)],
    25: [(28, 30)],
}

# Map pins: (story number, longitude, latitude)
PINS = [
    (1, 4.9, 52.1), (2, 114.1, 22.5), (3, -74.0, 40.7), (5, 139.7, 35.7),
    (6, 46.7, 24.6), (7, 56.3, 26.5), (8, 30.5, 50.4), (14, 30.7, 36.9),
    (15, -122.0, 37.4), (16, -77.0, 38.9), (20, 34.3, 31.4),
    (22, 125.8, 39.0), (26, 90.4, 23.8), (27, 106.8, -6.2),
    (28, 36.8, -1.3), (30, 30.5, 11.0), (31, 39.8, 14.7),
    (33, -17.4, 14.7), (34, 178.4, -17.6),
    (35, -118.2, 34.0), (36, -72.3, 18.5), (39, -47.9, -15.8),
    (41, -74.1, 4.6), (46, 151.2, -33.9), (47, -115.1, 36.2),
    (48, 12.5, 41.9),
]

# --------------------------------------------------------------------------
# Fonts.  Core fonts must be found, otherwise we raise and the caller
# falls back to the bundled PNG (whose rendering is known-good).
# --------------------------------------------------------------------------

_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts",
]


def _find_font(*names):
    for d in _FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    return None


class Fonts:
    def __init__(self, ImageFont):
        serif_b = _find_font("DejaVuSerif-Bold.ttf",
                             "LiberationSerif-Bold.ttf")
        serif = _find_font("DejaVuSerif.ttf", "LiberationSerif-Regular.ttf")
        sans_b = _find_font("DejaVuSans-Bold.ttf",
                            "LiberationSans-Bold.ttf")
        sans = _find_font("DejaVuSans.ttf", "LiberationSans-Regular.ttf")
        if not all([serif_b, serif, sans_b, sans]):
            raise RuntimeError("core fonts not available")
        self._paths = {"serif_b": serif_b, "serif": serif,
                       "sans_b": sans_b, "sans": sans}
        self._ImageFont = ImageFont
        self._cache = {}

    def get(self, kind, size):
        """size is in final-image pixels; returns a supersampled font."""
        key = (kind, size)
        if key not in self._cache:
            self._cache[key] = self._ImageFont.truetype(
                self._paths[kind], int(round(size * SS)))
        return self._cache[key]


# --------------------------------------------------------------------------
# Small drawing helpers (all coordinates in final-image pixels).
# --------------------------------------------------------------------------


def S(v):
    return int(round(v * SS))


def rect(d, box, **kw):
    d.rectangle([S(box[0]), S(box[1]), S(box[2]), S(box[3])], **kw)


def line(d, pts, **kw):
    d.line([(S(x), S(y)) for x, y in pts], **kw)


def ellipse(d, box, **kw):
    d.ellipse([S(box[0]), S(box[1]), S(box[2]), S(box[3])], **kw)


def polygon(d, pts, **kw):
    d.polygon([(S(x), S(y)) for x, y in pts], **kw)


def text(d, xy, s, font, fill=INK, anchor="la"):
    d.text((S(xy[0]), S(xy[1])), s, font=font, fill=fill, anchor=anchor)


def text_w(d, s, font):
    return d.textlength(s, font=font) / SS


def wrap(d, s, font, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    words = s.split()
    lines = []
    cur = ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if text_w(d, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def tracked(d, xy, s, font, fill, tracking, anchor="la"):
    """Draw text with extra letter tracking (in final-image pixels)."""
    widths = [text_w(d, ch, font) for ch in s]
    total = sum(widths) + tracking * max(0, len(s) - 1)
    x = xy[0]
    if anchor == "ma":
        x -= total / 2
    elif anchor == "ra":
        x -= total
    for ch, wch in zip(s, widths):
        d.text((S(x), S(xy[1])), ch, font=font, fill=fill, anchor="la")
        x += wch + tracking
    return total


# --------------------------------------------------------------------------
# Lead-panel scenes.  Each draws inside the box (x, y, w, h).
# --------------------------------------------------------------------------


def scene_summit(d, x, y, w, h):
    """Skyline, sun, and three flags for the Shenzhen three-way summit.

    Drawn in a 250x90 design space mapped onto the scene box, so nothing
    can spill outside it.
    """
    def sx(v):
        return x + v * w / 250.0

    def sy(v):
        return y + v * h / 90.0

    # sky
    rect(d, (x, y, x + w, y + h), fill=(233, 240, 238))
    # sun
    ellipse(d, (sx(208), sy(5), sx(234), sy(31)), fill=GOLD)
    # skyline silhouette (two depth layers)
    back = [(0, 62), (26, 62), (26, 44), (44, 44), (44, 66), (70, 66),
            (70, 38), (92, 38), (92, 62), (118, 62), (118, 50), (140, 50),
            (140, 66), (168, 66), (168, 42), (190, 42), (190, 62),
            (216, 62), (216, 54), (238, 54), (238, 66), (250, 66)]
    pts = [(sx(px), sy(py)) for px, py in back]
    polygon(d, pts + [(sx(250), sy(90)), (sx(0), sy(90))],
            fill=(150, 178, 176))
    front = [(0, 76), (34, 76), (34, 58), (58, 58), (58, 80), (96, 80),
             (96, 54), (124, 54), (124, 76), (158, 76), (158, 62),
             (184, 62), (184, 80), (220, 80), (220, 66), (250, 66)]
    pts = [(sx(px), sy(py)) for px, py in front]
    polygon(d, pts + [(sx(250), sy(90)), (sx(0), sy(90))], fill=TEAL_DARK)
    # ground
    rect(d, (x, sy(80), x + w, y + h), fill=INK)
    # skyline reflections shimmering in the harbour strip
    for rx in (44, 96, 140, 190):
        rect(d, (sx(rx), sy(81.5), sx(rx + 7), sy(88)),
             fill=(64, 96, 104))
    rect(d, (sx(212), sy(81.5), sx(218), sy(87)), fill=(96, 84, 48))
    # three flag poles with flags (US, China, Russia — simplified)
    for i, cxd in enumerate((62, 118, 174)):
        cx = sx(cxd)
        line(d, [(cx, sy(80)), (cx, sy(28))], fill=INK, width=S(1.8))
        fw, fh = 30 * w / 250.0, 13.5
        fx0, fy0 = cx + 2, sy(28)
        if i == 0:      # United States: stripes + blue canton
            rect(d, (fx0, fy0, fx0 + fw, fy0 + fh), fill=(246, 244, 238),
                 outline=INK_SOFT)
            for k in range(3):
                yy = fy0 + fh * (0.14 + 0.30 * k)
                rect(d, (fx0, yy, fx0 + fw, yy + fh * 0.15), fill=CRIMSON)
            rect(d, (fx0, fy0, fx0 + fw * 0.42, fy0 + fh * 0.52),
                 fill=(40, 60, 130))
        elif i == 1:    # China: red field, gold stars
            rect(d, (fx0, fy0, fx0 + fw, fy0 + fh), fill=(206, 40, 44),
                 outline=INK_SOFT)
            ellipse(d, (fx0 + fw * 0.08, fy0 + fh * 0.14,
                        fx0 + fw * 0.26, fy0 + fh * 0.50), fill=GOLD)
            ellipse(d, (fx0 + fw * 0.36, fy0 + fh * 0.10,
                        fx0 + fw * 0.48, fy0 + fh * 0.32), fill=GOLD)
            ellipse(d, (fx0 + fw * 0.38, fy0 + fh * 0.44,
                        fx0 + fw * 0.50, fy0 + fh * 0.66), fill=GOLD)
        else:           # Russia: white / blue / red bands
            rect(d, (fx0, fy0, fx0 + fw, fy0 + fh), fill=(246, 244, 238),
                 outline=INK_SOFT)
            rect(d, (fx0, fy0 + fh / 3, fx0 + fw, fy0 + 2 * fh / 3),
                 fill=(40, 84, 166))
            rect(d, (fx0, fy0 + 2 * fh / 3, fx0 + fw, fy0 + fh),
                 fill=CRIMSON)
    # conference table in front of the flags, with three name plates
    polygon(d, [(sx(46), sy(76)), (sx(204), sy(76)), (sx(216), sy(84)),
                (sx(34), sy(84))], fill=TEAL_DARK)
    line(d, [(sx(46), sy(76)), (sx(204), sy(76))], fill=GOLD,
         width=S(1.2))
    for cxd in (62, 118, 174):
        rect(d, (sx(cxd - 7), sy(78.5), sx(cxd + 7), sy(81)), fill=GOLD)


def scene_court(d, x, y, w, h):
    """Courthouse facade and scales of justice for the ICJ ruling.

    Drawn in a 250x90 design space mapped onto the scene box.
    """
    def sx(v):
        return x + v * w / 250.0

    def sy(v):
        return y + v * h / 90.0

    rect(d, (x, y, x + w, y + h), fill=(240, 238, 228))
    cx = sx(125)
    # pediment, with a gold disc at its centre
    polygon(d, [(sx(37), sy(26)), (sx(213), sy(26)), (sx(125), sy(6))],
            fill=TEAL)
    ellipse(d, (sx(119), sy(13), sx(131), sy(25)), fill=GOLD)
    rect(d, (sx(14), sy(28), sx(236), sy(33)), fill=TEAL_DARK)
    # columns with capitals and bases
    for k in range(5):
        cxx = sx(30 + k * 47.5)
        rect(d, (cxx - 5, sy(36), cxx + 5, sy(76)), fill=(192, 184, 158))
        rect(d, (cxx - 7, sy(36), cxx + 7, sy(39.5)), fill=(172, 162, 134))
        rect(d, (cxx - 7, sy(72.5), cxx + 7, sy(76)), fill=(172, 162, 134))
    rect(d, (sx(14), sy(76), sx(236), sy(82)), fill=TEAL_DARK)
    # two entrance steps below the base
    rect(d, (sx(8), sy(82), sx(242), sy(85.5)), fill=(192, 184, 158))
    rect(d, (sx(2), sy(85.5), sx(248), sy(89)), fill=(172, 162, 134))
    # scales: pillar, beam, two pans
    line(d, [(cx, sy(38)), (cx, sy(72))], fill=INK, width=S(3))
    line(d, [(sx(73), sy(42)), (sx(177), sy(42))], fill=INK, width=S(3))
    ellipse(d, (cx - 6, sy(33), cx + 6, sy(45)), fill=GOLD)
    for pxd in (73, 177):
        px = sx(pxd)
        line(d, [(px, sy(42)), (px - 13, sy(64))], fill=INK, width=S(1.5))
        line(d, [(px, sy(42)), (px + 13, sy(64))], fill=INK, width=S(1.5))
        d.arc([S(px - 15), S(sy(52)), S(px + 15), S(sy(74))],
              start=0, end=180, fill=GOLD, width=S(3))
    # base + gavel resting to the right
    rect(d, (cx - 16, sy(72), cx + 16, sy(77)), fill=INK)
    line(d, [(sx(183), sy(74)), (sx(207), sy(58))], fill=CRIMSON_DARK,
         width=S(3))
    rect(d, (sx(200), sy(48), sx(214), sy(58)), fill=CRIMSON)
    ellipse(d, (sx(198), sy(58), sx(216), sy(62)), fill=CRIMSON_DARK)


def scene_markets(d, x, y, w, h):
    """Plunging index line against a rising IPO line, over a skyline."""
    rect(d, (x, y, x + w, y + h), fill=(24, 36, 58))
    # dashed grid
    for gy in (0.25, 0.5, 0.75):
        yy = y + h * gy
        xx = x + 8
        while xx < x + w - 10:
            line(d, [(xx, yy), (xx + 7, yy)], fill=(90, 110, 140),
                 width=S(1))
            xx += 13
    # skyline at bottom
    bars = [(0, 18), (22, 30), (48, 22), (74, 38), (104, 26), (132, 34),
            (162, 20), (190, 30), (220, 28)]
    for bx, bh in bars:
        px = x + bx * w / 250.0
        rect(d, (px, y + h - bh, px + w * 20 / 250.0, y + h),
             fill=(52, 74, 104))
    # candlesticks floating above the skyline (mostly red on the day)
    candles = [(0.06, 30, 16, False), (0.16, 34, 12, False),
               (0.38, 40, 14, True), (0.60, 48, 18, False),
               (0.82, 58, 13, False), (0.90, 64, 10, True)]
    for fx, base_h, hgt, up in candles:
        cxp = x + fx * w
        col = GREEN if up else CRIMSON
        line(d, [(cxp, y + h - base_h - hgt), (cxp, y + h - base_h + 4)],
             fill=col, width=S(1.2))
        rect(d, (cxp - 3.5, y + h - base_h - hgt * 0.7,
                 cxp + 3.5, y + h - base_h), fill=col)
    # rising green line (the IPO)
    up = [(x + 10, y + h - 24), (x + w * 0.3, y + h - 36),
          (x + w * 0.52, y + h - 46), (x + w * 0.72, y + h - 56)]
    line(d, up, fill=GREEN, width=S(3))
    polygon(d, [(x + w * 0.72, y + h - 56), (x + w * 0.72 - 9,
              y + h - 50), (x + w * 0.72 - 2, y + h - 46)], fill=GREEN)
    # plunging crimson line (the Dow)
    dn = [(x + 10, y + 14), (x + w * 0.3, y + 26), (x + w * 0.52, y + 44),
          (x + w * 0.74, y + 66), (x + w * 0.94, y + h - 30)]
    line(d, dn, fill=CRIMSON, width=S(3.5))
    polygon(d, [(x + w * 0.94, y + h - 30), (x + w * 0.94 - 11, y + h - 32),
                (x + w * 0.94 - 4, y + h - 20)], fill=CRIMSON)

# --------------------------------------------------------------------------
# Index layout: rich-text wrapping (bold number + place, regular headline)
# and a column-flow planner that picks the largest font size that fits.
# --------------------------------------------------------------------------

INDEX_Y0 = 456
INDEX_Y1 = 946
COL_X = [MARGIN, MARGIN + 326, MARGIN + 652]
COL_W = 310


def rich_lines(d, segments, max_w, space_font):
    """Wrap styled segments into lines of (word, font, fill) tuples."""
    words = []
    for txt, fnt, fill in segments:
        for w_ in txt.split(" "):
            if w_:
                words.append((w_, fnt, fill, text_w(d, w_, fnt)))
    space_w = text_w(d, " ", space_font)
    lines = []
    cur = []
    cur_w = 0.0
    for w_ in words:
        add = w_[3] if not cur else w_[3] + space_w
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur = [w_]
            cur_w = w_[3]
        else:
            cur.append(w_)
            cur_w += add
    if cur:
        lines.append(cur)
    return lines, space_w


def story_segments(fonts, size, num, place, headline):
    return [
        ("%d" % num, fonts.get("sans_b", size), CRIMSON),
        (" %s \u2014 " % place, fonts.get("sans_b", size), INK),
        (headline, fonts.get("sans", size), INK_SOFT),
    ]


def plan_index(d, fonts, size):
    """Return placements [(kind, col, y, payload)] or None if it overflows."""
    lh = size * 1.21
    gap = 3.4
    header_h = 19.5
    placements = []
    col = 0
    y = INDEX_Y0

    def story_lines(st):
        segs = story_segments(fonts, size, st[0], st[1], st[2])
        lines, _ = rich_lines(d, segs, COL_W, fonts.get("sans", size))
        return lines

    for gname, stories in GROUPS:
        first_h = len(story_lines(stories[0])) * lh + gap
        if y + header_h + first_h > INDEX_Y1:
            col += 1
            y = INDEX_Y0
            if col > 2:
                return None
        placements.append(("header", col, y, gname))
        y += header_h
        for st in stories:
            lines = story_lines(st)
            hh = len(lines) * lh + gap
            if y + hh > INDEX_Y1:
                col += 1
                y = INDEX_Y0
                if col > 2:
                    return None
            placements.append(("story", col, y, (st, lines)))
            y += hh
    return placements


# --------------------------------------------------------------------------
# Page rendering
# --------------------------------------------------------------------------


def render(Image, ImageDraw, ImageFont):
    img = Image.new("RGB", (S(W), S(H)), PAPER)
    d = ImageDraw.Draw(img)
    fonts = Fonts(ImageFont)

    # page frame
    rect(d, (7, 7, W - 7, H - 7), outline=RULE, width=S(2.5))
    rect(d, (12.5, 12.5, W - 12.5, H - 12.5), outline=RULE, width=S(0.75))

    # ---------------- masthead ----------------
    tracked(d, (W / 2, 18), "THE WORLD'S NEWS \u00b7 ON ONE PAGE",
            fonts.get("sans_b", 10), TEAL, 2.2, anchor="ma")
    title = "ONE DAY, ONE PLANET"
    tsize = 56
    while tsize > 30 and text_w(d, title, fonts.get("serif_b", tsize)) > 950:
        tsize -= 2
    text(d, (W / 2, 28), title, fonts.get("serif_b", tsize), fill=INK,
         anchor="ma")
    line(d, [(MARGIN, 93), (W - MARGIN, 93)], fill=RULE, width=S(2.5))
    line(d, [(MARGIN, 97.5), (W - MARGIN, 97.5)], fill=RULE, width=S(1))
    text(d, (W / 2, 102), "Friday 20 November 2026",
         fonts.get("serif_b", 25), fill=CRIMSON, anchor="ma")
    tracked(d, (W / 2, 130), "48 STORIES \u00b7 7 REGIONS \u00b7 ONE DAY",
            fonts.get("sans_b", 12), TEAL_DARK, 2.4, anchor="ma")

    # ---------------- markets ticker strip ----------------
    rect(d, (MARGIN, 146, W - MARGIN, 164), fill=PAPER_DARK)
    line(d, [(MARGIN, 146), (W - MARGIN, 146)], fill=RULE, width=S(0.75))
    line(d, [(MARGIN, 164), (W - MARGIN, 164)], fill=RULE, width=S(0.75))
    ticker = [
        ("S&P 500 ", INK), ("\u25bc 2.0%", CRIMSON),
        ("   \u00b7   ", INK_SOFT),
        ("DOW ", INK), ("\u25bc 1,101", CRIMSON),
        (" BELOW 50,000", INK_SOFT),
        ("   \u00b7   ", INK_SOFT),
        ("NIKKEI ", INK), ("\u25bc 4.8%", CRIMSON),
        ("   \u00b7   ", INK_SOFT),
        ("SOFTBANK ", INK), ("\u25bc 16%", CRIMSON),
        ("   \u00b7   ", INK_SOFT),
        ("ANTHROPIC ", INK), ("\u25b2 17%", GREEN),
        (" NASDAQ DEBUT", INK_SOFT),
    ]
    tf = fonts.get("sans_b", 10)
    total = sum(text_w(d, s, tf) for s, _ in ticker)
    tx = (W - total) / 2
    for s, fill in ticker:
        text(d, (tx, 150), s, tf, fill=fill)
        tx += text_w(d, s, tf)

    # ---------------- lead panels ----------------
    leads = [
        ("SHENZHEN \u00b7 SUMMIT", TEAL_DARK, scene_summit,
         "Trump, Xi and Putin hold first three-way summit",
         "Four-point peace declaration signed after ~70 minutes of talks."),
        ("THE HAGUE \u00b7 WORLD COURT", (122, 90, 20), scene_court,
         "ICJ rules Myanmar committed genocide against the Rohingya",
         "First state ever held responsible \u2014 verdict 9\u20136; "
         "1.3m displaced."),
        ("NEW YORK \u00b7 MARKETS", CRIMSON_DARK, scene_markets,
         "Anthropic's record $81.3bn IPO closes +17%",
         "But the Dow falls 1,101 points as an AI sell-off bites."),
    ]
    lead_y, lead_h, panel_w, gap = 170, 160, 316, 12
    for i, (kicker, accent, scene, head, deck) in enumerate(leads):
        px = MARGIN + i * (panel_w + gap)
        rect(d, (px, lead_y, px + panel_w, lead_y + lead_h), fill=CARD,
             outline=INK, width=S(1.2))
        rect(d, (px, lead_y, px + panel_w, lead_y + 19), fill=accent)
        text(d, (px + 9, lead_y + 4), kicker, fonts.get("sans_b", 10.5),
             fill=(250, 248, 240))
        scene(d, px + 1, lead_y + 20, panel_w - 2, 63)
        hy = lead_y + 88
        for ln in wrap(d, head, fonts.get("serif_b", 15.5), panel_w - 18):
            text(d, (px + 9, hy), ln, fonts.get("serif_b", 15.5), fill=INK)
            hy += 18.5
        hy += 2
        for ln in wrap(d, deck, fonts.get("sans", 11), panel_w - 18):
            text(d, (px + 9, hy), ln, fonts.get("sans", 11),
                 fill=INK_SOFT)
            hy += 13.5

    # ---------------- map band ----------------
    text(d, (MARGIN, 339), "THE DAY ON THE MAP", fonts.get("sans_b", 12),
         fill=TEAL_DARK)
    note = "numbered pins mark index stories"
    text(d, (W - MARGIN, 340), note, fonts.get("sans", 10),
         fill=INK_SOFT, anchor="ra")
    map_y0, map_y1 = 356, 448
    rect(d, (MARGIN, map_y0, W - MARGIN, map_y1), fill=(240, 238, 230),
         outline=INK_SOFT, width=S(0.75))
    cell_w = (W - 2 * MARGIN) / MAP_COLS
    cell_h = (map_y1 - map_y0) / MAP_ROWS
    r = min(cell_w, cell_h) * 0.30
    for row, spans in MAP_SPANS.items():
        cy = map_y0 + (row + 0.5) * cell_h
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cx = MARGIN + (c + 0.5) * cell_w
                ellipse(d, (cx - r, cy - r, cx + r, cy + r), fill=MAP_DOT)
    # faint region labels in the ocean space
    lab_f = fonts.get("sans_b", 8.5)
    lab_fill = (164, 174, 168)
    for lx, ly, lab in ((44, 398, "N. AMERICA"), (352, 382, "EUROPE"),
                        (618, 418, "AFRICA"), (636, 440, "ASIA-PACIFIC")):
        tracked(d, (lx, ly), lab, lab_f, lab_fill, 1.6)
    nudges = {3: (-3, -5), 16: (4, 5), 15: (-3, -3), 35: (3, 4),
              8: (-2, -4), 14: (5, 4), 48: (-5, 3), 20: (-4, 5),
              7: (6, -3), 1: (0, -3), 31: (5, -4), 41: (-5, 6),
              47: (7, -7)}
    for num, lon, lat in PINS:
        px = MARGIN + (lon + 180) / 360.0 * (W - 2 * MARGIN)
        py = map_y0 + (80 - lat) / 128.0 * (map_y1 - map_y0)
        dx, dy = nudges.get(num, (0, 0))
        px, py = px + dx, py + dy
        ellipse(d, (px - 6.5, py - 6.5, px + 6.5, py + 6.5),
                fill=CRIMSON, outline=(250, 248, 240), width=S(1.1))
        text(d, (px, py - 3.8), "%d" % num, fonts.get("sans_b", 7.5),
             fill=(250, 248, 240), anchor="ma")

    # ---------------- story index ----------------
    for sep_x in (344, 670):
        line(d, [(sep_x, INDEX_Y0 + 2), (sep_x, INDEX_Y1)],
             fill=(196, 188, 168), width=S(0.75))
    chosen = None
    for size in (12, 11.5, 11, 10.5, 10, 9.5, 9):
        chosen = plan_index(d, fonts, size)
        if chosen is not None:
            break
    if chosen is None:
        raise RuntimeError("index does not fit")
    size = size
    lh = size * 1.21
    for kind, col, y, payload in chosen:
        x0 = COL_X[col]
        if kind == "header":
            if y > INDEX_Y0 + 1:
                line(d, [(x0, y - 3), (x0 + COL_W + 8, y - 3)],
                     fill=(206, 198, 178), width=S(0.75))
            tracked(d, (x0 + 1, y + 1), payload, fonts.get("sans_b", 11),
                    TEAL_DARK, 1.1)
            line(d, [(x0, y + 16.5), (x0 + COL_W + 8, y + 16.5)],
                 fill=TEAL, width=S(1.4))
        else:
            st, lines = payload
            _, space_w = rich_lines(
                d, story_segments(fonts, size, st[0], st[1], st[2]),
                COL_W, fonts.get("sans", size))
            ly = y
            for ln in lines:
                x = x0 + 1
                for w_, fnt, fill, ww in ln:
                    d.text((S(x), S(ly)), w_, font=fnt, fill=fill,
                           anchor="la")
                    x += ww + space_w
                ly += lh

    # ---------------- the day in numbers ----------------
    line(d, [(MARGIN, 953), (W - MARGIN, 953)], fill=RULE, width=S(2))
    tracked(d, (W / 2, 957), "THE DAY IN NUMBERS",
            fonts.get("sans_b", 10.5), CRIMSON, 2.2, anchor="ma")
    cell_w_n = (W - 2 * MARGIN) / len(NUMBERS)
    for i, (value, label) in enumerate(NUMBERS):
        cx = MARGIN + (i + 0.5) * cell_w_n
        if i:
            line(d, [(MARGIN + i * cell_w_n, 973),
                     (MARGIN + i * cell_w_n, 1005)],
                 fill=(196, 188, 168), width=S(0.75))
        text(d, (cx, 971), value, fonts.get("sans_b", 14.5), fill=INK,
             anchor="ma")
        ly = 989
        for ln in wrap(d, label, fonts.get("sans", 7.5), cell_w_n - 8):
            text(d, (cx, ly), ln, fonts.get("sans", 7.5), fill=INK_SOFT,
                 anchor="ma")
            ly += 9

    return img.resize((S(W) // SS, S(H) // SS), Image.LANCZOS)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = render(Image, ImageDraw, ImageFont)
        img.save(dest, format="PNG")
    except Exception:
        here = os.path.dirname(os.path.abspath(__file__))
        shutil.copyfile(os.path.join(here, "entry.png"), dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
