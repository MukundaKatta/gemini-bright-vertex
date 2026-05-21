"""Build the final gemini-bright-vertex demo video.

Composition:
  - ~14s intro slide with TTS narration
  - ~32s real Cloud Run footage (already captured at .video-build/real_footage.mp4)
  - ~11s outro slide with TTS narration

Total ≈ 60s, well under the 3-minute lablab submission limit. Centerpiece
is real footage of the deployed Streamlit dashboard answering "Anthropic
Claude latest release notes 2026" by walking the Bright Data MCP tools
(SERP API + Web Unlocker scrape + LinkedIn dataset lookup) and citing
verbatim quotes back from the unlocked Anthropic pages.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1920, 1080
FG = "#0f172a"
FG_MUTED = "#475569"
ACCENT = "#f59e0b"          # Bright Data amber  (Stage 1 — scrape)
ACCENT_2 = "#4285f4"        # Google blue        (Stage 2 — Vertex AI Search)
ACCENT_DEEP = "#b45309"     # Bright Data deep amber, for footer accents
BG = "#ffffff"
PANEL = "#f8fafc"


def _draw_accent_gradient(d, x0, y0, x1, y1, steps=160):
    """Render the Stage 1 -> Stage 2 amber-to-Google-blue accent bar."""
    from PIL import ImageColor
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

SF = "/System/Library/Fonts/SFNS.ttf"
SFI = "/System/Library/Fonts/SFNSItalic.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"
if not Path(MONO).exists():
    MONO = "/System/Library/Fonts/Menlo.ttc"


def font(size, mono=False, italic=False):
    path = MONO if mono else (SFI if italic else SF)
    return ImageFont.truetype(path, size)


def draw_intro(img, d):
    d.rectangle([(0, 0), (W, H)], fill=BG)
    d.rectangle([(0, H - 56), (W, H)], fill=PANEL)
    d.text((48, H - 44),
           "github.com/MukundaKatta/gemini-bright-vertex",
           font=font(22), fill=FG_MUTED)
    d.text((W - 270, H - 44), "Apache 2.0", font=font(22), fill=FG_MUTED)
    d.text((96, 200), "gemini-bright-vertex", font=font(108), fill=FG)
    # Stage 1 (Bright Data amber) -> Stage 2 (Google blue) gradient bar.
    _draw_accent_gradient(d, 96, 340, 700, 352)
    d.text((96, 390),
           "STAGE 1: Bright Data scrape  →  STAGE 2: Vertex AI Search index",
           font=font(34), fill=FG)
    d.text((96, 440),
           "→  STAGE 3: synthesized answer with verbatim quotes.",
           font=font(34), fill=FG_MUTED)
    d.text((96, 560),
           "Bright Data Web Data UNLOCKED Hackathon",
           font=font(32), fill=FG)
    d.text((96, 605),
           "· lablab.ai · Track 2: Intelligence Synthesis ·",
           font=font(30), fill=FG_MUTED)
    d.text((96, 650),
           "· May 25 to 31, 2026 ·",
           font=font(30), fill=FG_MUTED)
    d.text((96, 780),
           "What follows is real footage of the deployed",
           font=font(28, italic=True), fill=FG_MUTED)
    d.text((96, 820),
           "Cloud Run dashboard answering a live two-stage question.",
           font=font(28, italic=True), fill=FG_MUTED)


def draw_outro(img, d):
    d.rectangle([(0, 0), (W, H)], fill=BG)
    d.text((96, 160), "gemini-bright-vertex", font=font(72), fill=FG)
    _draw_accent_gradient(d, 96, 270, 700, 282)
    d.text((96, 320),
           "github.com/MukundaKatta/gemini-bright-vertex",
           font=font(30, mono=True), fill=ACCENT_DEEP)
    d.text((96, 400),
           "gemini-bright-vertex-1029931682737.us-central1.run.app",
           font=font(28, mono=True), fill=ACCENT_2)
    d.text((96, 510),
           "STAGE 1  Bright Data MCP (SERP / Web Unlocker / extract / dataset)",
           font=font(28), fill=ACCENT_DEEP)
    d.text((96, 555),
           "STAGE 2  Vertex AI Search (Discovery Engine + GenAI App Builder)",
           font=font(28), fill=ACCENT_2)
    d.text((96, 600),
           "STAGE 3  vertex_search → synthesized answer with verbatim quotes",
           font=font(28), fill=FG)
    d.text((96, 700),
           "Google Cloud Agent Builder (ADK) + Gemini 2.5 Flash on Vertex AI",
           font=font(28), fill=FG_MUTED)
    d.text((96, 800),
           "Every quote is copied byte-for-byte from the indexed corpus.",
           font=font(26, italic=True), fill=FG_MUTED)
    d.text((96, 840),
           "No paraphrasing. Track 2: Intelligence Synthesis.",
           font=font(26, italic=True), fill=FG_MUTED)
    d.text((96, 910),
           "Apache 2.0. Mukunda Katta, independent.",
           font=font(28, italic=True), fill=FG_MUTED)


INTRO_NARRATION = (
    "Bright Data plus Vertex A I Search. Track Two, Intelligence "
    "Synthesis. A two stage research agent. Stage one scrapes the live "
    "web through the Bright Data M C P server. Stage two indexes every "
    "scraped page into a Vertex A I Search corpus. Stage three answers "
    "the user's question from the indexed corpus with verbatim quotes. "
    "What follows is real footage of the deployed Cloud Run dashboard."
)


OUTRO_NARRATION = (
    "Bright Data plus Vertex A I Search. Track Two, Intelligence "
    "Synthesis. Stage one unlocked the live web. Stage two turned it "
    "into a durable, queryable corpus on Vertex A I Search. Stage three "
    "synthesized the final answer with quotes copied byte for byte from "
    "the indexed corpus. Built on the A D K with Gemini two point five "
    "Flash. Apache two point zero. Thank you."
)


def render_slide(name, draw_fn, outdir):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_fn(img, d)
    p = outdir / f"{name}.png"
    img.save(p, "PNG", optimize=True)
    return p


def say_to_m4a(text, outpath):
    aiff = outpath.with_suffix(".aiff")
    subprocess.run(
        ["say", "-v", "Samantha", "-r", "175", "-o", str(aiff), text],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(aiff),
         "-c:a", "aac", "-b:a", "128k", str(outpath)],
        check=True,
    )
    aiff.unlink(missing_ok=True)


def make_slide_segment(png, m4a, out):
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(m4a)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    seg_dur = float(dur) + 0.5
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-loop", "1", "-i", str(png),
        "-i", str(m4a),
        "-af", "apad=pad_dur=0.5",
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-r", "30", "-t", f"{seg_dur:.2f}",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(out),
    ], check=True)
    return out, seg_dur


def main():
    outdir = Path("/Users/ubl/gemini-bright-vertex/.video-build")
    outdir.mkdir(parents=True, exist_ok=True)

    real = outdir / "real_footage.mp4"
    if not real.exists():
        sys.exit(f"missing real footage at {real}; run record_real_demo.py first")

    for needed in ("ffmpeg", "ffprobe", "say"):
        if shutil.which(needed) is None:
            sys.exit(f"missing tool: {needed}")

    print("[1/4] slides...")
    intro_png  = render_slide("01_intro",  draw_intro,  outdir)
    outro_png  = render_slide("99_outro",  draw_outro,  outdir)
    print(f"  rendered {intro_png.name}")
    print(f"  rendered {outro_png.name}")

    print("[2/4] audio...")
    intro_m4a = outdir / "01_intro.m4a"
    outro_m4a = outdir / "99_outro.m4a"
    say_to_m4a(INTRO_NARRATION, intro_m4a)
    print(f"  spoke {intro_m4a.name}")
    say_to_m4a(OUTRO_NARRATION, outro_m4a)
    print(f"  spoke {outro_m4a.name}")

    print("[3/4] segments...")
    intro_seg, intro_dur = make_slide_segment(intro_png, intro_m4a, outdir / "seg_01_intro.mp4")
    outro_seg, outro_dur = make_slide_segment(outro_png, outro_m4a, outdir / "seg_99_outro.mp4")
    real_dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(real)],
        capture_output=True, text=True, check=True,
    ).stdout.strip())
    print(f"  intro {intro_dur:.1f}s · real {real_dur:.1f}s · outro {outro_dur:.1f}s")

    print("[4/4] concat...")
    list_file = outdir / "concat.txt"
    list_file.write_text("\n".join([
        f"file '{intro_seg.resolve()}'",
        f"file '{real.resolve()}'",
        f"file '{outro_seg.resolve()}'",
    ]) + "\n")

    final = outdir / "demo.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "128k",
        str(final),
    ], check=True)

    size_mb = final.stat().st_size / (1024 * 1024)
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(final)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    print(f"\nDONE: {final}  ({size_mb:.1f} MB, {float(dur):.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
