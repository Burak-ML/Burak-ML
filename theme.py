"""Palette for the profile header, taken from the avatar: deep navy ground,
warm off-white type and one accent, the gold of the glasses.

One theme for both GitHub modes, so the profile looks the same everywhere.
"""

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "navy": dict(
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
