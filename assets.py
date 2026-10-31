#!/usr/bin/env python3
"""The profile header and about panel, each drawn twice: on paper and on navy.

Kept deliberately plain: nothing to decode and no animation to wait for.
"""

import textwrap

from theme import MONO, THEMES, esc
from wordmark import wordmark

W = 1200
H = 330
M = 56                      # page margin


def build_header(theme_name, u, projects):
    t = THEMES[theme_name]
    label = "Burak, @Burak-ML. AI automation and agentic systems; data science with Python and SQL."

    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
         'height="%d" role="img" aria-label="%s">' % (W, H, W, H, esc(label)),
         "<defs>"
         '<radialGradient id="glow" cx="0.82" cy="0.35" r="0.75">'
         '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
         "</radialGradient></defs>" % (t["glow"], t["bg"]),
         '<rect width="%d" height="%d" fill="%s"/>' % (W, H, t["bg"]),
         '<rect width="%d" height="%d" fill="url(#glow)"/>' % (W, H)]

    p.append('<text x="%d" y="%d" font-family="%s" font-size="12.5" fill="%s" '
             'letter-spacing="2.2">@BURAK-ML</text>' % (M, 44, MONO, t["accent"]))

    mark, _, mh = wordmark("BURAK", M, 66, 0.95, t["wordmark"])
    p.append(mark)

    p.append('<rect x="%d" y="%d" width="48" height="3" fill="%s"/>'
             % (M, 226, t["accent"]))
    p.append('<text x="%d" y="%d" font-family="%s" font-size="22" fill="%s" '
             'letter-spacing="-0.3">AI automation &amp; agentic systems.</text>'
             % (M, 264, MONO, t["ink"]))
    p.append('<text x="%d" y="%d" font-family="%s" font-size="15" fill="%s">'
             'Data science with Python and SQL.</text>' % (M, 292, MONO, t["ink2"]))

    p.append("</svg>")
    return "\n".join(p) + "\n"


# --------------------------------------------------------------------------- about

ABOUT = [
    "I'm Burak, a second-year Computer Programming student in T\u00fcrkiye. I build "
    "AI automation and agent tooling: an MCP-based skill and memory system, a "
    "local-first coding agent and exploratory LLM evaluation work. I develop with "
    "AI end to end, and I write down how each project works and how to run it.",
    "Alongside that, I work in data science. I'm open to internship and junior "
    "opportunities.",
]

TOOLS = [
    ("AI AUTOMATION & AGENTS",
     ["MCP", "Tool-using agents", "LLM evaluation", "TypeScript", "GitHub Actions"]),
    ("DATA SCIENCE",
     ["Python", "SQL", "PostgreSQL", "Pandas", "NumPy", "Jupyter"]),
]

CHIP_H, CHIP_GAP, CHIP_FS = 30, 10, 13.5
CHAR_W = 0.6                # monospace advance, as a fraction of the font size


def _chips(t, labels, x, y, max_w):
    """Flow the labels into rows no wider than max_w. Returns (svg, bottom)."""
    out, cx, cy = [], x, y
    for label in labels:
        w = round(len(label) * CHIP_FS * CHAR_W + 28)
        if cx + w > x + max_w:
            cx, cy = x, cy + CHIP_H + CHIP_GAP
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="15" fill="%s" stroke="%s"/>'
                   % (cx, cy, w, CHIP_H, t["chip"], t["chip_line"]))
        out.append('<text x="%.1f" y="%d" font-family="%s" font-size="%s" fill="%s" '
                   'text-anchor="middle">%s</text>'
                   % (cx + w / 2, cy + 20, MONO, CHIP_FS, t["ink"], esc(label)))
        cx += w + CHIP_GAP
    return out, cy + CHIP_H


def build_about(theme_name):
    t = THEMES[theme_name]
    body = []
    y = 46
    body.append('<text x="%d" y="%d" font-family="%s" font-size="12.5" fill="%s" '
                'letter-spacing="2.2">ABOUT</text>' % (M, y, MONO, t["accent"]))
    y += 14

    for i, para in enumerate(ABOUT):
        size, colour, step = (17, t["ink"], 30) if i == 0 else (16, t["ink2"], 28)
        for line in textwrap.wrap(para, 96):
            y += step
            body.append('<text x="%d" y="%d" font-family="%s" font-size="%d" fill="%s">%s</text>'
                        % (M, y, MONO, size, colour, esc(line)))
        y += 10

    y += 14
    body.append('<rect x="%d" y="%d" width="%d" height="1" fill="%s"/>' % (M, y, W - 2 * M, t["rule"]))
    y += 34

    col_w = (W - 2 * M - 48) // 2
    bottom = y
    for c, (title, labels) in enumerate(TOOLS):
        x = M + c * (col_w + 48)
        body.append('<text x="%d" y="%d" font-family="%s" font-size="12.5" fill="%s" '
                    'letter-spacing="2.2">%s</text>' % (x, y, MONO, t["accent"], esc(title)))
        chips, b = _chips(t, labels, x, y + 18, col_w)
        body += chips
        bottom = max(bottom, b)

    h = bottom + 44
    label = "About Burak. " + " ".join(ABOUT) + " " + " ".join(
        "%s: %s." % (n.title(), ", ".join(l)) for n, l in TOOLS)
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
         'height="%d" role="img" aria-label="%s">' % (W, h, W, h, esc(label)),
         "<defs>"
         '<radialGradient id="glow" cx="0.18" cy="0.2" r="0.9">'
         '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
         "</radialGradient></defs>" % (t["glow"], t["bg"]),
         '<rect width="%d" height="%d" fill="%s"/>' % (W, h, t["bg"]),
         '<rect width="%d" height="%d" fill="url(#glow)"/>' % (W, h)]
    return "\n".join(p + body + ["</svg>"]) + "\n"
