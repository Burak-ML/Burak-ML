#!/usr/bin/env python3
"""The profile header, drawn twice: once on paper, once on navy.

Kept deliberately plain: a name, one line about the work, nothing to decode.
The static frame is the whole design; there is no animation to wait for.
"""

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
