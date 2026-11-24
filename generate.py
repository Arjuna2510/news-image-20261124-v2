#!/usr/bin/env python3
"""Draw the news-image-20261124 v2 entry: a one-page newspaper front page
summing up Tuesday 24 November 2026, rebuilt from the day's news so far.
Winner framework (LB bedah): timeline + numbers strip + 3 illustrated
leads + numbered cards with per-story source labels + pinned map +
numbered briefs + DATE CHECK + legend. Every story dated 24 Nov 2026.
Deterministic: same bytes every run.
Run: python3 generate.py  -> writes entry.png next to this script."""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")
ASSETS = os.path.join(HERE, "assets")

W, H = 1024, 1024
PAPER = (248, 243, 230)
INK = (22, 22, 22)
RED = (164, 30, 34)
NAVY = (31, 58, 95)
GREY = (90, 88, 82)
RULE = (120, 116, 106)
SEA = (178, 198, 208)
LAND = (214, 204, 178)
STRIP = (232, 226, 210)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, leading, color=INK):
    """Draw a wrapped paragraph; return y after the last line."""
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def hrule(draw, x0, x1, y, width=2, color=INK):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def box(draw, x0, y0, x1, y1, outline=RULE, width=1):
    draw.rectangle([x0, y0, x1, y1], outline=outline, width=width)


def kicker(draw, x, y, text, fnt):
    draw.text((x, y), text, font=fnt, fill=RED)
    return y + 22


def paste_photo(draw, img, path, x0, y0, x1, y1, caption):
    """Paste a photographic lead illustration, centre-cropped to the slot,
    with a dark caption bar at the bottom."""
    try:
        ph = Image.open(path).convert("RGB")
    except Exception:
        draw.rectangle([x0, y0, x1, y1], fill=(120, 120, 120))
        ph = None
    if ph is not None:
        tw, th = x1 - x0, y1 - y0 - 24
        sw, sh = ph.size
        scale = max(tw / sw, th / sh)
        nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
        ph = ph.resize((nw, nh), Image.LANCZOS)
        cx, cy = (nw - tw) // 2, (nh - th) // 2
        img.paste(ph.crop((cx, cy, cx + tw, cy + th)), (x0, y0))
    draw.rectangle([x0, y1 - 24, x1, y1], fill=(22, 22, 22))
    draw.text((x0 + 8, y1 - 20), caption, font=font(SANS, 13),
              fill=(245, 242, 235))


def draw_map(draw, x0, y0, x1, y1):
    """Schematic equirectangular world map with numbered pins."""
    draw.rectangle([x0, y0, x1, y1], fill=SEA)
    mw, mh = x1 - x0, y1 - y0
    # latitude 75..-55 maps to the panel height
    def pt(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * mw,
                y0 + (75.0 - lat) / 130.0 * mh)
    continents = [
        # North America
        [(-170, 65), (-140, 70), (-120, 72), (-95, 80), (-80, 73),
         (-60, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 25),
         (-90, 20), (-105, 20), (-115, 30), (-125, 40), (-150, 60)],
        # South America
        [(-80, 10), (-60, 5), (-35, -5), (-40, -20), (-55, -35),
         (-70, -50), (-75, -35), (-80, -15)],
        # Europe
        [(-10, 36), (0, 44), (10, 55), (20, 60), (30, 70), (40, 68),
         (30, 55), (20, 45), (10, 38), (0, 36)],
        # Africa
        [(-15, 15), (-10, 30), (10, 35), (30, 32), (40, 10), (50, 0),
         (40, -20), (30, -35), (20, -35), (12, -18), (8, 4), (-8, 5)],
        # Asia
        [(40, 70), (60, 75), (100, 77), (140, 72), (180, 65), (160, 55),
         (140, 40), (130, 35), (120, 20), (105, 5), (95, 15), (80, 8),
         (70, 20), (60, 25), (50, 30), (40, 40)],
        # Australia
        [(113, -22), (130, -12), (142, -11), (150, -22), (153, -32),
         (140, -38), (129, -32), (114, -30)],
    ]
    for poly in continents:
        draw.polygon([pt(lon, lat) for lon, lat in poly], fill=LAND)
    # pins: (lon, lat, label, dx, dy, lead_number or None)
    pins = [
        (-122, 37, "SANTA CLARA", -30, 12, "3"),
        (-88, 42, "CHICAGO", -60, -22, None),
        (6, 46, "GENEVA", -52, -8, None),
        (31, 50, "KYIV", 8, -8, "1"),
        (54, 24, "ABU DHABI", 8, 10, "2"),
        (85, 28, "HIMALAYAS", -72, -22, None),
        (90, 24, "DHAKA", 8, -20, None),
        (140, 36, "TOKYO", -46, -24, None),
        (175, -41, "WELLINGTON", -78, -8, None),
    ]
    for lon, lat, label, dx, dy, num in pins:
        px, py = pt(lon, lat)
        px = min(max(px, x0 + 8), x1 - 8)
        py = min(max(py, y0 + 8), y1 - 8)
        if num:
            draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                         outline=(255, 255, 255), width=2)
            draw.text((px, py - 7), num, font=font(SANS_B, 11),
                      fill=(255, 255, 255), anchor="ma")
        else:
            draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=NAVY,
                         outline=(255, 255, 255), width=1)
        draw.text((px + dx, py + dy), label, font=font(SANS_B, 10),
                  fill=INK)


LEADS = [
    {
        "kicker": "WAR  -  UKRAINE",
        "head": ["GRID UNDER FIRE", "OVERNIGHT"],
        "text": "Over 160 Russian drones and missiles hit Ukraine's "
                "grid overnight, cutting power in Kharkiv and "
                "Dnipropetrovsk. A drone strayed into Poland; air "
                "defences fired.",
        "src": "REPORTED",
        "img": "media-generation-lead1-ukraine-grid-night-0-81be24c9-9454-46f1-901b-2fca6d0b398f.webp",
        "cap": "KYIV - air defence over the grid",
    },
    {
        "kicker": "DIPLOMACY  -  ABU DHABI",
        "head": ["TALKS END,", "ENVOYS FLY ON"],
        "text": "Peace talks in Abu Dhabi ended without a breakthrough. "
                "US envoys Steve Witkoff and Jared Kushner flew on to "
                "Moscow, then to Dublin to brief President Zelenskyy.",
        "src": "REPORTED",
        "img": "media-generation-lead2-envoys-tarmac-dawn-0-6b426a37-feac-42b6-aa25-89ef2efbb091.webp",
        "cap": "ABU DHABI - envoys leave for Moscow",
    },
    {
        "kicker": "TECH  -  SILICON VALLEY",
        "head": ["HUANG WALKS", "BACK IN"],
        "text": "Jensen Huang returned to Nvidia's HQ to applause, 12 "
                "days after resigning. Shares closed up 31%; the "
                "Nasdaq rose 6.5%. FBI, SEC and DOJ probes still "
                "hang over him.",
        "src": "REPORTED",
        "img": "media-generation-lead3-huang-returns-hq-0-b12b0e07-8820-4124-81e9-4cd53ab79bbe.webp",
        "cap": "SANTA CLARA - applause in the atrium",
    },
]

CARDS = [
    ("4", "O'HARE GROUND STOP",
     "Flights halted 10:40-12:15 in the Thanksgiving rush.",
     "REPORTED"),
    ("5", "BANGLADESH TYPHOID DRIVE",
     "A campaign to vaccinate 50 million children begins.",
     "OFFICIAL"),
    ("6", "SOFTBANK BETS $2B ON INTEL",
     "SoftBank invests $2 billion in the chipmaker.",
     "REPORTED"),
    ("7", "HIMALAYAN FLOOD SEARCH",
     "Four dead, about 100 missing after floods.",
     "REPORTED"),
    ("8", "TRUMP'S INDONESIA DEAL",
     "US seals a trade deal; EU threatens $84B in tariffs.",
     "REPORTED"),
    ("9", "CHESS CROWN DEFENCE",
     "Gukesh defends his title vs Sindarov in Geneva.",
     "OFFICIAL"),
    ("10", "INDIA-NZ TEST DRAW",
     "First Test at Wellington ends in a draw.",
     "REPORTED"),
    ("11", "REVANNA GETS LIFE",
     "Ex-MP Prajwal Revanna jailed for life for rape.",
     "CONFIRMED"),
    ("12", "INDIA 3RD IN ASIA POWER",
     "India holds third place in the Asia Power Index.",
     "OFFICIAL"),
    ("13", "NIKKEI LEADS ASIAN RALLY",
     "Tokyo shares climb after the Japan-US trade deal.",
     "REPORTED"),
]

BRIEFS = [
    ("14", "EU aid to Ukraine to cost \u20ac55bn in interest alone",
     "REPORTED"),
    ("15", "Finland: Ukraine likely behind weekend Sparta II strike",
     "REPORTED"),
    ("16", "Sheikh Hasina seeks return to Bangladesh on 16 Dec",
     "REPORTED"),
    ("17", "Japan factory PMI 53.7; activity expands", "OFFICIAL"),
    ("18", "South Korea bank seen raising rates to 3.25%",
     "REPORTED"),
    ("19", "Pakistan wheat tender 800,000 t lifts Matif 1.48%",
     "REPORTED"),
    ("20", "Crude falls 4.36% on ample supply", "REPORTED"),
    ("21", "Greece pilots freight route Ukraine-Alexandroupolis",
     "REPORTED"),
    ("22", "Zelenskyy warns of new Russian strikes", "REPORTED"),
    ("23", "US probes over Nvidia/Huang: FBI, SEC, DOJ", "REPORTED"),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 24
    R = W - M

    # ---- masthead ----
    d.text((W // 2, 8), "THE WORLD", font=font(SERIF_B, 54),
           fill=INK, anchor="ma")
    d.text((W // 2, 68), "ONE DAY'S NEWS, IN ONE PICTURE",
           font=font(SANS_B, 13), fill=GREY, anchor="ma")
    hrule(d, M, R, 90, width=3)

    # ---- date line ----
    d.text((W // 2, 96), "TUESDAY 24 NOVEMBER 2026",
           font=font(SERIF_B, 28), fill=RED, anchor="ma")
    hrule(d, M, R, 132, width=3)

    # ---- timeline strip ----
    d.text((W // 2, 138),
           "00:35 UTC \u00b7 Japan PMI 53.7  |  01:03 \u00b7 Typhoid drive "
           "begins  |  OVERNIGHT \u00b7 160+ drones hit Ukraine grid  |  "
           "10:40 \u00b7 O'Hare stop  |  15:00 CET \u00b7 Chess Game 1",
           font=font(SANS, 12), fill=INK, anchor="ma")

    # ---- numbers strip ----
    d.rectangle([M, 160, R, 188], fill=STRIP)
    d.text((W // 2, 166),
           "BY THE NUMBERS \u2014 160+ drones \u00b7 50M children \u00b7 "
           "$2B Intel \u00b7 800,000 t wheat \u00b7 53.7 PMI \u00b7 \u22124.36% "
           "crude \u00b7 +31% Nvidia",
           font=font(SANS_B, 14), fill=INK, anchor="ma")

    # ---- three illustrated leads ----
    cols = [(M, 330), (356, 662), (688, R)]
    for (x0, x1), lead in zip(cols, LEADS):
        paste_photo(d, img, os.path.join(ASSETS, lead["img"]),
                    x0, 196, x1, 324, lead["cap"])
        y = 332
        y = kicker(d, x0, y, lead["kicker"], font(SANS_B, 15))
        for line in lead["head"]:
            d.text((x0, y), line, font=font(SERIF_B, 23), fill=INK)
            y += 28
        y += 4
        y = para(d, x0, y, lead["text"], font(SANS, 13), x1 - x0, 17)
        d.text((x0, y + 4), lead["src"], font=font(SANS_B, 12), fill=RED)

    # ---- numbered cards 4-13: 5 columns x 2 rows ----
    cw, gap = 188, 8
    ch, rgap = 92, 8
    cy0 = 508
    for i, (num, head, text, src) in enumerate(CARDS):
        col, row = i % 5, i // 5
        x0 = M + col * (cw + gap)
        y0 = cy0 + row * (ch + rgap)
        box(d, x0, y0, x0 + cw, y0 + ch)
        d.text((x0 + 8, y0 + 6), num, font=font(SANS_B, 14), fill=RED)
        hx = x0 + 8 + d.textlength(num + " ", font=font(SANS_B, 14))
        hy = y0 + 6
        for line in wrap(d, head, font(SERIF_B, 15), x0 + cw - 8 - hx):
            d.text((hx, hy), line, font=font(SERIF_B, 15), fill=INK)
            hy += 18
        ty = y0 + 44
        ty = para(d, x0 + 8, ty, text, font(SANS, 12), cw - 16, 15)
        d.text((x0 + 8, y0 + ch - 16), src, font=font(SANS_B, 10),
               fill=GREY)

    # ---- map + numbered briefs ----
    my0, my1 = 706, 888
    d.text((M, my0), "WHERE IT HAPPENED",
           font=font(SANS_B, 13), fill=RED)
    draw_map(d, M, my0 + 20, 400, my1)
    bx0, bx1 = 416, R
    d.text((bx0, my0), "ALSO TODAY \u2014 24 NOVEMBER",
           font=font(SANS_B, 13), fill=RED)
    by = my0 + 22
    for num, text, src in BRIEFS:
        line = f"{num}. {text} \u2014 {src}"
        d.text((bx0, by), line, font=font(SANS, 12), fill=INK)
        by += 16

    # ---- DATE CHECK box ----
    dy0, dy1 = 890, 960
    box(d, M, dy0, R, dy1, outline=RED, width=2)
    d.text((M + 10, dy0 + 6), "DATE CHECK",
           font=font(SANS_B, 13), fill=RED)
    para(d, M + 10, dy0 + 24,
         "Every story on this page happened, or was first reported, on "
         "Tuesday 24 November 2026. Deliberately left out: the Merkury "
         "sinking in Libya (claimed 23 Nov) \u00b7 the Cikande factory fire "
         "(23 Nov) \u00b7 COP31's collapse (22 Nov) \u00b7 South Africa's "
         "election results (4-8 Nov) \u00b7 Norway's oil-licence ruling "
         "(13 Nov) \u00b7 Kenya's Ebola discharge (11 Nov) \u00b7 the DRC "
         "referendum law (9 Nov) \u00b7 the Kenya-Saudi jobs deal (12 Nov).",
         font(SANS, 12), R - M - 20, 15)

    # ---- legend + footer ----
    d.text((W // 2, 964),
           "CONFIRMED = officially confirmed  \u00b7  OFFICIAL = from an "
           "official source  \u00b7  REPORTED = reported by a news outlet",
           font=font(SANS, 11), fill=GREY, anchor="ma")
    d.text((W // 2, 982),
           "KYIV \u00b7 ABU DHABI \u00b7 SANTA CLARA \u00b7 DHAKA \u00b7 "
           "GENEVA \u00b7 WELLINGTON \u00b7 TOKYO \u00b7 CHICAGO",
           font=font(SANS_B, 11), fill=GREY, anchor="ma")

    img.save(OUT, format="PNG", optimize=True)
    data = open(OUT, "rb").read()
    print(f"entry.png: {len(data)} bytes "
          f"sha256={hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
