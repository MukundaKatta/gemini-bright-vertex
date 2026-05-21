"""Generate the lablab submission cover image (1200x675, 16:9 thumb).

Reuses the same palette + typography as the intro slide so the cover and
the demo video read as one set. Stage 1 (Bright Data amber) → Stage 2
(Google blue) gradient accent bar mirrors the two-stage flow.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageColor


W, H = 1200, 675
FG = "#0f172a"
FG_MUTED = "#475569"
ACCENT = "#f59e0b"            # Bright Data amber
ACCENT_2 = "#4285f4"          # Google blue
ACCENT_DEEP = "#b45309"
BG = "#ffffff"
PANEL = "#f8fafc"

SF = "/System/Library/Fonts/SFNS.ttf"
SFI = "/System/Library/Fonts/SFNSItalic.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"
if not Path(MONO).exists():
    MONO = "/System/Library/Fonts/Menlo.ttc"


def font(size, mono=False, italic=False):
    path = MONO if mono else (SFI if italic else SF)
    return ImageFont.truetype(path, size)


def gradient_bar(d, x0, y0, x1, y1, steps=160):
    a = ImageColor.getrgb(ACCENT)
    b = ImageColor.getrgb(ACCENT_2)
    width = (x1 - x0) / steps
    for i in range(steps):
        t = i / max(steps - 1, 1)
        r = round(a[0] + (b[0] - a[0]) * t)
        g = round(a[1] + (b[1] - a[1]) * t)
        bl = round(a[2] + (b[2] - a[2]) * t)
        sx = round(x0 + i * width)
        ex = round(x0 + (i + 1) * width)
        d.rectangle([(sx, y0), (ex, y1)], fill=(r, g, bl))


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Footer band
    d.rectangle([(0, H - 40), (W, H)], fill=PANEL)
    d.text((24, H - 32),
           "github.com/MukundaKatta/gemini-bright-vertex",
           font=font(16), fill=FG_MUTED)
    d.text((W - 200, H - 32), "Apache 2.0", font=font(16), fill=FG_MUTED)

    # Title block
    d.text((60, 80), "gemini-bright-vertex", font=font(64), fill=FG)
    gradient_bar(d, 60, 180, 540, 192)

    d.text((60, 220),
           "STAGE 1: Bright Data scrape",
           font=font(26), fill=ACCENT_DEEP)
    d.text((60, 256),
           "STAGE 2: Vertex AI Search index",
           font=font(26), fill=ACCENT_2)
    d.text((60, 292),
           "STAGE 3: synthesized answer, verbatim quotes",
           font=font(26), fill=FG)

    d.text((60, 380),
           "Gemini 2.5 ADK + Bright Data MCP + Vertex AI Search",
           font=font(20, mono=True), fill=FG)
    d.text((60, 415),
           "(SERP + Web Unlocker + Discovery Engine / GenAI App Builder)",
           font=font(18), fill=FG_MUTED)

    d.text((60, 500),
           "Bright Data Web Data UNLOCKED Hackathon",
           font=font(22), fill=FG)
    d.text((60, 532),
           "Track 2: Intelligence Synthesis",
           font=font(20), fill=ACCENT_DEEP)
    d.text((60, 562),
           "lablab.ai · May 25 to 31, 2026",
           font=font(20), fill=FG_MUTED)

    out = Path("/Users/ubl/gemini-bright-vertex/.video-build/cover.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    size = out.stat().st_size / 1024
    print(f"DONE: {out} ({size:.1f} KB)")


if __name__ == "__main__":
    main()
