"""Palette for the profile header, taken from the avatar: deep navy ground,
warm off-white type and one accent, the gold of the glasses.

Two themes because a GitHub reader may be on either. The light one is warm
paper with the same navy as ink, so the pair reads as one object.
"""

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "light": dict(
        bg="#f6f2ea",
        glow="#f6f2ea",
        ink="#0a1f44",
        ink2="#3b4d70",
        ink3="#6a7893",
        rule="#d6d0c2",
        accent="#8a5a12",
        chip="#ece6d9",
        chip_line="#d6d0c2",
        wordmark="#0a1f44",
    ),
    "dark": dict(
        bg="#061a3a",
        glow="#0d3269",
        ink="#f6efe4",
        ink2="#b8c5dd",
        ink3="#7e92b4",
        rule="#17335f",
        accent="#e6b56a",
        chip="#0f2b57",
        chip_line="#1d3f77",
        wordmark="#f6efe4",
    ),
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))
