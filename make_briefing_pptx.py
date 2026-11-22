#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_briefing_pptx.py - genera il briefing di 6 slide (una per punto del piano)
per la presentazione Electrade del 23/11/2026.

    python "presentazione lunedì 23/make_briefing_pptx.py"

Output: "presentazione lunedì 23/Presentazione_Electrade_6_punti.pptx"

Ogni slide contiene:
  - la domanda a cui il punto risponde
  - tabella a due colonne: DATO NECESSARIO | DOVE LO PRENDO
  - lo schema (mock) del grafico che verra' mostrato a schermo
  - cosa mostro a schermo / da validare con l'esperto / tempo stimato

Le slide sono concettuali: nessuna data, nessun prezzo, nessuna zona gia' scelta.
Base di lavoro: prezzi orari (PT60).
I testi stanno in SLIDES: si modificano li', senza toccare il layout.
"""
import math
import os
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "Presentazione_Electrade_6_punti.pptx")

# ---------------------------------------------------------------- design tokens
INK = RGBColor(0x1A, 0x1A, 0x1A)
GREY = RGBColor(0x55, 0x55, 0x55)
RULE = RGBColor(0xC8, 0xC8, 0xC8)
LIGHT = RGBColor(0xF2, 0xF2, 0xF2)
PAPER = RGBColor(0xFA, 0xFA, 0xFA)
ACCENT = RGBColor(0x1F, 0x4E, 0x79)
RED = RGBColor(0xC0, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# colori delle sette zone di mercato (etichette generiche nei mock)
ZONE = {
    "1": RGBColor(0x1F, 0x4E, 0x79),
    "2": RGBColor(0x2E, 0x75, 0xB6),
    "3": RGBColor(0x70, 0xAD, 0x47),
    "4": RGBColor(0xED, 0x7D, 0x31),
    "5": RGBColor(0xFF, 0xC0, 0x00),
    "6": RGBColor(0x70, 0x30, 0xA0),
    "7": RGBColor(0x00, 0xB0, 0xB0),
}

FONT = "Calibri"
MONO = "Consolas"

W, H = 13.333, 7.5
M = 0.45
COL_L_X, COL_L_W = 0.45, 6.30
COL_R_X, COL_R_W = 6.95, 5.95
C1_W = 3.55                      # larghezza colonna "dato necessario"

FOOT = ("Analisi prezzo zero - per Electrade S.p.A.  |  Davide Cacciari  |  18/11/2026  |  "
        "piano: ROADMAP.md")

# Metodo di default: API GME (due righe sopra la tabella, su ogni slide)
API_METHOD = "METODO \u00b7 GME API \u2014 api.mercatoelettrico.org/request"
API_METHOD_2 = "/api/v1/Auth + /api/v1/RequestData \u00b7 parametri DataName e Segment"


# ---------------------------------------------------------------- helpers
def tb(slide, x, y, w, h, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    tf.paragraphs[0].alignment = align
    return tf


def para(tf, text, size=9.5, bold=False, color=INK, first=False, space_after=2,
         font=FONT, italic=False, space_before=0, align=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    if align is not None:
        p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.name = font
    r.font.color.rgb = color
    return p


def bullets(tf, items, size=8.8, color=INK, first=True, space_after=3, marker="\u2013 "):
    for i, it in enumerate(items):
        para(tf, marker + it, size=size, color=color, first=(first and i == 0),
             space_after=space_after)


def soft_url(u):
    """Spazi sottili per far andare a capo gli URL su / ? & =."""
    out = []
    for ch in u:
        out.append(ch)
        if ch in "/?&=":
            out.append("\u200b")
    return "".join(out)


def nlines(text, per_line):
    return max(1, int(len(text) / per_line) + (1 if len(text) % per_line else 0))


def rect(slide, x, y, w, h, fill=None, line=None, line_w=0.75):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                                Inches(w), Inches(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    sh.shadow.inherit = False
    sh.text_frame.text = ""
    return sh


def label(slide, x, y, w, text, color=ACCENT, size=9):
    tf = tb(slide, x, y, w, 0.22)
    para(tf, text.upper(), size=size, bold=True, color=color, first=True, space_after=0)


def poly(slide, pts, color=INK, width=1.25, dash=None, close=False):
    """pts = [(x_in, y_in), ...] in inches."""
    if len(pts) < 2:
        return None
    x0, y0 = pts[0]
    builder = slide.shapes.build_freeform(Emu(int(x0 * 914400)), Emu(int(y0 * 914400)))
    builder.add_line_segments(
        [(Emu(int(x * 914400)), Emu(int(y * 914400))) for x, y in pts[1:]],
        close=close,
    )
    sh = builder.convert_to_shape()
    if close:
        sh.fill.solid()
        sh.fill.fore_color.rgb = color
    else:
        sh.fill.background()
    sh.line.color.rgb = color
    sh.line.width = Pt(width)
    if dash:
        sh.line.dash_style = dash
    sh.shadow.inherit = False
    return sh


def axes(slide, x, y, w, h, xlab="", ylab="", zero=None):
    """Cornice + assi di un mock. zero = quota (0..1) della linea zero."""
    rect(slide, x, y, w, h, fill=PAPER, line=RULE)
    rect(slide, x, y + h - 0.012, w, 0.012, fill=RULE)
    rect(slide, x, y, 0.012, h, fill=RULE)
    if zero is not None:
        zy = y + h * zero
        rect(slide, x, zy, w, 0.008, fill=RGBColor(0xE0, 0xE0, 0xE0))
    if xlab:
        tf = tb(slide, x, y + h + 0.02, w, 0.2, align=PP_ALIGN.CENTER)
        para(tf, xlab, size=7.5, color=GREY, first=True, space_after=0)
    if ylab:
        tf = tb(slide, x - 0.02, y - 0.22, 4.0, 0.2)
        para(tf, ylab, size=7.5, color=GREY, first=True, space_after=0)


def legend(slide, x, y, items, size=7.5, gap=1.12):
    """items = [(label, color)]"""
    for i, (lab, col) in enumerate(items):
        rect(slide, x + i * gap, y + 0.045, 0.13, 0.065, fill=col)
        tf = tb(slide, x + i * gap + 0.17, y, gap - 0.18, 0.2)
        para(tf, lab, size=size, color=GREY, first=True, space_after=0)


# ---------------------------------------------------------------- tabella
def draw_table(slide, x, y, w, rows, c1=C1_W, fs=8.8, lh=0.145):
    """Tabella a due colonne: (dato necessario | dove lo prendo)."""
    c2 = w - c1
    gap = 0.14
    label(slide, x, y, c1, "Dato necessario")
    label(slide, x + c1 + gap, y, c2, "Dove lo prendo")
    y += 0.21
    rect(slide, x, y, w, 0.012, fill=INK)
    y += 0.07
    cpl1 = max(10, int(c1 * 144 / fs))
    cpl2 = max(10, int((c2 - gap) * 144 / fs))
    for d, s in rows:
        h = max(nlines(d, cpl1), nlines(s, cpl2)) * lh + 0.06
        tf = tb(slide, x, y, c1 - gap, h, anchor=MSO_ANCHOR.MIDDLE)
        para(tf, d, size=fs, color=INK, first=True, space_after=0)
        tf = tb(slide, x + c1 + gap, y, c2 - gap, h, anchor=MSO_ANCHOR.MIDDLE)
        para(tf, s, size=fs, color=ACCENT, first=True, space_after=0)
        y += h
        rect(slide, x, y - 0.03, w, 0.006, fill=RULE)
    return y


# ---------------------------------------------------------------- slide chrome
def chrome(slide, s, n_total):
    rect(slide, 0, 0, W, 0.06, fill=ACCENT)
    tf = tb(slide, M, 0.26, 12.45, 0.5)
    para(tf, s["title"], size=21, bold=True, color=INK, first=True, space_after=0)
    tf = tb(slide, M, 0.82, 12.45, 0.3)
    para(tf, s["question"], size=11.5, color=ACCENT, first=True, space_after=0)
    rect(slide, M, 1.2, 12.45, 0.012, fill=RULE)

    # colonna sinistra: metodo + tabella a due colonne + output
    tf = tb(slide, COL_L_X, 1.30, COL_L_W, 0.2)
    para(tf, API_METHOD, size=8.5, color=ACCENT, font=MONO, first=True, space_after=0)
    tf = tb(slide, COL_L_X, 1.48, COL_L_W, 0.2)
    para(tf, API_METHOD_2, size=8, color=GREY, font=MONO, first=True, space_after=0)
    draw_table(slide, COL_L_X, 1.76, COL_L_W, s["table"])

    label(slide, COL_L_X, 3.75, COL_L_W, "Cosa mostro a schermo")
    tf = tb(slide, COL_L_X, 4.00, COL_L_W, 1.8)
    bullets(tf, s["output"], size=8.8, space_after=4)

    # colonna destra: mock
    mx, my, mw, mh = COL_R_X, 1.30, COL_R_W, 4.90
    rect(slide, mx, my, mw, mh, fill=PAPER, line=RULE)
    s["mock"](slide, mx, my, mw, mh)
    tf = tb(slide, mx, my + mh + 0.06, mw, 0.4)
    para(tf, s["mock_caption"], size=8, color=GREY, italic=True, first=True, space_after=0)

    # fascia "da validare"
    rect(slide, M, 6.86, 12.45, 0.44, fill=LIGHT)
    tf = tb(slide, M + 0.12, 6.93, 9.9, 0.32, anchor=MSO_ANCHOR.MIDDLE)
    para(tf, "Domanda per Federico  \u2013  " + s["doubt"], size=9,
         color=INK, first=True, space_after=0)
    tf = tb(slide, M + 10.1, 6.93, 2.2, 0.32, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    para(tf, "TEMPO STIMATO  " + s["time"], size=9, bold=True, color=ACCENT,
         first=True, space_after=0)

    tf = tb(slide, M, 7.34, 12.45, 0.2)
    para(tf, FOOT + "   |   slide %d/%d" % (s["num"], n_total), size=7.5,
         color=GREY, first=True, space_after=0)


# ---------------------------------------------------------------- mocks
def mock_prices(slide, x, y, w, h):
    px, py, pw, ph = x + 0.42, y + 0.28, w - 0.68, h - 0.68
    axes(slide, px, py, pw, ph, xlab="periodo analizzato", ylab="EUR/MWh", zero=0.78)
    pts = []
    for i in range(13):
        v = 0.55 + 0.22 * ((i % 4) - 1.5) / 1.5 + 0.06 * i
        pts.append((px + pw * i / 12.0, py + ph * (1 - min(max(v, 0.05), 0.95))))
    poly(slide, pts, INK, 2.0)
    for k, (name, col) in enumerate(ZONE.items()):
        pts = []
        for i in range(13):
            amp = 0.06 + 0.035 * k
            v = 0.62 + amp * ((i % 5) - 2) / 2 + 0.035 * i - 0.05 * k
            pts.append((px + pw * i / 12.0, py + ph * (1 - min(max(v, 0.08), 0.95))))
        poly(slide, pts, col, 1.1)
    tf = tb(slide, px - 0.42, py + ph * 0.74, 0.38, 0.2, align=PP_ALIGN.RIGHT)
    para(tf, "0", size=7.5, color=GREY, first=True, space_after=0)
    legend(slide, px, y + h - 0.24, [("indice nazionale", INK), ("zona 1", ZONE["1"]),
                                      ("zona 4", ZONE["4"]), ("zona 6", ZONE["6"]),
                                      ("zona 7", ZONE["7"])], gap=1.02)


def mock_event(slide, x, y, w, h):
    px, py, pw, ph = x + 0.45, y + 0.30, w - 0.75, h - 0.80
    axes(slide, px, py, pw, ph, xlab="quantita' (MWh)", ylab="EUR/MWh", zero=0.86)
    yz = py + ph * 0.86
    off = [(px + pw * 0.04, yz), (px + pw * 0.58, yz),
           (px + pw * 0.58, py + ph * 0.55), (px + pw * 0.70, py + ph * 0.55),
           (px + pw * 0.70, py + ph * 0.32), (px + pw * 0.82, py + ph * 0.32),
           (px + pw * 0.82, py + ph * 0.17), (px + pw * 0.95, py + ph * 0.17)]
    poly(slide, off, GREY, 1.6)
    dem = [(px + pw * 0.04, py + ph * 0.12), (px + pw * 0.26, py + ph * 0.12),
           (px + pw * 0.26, py + ph * 0.38), (px + pw * 0.34, py + ph * 0.38),
           (px + pw * 0.34, py + ph * 0.62), (px + pw * 0.44, py + ph * 0.62),
           (px + pw * 0.44, yz), (px + pw * 0.56, yz), (px + pw * 0.56, py + ph * 0.97)]
    poly(slide, dem, ZONE["2"], 1.6)
    ix = px + pw * 0.44
    rect(slide, ix - 0.004, yz, 0.008, py + ph - yz, fill=RGBColor(0xCC, 0xCC, 0xCC))
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(ix - 0.055), Inches(yz - 0.055),
                                 Inches(0.11), Inches(0.11))
    dot.fill.solid()
    dot.fill.fore_color.rgb = RED
    dot.line.fill.background()
    dot.shadow.inherit = False
    tf = tb(slide, ix - 1.05, yz + 0.04, 2.1, 0.3, align=PP_ALIGN.CENTER)
    para(tf, "Pz = 0 EUR/MWh (tratto piatto)", size=7.5, bold=True, color=RED,
         first=True, space_after=0)
    legend(slide, px, y + h - 0.22, [("domanda", ZONE["2"]),
                                      ("offerta", GREY), ("Pz", RED)], gap=1.15)


def mock_time(slide, x, y, w, h):
    cols, rows = 6, 3
    gx, gy = x + 0.38, y + 0.26
    gw, gh = w - 0.62, h - 0.62
    cw, ch = gw / cols, gh / rows
    for r in range(rows):
        for c in range(cols):
            bx, by = gx + c * cw + 0.03, gy + r * ch + 0.03
            bw, bh = cw - 0.07, ch - 0.09
            rect(slide, bx, by, bw, bh, fill=WHITE, line=RULE, line_w=0.5)
            f = (r * cols + c) / float(cols * rows - 1)
            flat = by + bh * 0.72
            poly(slide, [(bx + 0.05, flat), (bx + bw * 0.55, flat),
                         (bx + bw * 0.55, by + bh * 0.35),
                         (bx + bw - 0.05, by + bh * 0.35)], GREY, 0.8)
            dy = by + bh * (0.9 - 0.45 * f)
            poly(slide, [(bx + 0.05, by + bh * 0.15), (bx + bw * 0.45, by + bh * 0.15),
                         (bx + bw * 0.45, dy), (bx + bw - 0.05, dy)],
                 ZONE["2"], 0.8)
            if f > 0.55:
                rect(slide, bx + 0.05, flat, bw - 0.1, 0.005, fill=RED)
    tf = tb(slide, gx, gy + gh + 0.01, gw, 0.2, align=PP_ALIGN.CENTER)
    para(tf, "ore della finestra  \u2192  (sinistra = inizio, destra = fine)",
         size=7.5, color=GREY, first=True, space_after=0)


SOLAR = RGBColor(0xFF, 0xC9, 0x4D)
WIND = RGBColor(0x66, 0xBB, 0x6A)
REST = RGBColor(0x8F, 0xAA, 0xDC)
LOAD = RGBColor(0x1A, 0x1A, 0x1A)


def mock_zones_48h(slide, x, y, w, h):
    """7 pannelli (uno per zona): generazione impilata per fonte + carico, su 48 ore."""
    cols, rows = 4, 2
    gx, gy = x + 0.26, y + 0.20
    gw, gh = w - 0.40, h - 0.46
    cw, ch = gw / cols, gh / rows
    n = 24                                   # punti (ogni 2 ore su 48 h)
    surplus_zone = 3                          # zona con generazione > carico

    # profili normalizzati per le 7 zone
    def prof(i, kind, zone):
        h24 = i % 24
        if kind == "solare":
            v = max(0.0, math.sin(math.pi * (h24 - 6) / 12.0)) if 6 <= h24 <= 18 else 0.0
            v *= 0.9 + 0.25 * math.sin(zone * 1.7 + 1.0)
        elif kind == "eolico":
            v = 0.16 + 0.10 * math.sin(h24 * 0.7 + zone) + 0.07 * math.sin(h24 * 1.9 + zone * 2)
        elif kind == "resto":
            v = 0.40 + 0.08 * math.sin(h24 * 0.25 + zone * 0.5) + 0.05 * math.sin(h24 * 0.9)
        else:  # carico
            v = 0.52 + 0.22 * math.exp(-((h24 - 19) ** 2) / 12.0) \
                + 0.14 * math.exp(-((h24 - 8) ** 2) / 10.0) \
                + 0.05 * math.sin(h24 * 0.6 + zone)
        return max(0.03, v)

    series = []
    for z in range(7):
        sol, eol, rest, load = [], [], [], []
        for i in range(n):
            zone = z + 1
            s = prof(i, "solare", zone)
            e = prof(i, "eolico", zone)
            r = prof(i, "resto", zone)
            l = prof(i, "load", zone)
            if z == surplus_zone:
                s *= 1.35
                e *= 1.20
                l *= 0.85
            elif z == 4:
                l *= 1.10
            sol.append(s)
            eol.append(e)
            rest.append(r)
            load.append(l)
        series.append((sol, eol, rest, load))

    # scala comune a tutte le zone
    peak = 0.0
    for sol, eol, rest, load in series:
        for i in range(n):
            peak = max(peak, sol[i] + eol[i] + rest[i], load[i])

    for z in range(7):
        c, r = z % cols, z // cols
        bx, by = gx + c * cw + 0.05, gy + r * ch + 0.05
        bw, bh = cw - 0.12, ch - 0.30
        rect(slide, bx, by, bw, bh, fill=WHITE, line=RULE, line_w=0.5)
        base = by + bh
        sc = bh * 0.92 / peak
        xs = [bx + 0.04 + (bw - 0.08) * i / float(n - 1) for i in range(n)]
        sol, eol, rest, load = series[z]
        y_rest = [base - rest[i] * sc for i in range(n)]
        y_eol = [base - (rest[i] + eol[i]) * sc for i in range(n)]
        y_sol = [base - (rest[i] + eol[i] + sol[i]) * sc for i in range(n)]
        y_load = [base - load[i] * sc for i in range(n)]
        poly(slide, list(zip(xs, [base] * n)) + list(reversed(list(zip(xs, y_rest)))),
             REST, 0.4, close=True)
        poly(slide, list(zip(xs, y_rest)) + list(reversed(list(zip(xs, y_eol)))),
             WIND, 0.4, close=True)
        poly(slide, list(zip(xs, y_eol)) + list(reversed(list(zip(xs, y_sol)))),
             SOLAR, 0.4, close=True)
        poly(slide, list(zip(xs, y_load)), LOAD, 1.2)
        tf = tb(slide, bx, by + bh + 0.02, bw, 0.18, align=PP_ALIGN.CENTER)
        para(tf, "zona %d" % (z + 1), size=7, bold=True, color=GREY, first=True,
             space_after=0)
    # legenda
    legend(slide, gx, y + h - 0.20, [("solare", SOLAR), ("eolico", WIND),
                                      ("resto (idro, gas, altro)", REST),
                                      ("carico", LOAD)], gap=1.28)


def mock_map(slide, x, y, w, h):
    px, py = x + 0.35, y + 0.22
    pw, ph = w - 0.60, h - 0.72
    boxes = {
        "1": (0.28, 0.02, 0.34, 0.13),
        "2": (0.22, 0.19, 0.36, 0.13),
        "3": (0.25, 0.36, 0.30, 0.13),
        "4": (0.25, 0.53, 0.30, 0.13),
        "5": (0.44, 0.66, 0.24, 0.11),
        "6": (0.60, 0.76, 0.26, 0.11),
        "7": (0.03, 0.40, 0.14, 0.16),
    }
    pos = {}
    for name, (fx, fy, fw, fh) in boxes.items():
        pos[name] = (px + pw * fx, py + ph * fy, pw * fw, ph * fh)

    def edge(a, side_a, b, side_b):
        ax, ay, aw, ah = pos[a]
        bx, by, bw, bh = pos[b]
        p1 = {"l": (ax, ay + ah / 2), "r": (ax + aw, ay + ah / 2),
              "t": (ax + aw / 2, ay), "b": (ax + aw / 2, ay + ah)}[side_a]
        p2 = {"l": (bx, by + bh / 2), "r": (bx + bw, by + bh / 2),
              "t": (bx + bw / 2, by), "b": (bx + bw / 2, by + bh)}[side_b]
        return p1, p2

    for a, sa, b, sb, wd in [("1", "b", "2", "t", 2.2), ("2", "b", "3", "t", 2.2),
                             ("4", "b", "5", "t", 1.3), ("5", "r", "6", "l", 1.3),
                             ("7", "t", "2", "l", 1.0), ("7", "r", "4", "l", 1.0)]:
        p1, p2 = edge(a, sa, b, sb)
        poly(slide, [p1, p2], GREY, wd)
    for fx, fy, tx, ty in [(0.72, 0.03, 0.70, 0.10), (0.27, 0.00, 0.33, 0.03),
                           (0.40, 0.00, 0.46, 0.04), (0.16, 0.25, 0.21, 0.25),
                           (0.74, 0.63, 0.72, 0.60)]:
        poly(slide, [(px + pw * fx, py + ph * fy), (px + pw * tx, py + ph * ty)],
             GREY, 1.1)
    for name, (fx, fy, fw, fh) in boxes.items():
        bx, by = px + pw * fx, py + ph * fy
        bw, bh = pw * fw, ph * fh
        sh = rect(slide, bx, by, bw, bh, fill=ZONE[name], line=WHITE)
        tf = sh.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = 0
        tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        para(tf, "zona %s" % name, size=7.5, bold=True, color=WHITE, first=True,
             space_after=0, align=PP_ALIGN.CENTER)
    vx = px + pw * 0.40
    rect(slide, vx - 0.032, py + ph * 0.47, 0.064, ph * 0.09, fill=RED)
    tf = tb(slide, px + pw * 0.57, py + ph * 0.42, 1.35, 0.35)
    para(tf, "vincolo ridotto\n(caso da verificare)", size=7.5, bold=True, color=RED,
         first=True, space_after=0)
    tf = tb(slide, px, py + ph + 0.01, pw, 0.2)
    para(tf, "schema concettuale  |  spessore = capacita'  |  rosso = limite ridotto",
         size=7.5, color=GREY, first=True, space_after=0)


def mock_open(slide, x, y, w, h):
    px, py, pw, ph = x + 0.42, y + 0.28, w - 0.72, h - 0.72
    rect(slide, px, py, pw, ph, fill=WHITE, line=RULE, line_w=0.75)
    rows = [
        ("spiegazione", "evidenza", "stato"),
        ("merit order, rinnovabili a costo nullo", "curva offerta", "verificare"),
        ("capacita' di uscita ridotta", "transiti e limiti", "verificare"),
        ("lo zero non coincide col floor", "regole di mercato", "confermato"),
        ("lato domanda: pompaggi e domanda elastica", "curve domanda", "aperta"),
    ]
    rh = ph / len(rows)
    for r, row in enumerate(rows):
        if r == 0:
            rect(slide, px, py + r * rh, pw, rh, fill=LIGHT)
        for c, cell in enumerate(row):
            cx = px + pw * [0.0, 0.44, 0.76][c]
            cwid = pw * ([0.44, 0.32, 0.24][c])
            tf = tb(slide, cx + 0.07, py + r * rh + rh * 0.28, cwid - 0.11, rh)
            para(tf, cell, size=7.5, bold=(r == 0),
                 color=(ACCENT if r == 0 else INK), first=True, space_after=0)
        rect(slide, px, py + (r + 1) * rh, pw, 0.006, fill=RULE)
    tf = tb(slide, px, py + ph + 0.03, pw, 0.3)
    para(tf, "domande aperte all'esperto + 'cosa significa per un desk'",
         size=7.5, color=ACCENT, bold=True, first=True, space_after=0)


# ---------------------------------------------------------------- contenuti
SLIDES = [
    {
        "num": 1,
        "title": "1 \u00b7 Prezzi: la mappa delle ore a prezzo zero",
        "question": "Dove e quando il prezzo zonale va a zero?",
        "table": [
            ("Serie orarie dei prezzi: 7 zone + indice nazionale", "ME_ZonalPrices (MGP, PT60)"),
            ("Timestamp: ora locale, ora legale (giornate da 23/25 ore)", "stesso dataset, campo Hour"),
            ("Classificazione di ogni ora: zero / negativo / compresso / alto", "calcolo su ME_ZonalPrices"),
            ("Continuit\u00e0 della serie e dati mancanti", "verifica su ME_ZonalPrices"),
            ("Finestra di 48 ore dello scenario, scelta sul grafico annuale", "taglio sulle serie orarie"),
            ("Confronto con le statistiche pubblicate", "ME_PriceSpread (MGP) \u00b7 Relazione Annuale GME"),
        ],
        "output": [
            "Grafico A \u2014 prezzi di indice nazionale e 7 zone sull'intero periodo, con le ore a zero evidenziate: da qui si sceglie la finestra",
            "Grafico B \u2014 heatmap zona \u00d7 periodo: conteggio delle ore a zero e negative",
            "Lettura: l'indice nazionale (media ponderata) riassume la divergenza fra zone.",
        ],
        "mock": mock_prices,
        "mock_caption": "Mock: l'indice nazionale segue il mercato, le zone si staccano.",
        "doubt": "L'indice nazionale \u00e8 il riferimento giusto o serve la mediana? E quante ore consecutive a zero fanno un 'evento'?",
        "time": "~1,5 h",
    },
    {
        "num": 2,
        "title": "2 \u00b7 Scelta dell'evento: il criterio, non la preferenza",
        "question": "Quale evento analizzo, e con quale criterio?",
        "table": [
            ("Sequenze di ore consecutive a prezzo zero, per zona", "calcolo su ME_ZonalPrices (PT60)"),
            ("Prezzi di tutte le zone nelle 48 ore dell'evento", "ME_ZonalPrices (MGP, PT60)"),
            ("Curva domanda/offerta di un'ora: prezzo, quantit\u00e0 offerta e accettata", "ME_DemandAndSupply (MGP) \u00b7 Hour"),
            ("Limiti tecnici di offerta e regole di formazione del prezzo", "DTF 20 MPE \u00b7 Disciplina ME artt. 41-42"),
        ],
        "output": [
            "Tabella eventi candidati: data, zona, ore consecutive a zero, prezzo minimo",
            "Grafico \u2014 domanda e offerta dell'ora scelta: marker all'intersezione sul tratto piatto a zero",
            "Box regole: lo zero non \u00e8 il floor, \u00e8 l'offerta marginale accettata",
        ],
        "mock": mock_event,
        "mock_caption": "Mock: l'offerta ha un tratto piatto a prezzo zero e la domanda lo interseca.",
        "doubt": "Il criterio (ore consecutive a zero in almeno due zone) regge? Come sceglieresti l'evento senza scegliere a posteriori?",
        "time": "~2 h",
    },
    {
        "num": 3,
        "title": "3 \u00b7 Curve di domanda e offerta nel tempo",
        "question": "Nelle ore successive l'intersezione si sposta davvero?",
        "table": [
            ("Curve domanda/offerta di ogni ora della finestra di 48 ore, per zona", "ME_DemandAndSupply (MGP) \u00b7 Hour"),
            ("Stesse curve per una zona di controllo", "id"),
            ("Per ora: quantit\u00e0 offerta per livello di prezzo e accettata", "id"),
            ("Volume offerto a prezzo zero: la variabile della persistenza", "id"),
            ("Prezzo zonale delle altre zone nella stessa ora", "ME_ZonalPrices (MGP, PT60)"),
        ],
        "output": [
            "Grafico A \u2014 small multiples, un pannello per ora: offerta, domanda, marker del prezzo",
            "Grafico B \u2014 heatmap ora \u00d7 livello di prezzo: quantit\u00e0 offerta e linea del prezzo zonale",
            "Lettura (ipotesi): la domanda scende sotto il tratto a zero \u2192 prezzo appiattito",
        ],
        "mock": mock_time,
        "mock_caption": "Mock: un pannello per ora; in rosso il tratto piatto a prezzo zero.",
        "doubt": "Small multiples o heatmap? Serve una zona di controllo nello stesso pannello?",
        "time": "~2 h",
    },
    {
        "num": 4,
        "title": "4 \u00b7 Chi offre davvero: volumi per fonte e zona",
        "question": "L'offerta che schiaccia il prezzo \u00e8 rinnovabile, idroelettrica o gas?",
        "table": [
            ("Generazione per fonte, per zona, ora per ora", "ENTSO-E Transparency (Actual Generation)"),
            ("Carico (domanda) di ogni zona nella finestra", "ME_Demand (MGP)"),
            ("Volumi venduti e rigittati per zona e tecnologia", "Offers_PublicDomain (MGP) + file GMT"),
        ],
        "output": [
            "7 grafici, uno per zona: generazione impilata per fonte e carico, sulla finestra di 48 ore",
            "Il gap fra generazione e carico è il surplus della zona: in una la generazione supera il carico, nell'altra il contrario",
            "Lettura: il volume rigittato è la firma del surplus non vendibile",
        ],
        "mock": mock_zones_48h,
        "mock_caption": "Mock: un pannello per zona sulla finestra di 48 ore, generazione impilata e carico.",
        "doubt": "API GME o ENTSO-E per la ripartizione per fonte? E il gap fra carico e venduti come lo leggi?",
        "time": "~3 h",
    },
    {
        "num": 5,
        "title": "5 \u00b7 Mappa e transiti: perch\u00e9 il surplus non esce",
        "question": "\u00c8 un problema di rete? Quale vincolo limita l'uscita dalla zona?",
        "table": [
            ("Limiti di transito fra zone, per ora", "ME_TransmissionLimits (MGP)"),
            ("Flussi e saturazione per coppia di zone", "ME_Transits (MGP)"),
            ("Limiti di trasferimento fra aree e piano di manutenzione", "Terna"),
            ("Flussi programmati e capacit\u00e0 sui confini", "ENTSO-E Transparency"),
            ("Prezzi ai due lati del vincolo: se divergono, \u00e8 saturo", "ME_ZonalPrices (MGP, PT60)"),
        ],
        "output": [
            "Grafico A \u2014 mappa schematica: spessore = capacit\u00e0, colore = congestione",
            "Grafico B \u2014 limite di trasferimento per ora nella finestra, contro il valore normale",
            "Lettura: a vincolo saturo il prezzo non si allinea; lo zero \u00e8 un eccesso che non esce",
        ],
        "mock": mock_map,
        "mock_caption": "Mock: schema concettuale; in rosso il tipo di vincolo da verificare.",
        "doubt": "Quale fonte \u00e8 l'autorit\u00e0 sui limiti (GME, Terna, ENTSO-E)? Come si mettono in relazione senza contraddirsi?",
        "time": "~3 h",
    },
    {
        "num": 6,
        "title": "6 \u00b7 Lettura finale e discussione aperta",
        "question": "Cosa dice l'analisi, cosa non so, cosa porto al colloquio",
        "table": [
            ("Sintesi: 'spiegazione \u2192 evidenza \u2192 stato'", "tabella finale"),
            ("Le spiegazioni possibili, con la prova che le sostiene o le confuta", "punti 1-5"),
            ("Numeri di contesto dalle fonti ufficiali", "Relazione Annuale GME \u00b7 Rapporti Terna"),
            ("Risposta di sistema: capacity market, rete, nuovi collegamenti", "ME_GeneralisedConstraints \u00b7 ME_MarketCoupling"),
        ],
        "output": [
            "Tabella finale: spiegazione, evidenza, stato (confermata / da verificare / aperta)",
            "Le domande aperte da girare all'esperto (metodo e dati)",
            "Chiusura 'da desk': chi compra a zero, chi perde, perch\u00e9 la risposta \u00e8 di sistema",
        ],
        "mock": mock_open,
        "mock_caption": "Mock: ogni spiegazione con evidenza e stato.",
        "doubt": "Su quale punto saresti pi\u00f9 severo? 'Prezzo zero = surplus non esportabile' regge?",
        "time": "~1,5 h",
    },
]


# ---------------------------------------------------------------- build
def build():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    blank = prs.slide_layouts[6]
    for s in SLIDES:
        slide = prs.slides.add_slide(blank)
        chrome(slide, s, len(SLIDES))
    prs.save(OUT)
    return OUT


def main():
    out = build()
    size = os.path.getsize(out) // 1024
    print("[ok] %s - %d slide, %d KB" % (os.path.basename(out), len(SLIDES), size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
