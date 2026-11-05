"""Render animated, GitHub-safe GIFs from the profile's self-contained SVGs.

The SVGs remain editable source assets. Chromium renders their actual CSS and
SMIL timelines when available. CairoSVG supplies a portable light-sweep
animation fallback for sandboxed/headless environments. Pillow creates compact,
infinitely looping exports in either mode.

Usage:
    python3 render_gifs.py
    python3 render_gifs.py --only hero
"""

from __future__ import annotations

import argparse
from io import BytesIO
import math
import os
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

# A settled intro, a full motion cycle, and a moderate frame rate give readable
# cards without creating enormous GIFs in the GitHub profile.
SCENES = {
    "hero": (13.2, 6, 840, 3.9),
    "mission": (4.6, 7, 840, 2.8),
    "stack": (6.3, 7, 840, 3.2),
    "identity": (7.0, 7, 840, 3.0),
    "contribution": (3.0, 7, 840, 1.5),
    "contact": (7.2, 7, 840, 2.5),
}

BADGES = [
    "badge-codmash",
    "badge-website",
    "badge-portfolio",
    "badge-email",
    "badge-github",
    "badge-linkedin",
]


def dimensions(svg_file: Path) -> tuple[int, int]:
    root = ET.parse(svg_file).getroot()
    return int(root.attrib["width"]), int(root.attrib["height"])


def set_animation_time(page, seconds: float) -> None:
    """Seek SMIL and CSS animation timelines without wall-clock waiting."""
    page.evaluate(
        """(seconds) => {
          const root = document.documentElement;
          if (root.pauseAnimations) root.pauseAnimations();
          if (root.setCurrentTime) root.setCurrentTime(seconds);
          for (const anim of document.getAnimations({subtree:true})) {
            anim.pause();
            anim.currentTime = seconds * 1000;
          }
        }""",
        seconds,
    )


def global_palette(frames: list[Image.Image], colors: int) -> Image.Image:
    picks = [frames[round(i * (len(frames) - 1) / 3)] for i in range(4)]
    small_width = min(280, frames[0].width)
    small_height = min(180, frames[0].height)
    sample = Image.new("RGB", (2 * small_width, 2 * small_height))
    for i, frame in enumerate(picks):
        block = frame.resize((small_width, small_height), Image.Resampling.BILINEAR)
        sample.paste(block, ((i % 2) * small_width, (i // 2) * small_height))
    return sample.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)


def write_gif(name: str, frames: list[Image.Image], fps: int) -> Path:
    colors = 128 if not name.startswith("badge-") else 80
    palette = global_palette(frames, colors)
    paletted = [
        frame.quantize(palette=palette, dither=Image.Dither.NONE)
        for frame in frames
    ]
    output = ASSETS / f"{name}.gif"
    paletted[0].save(
        output,
        save_all=True,
        append_images=paletted[1:],
        duration=round(1000 / fps),
        loop=0,
        optimize=True,
        disposal=2,
    )
    with Image.open(output) as check:
        if check.n_frames < 3 or check.info.get("loop") != 0:
            raise RuntimeError(f"Animation failed validation: {output}")
        actual_frames = check.n_frames
    print(f"{output.relative_to(ROOT)}  |  {actual_frames} frames  |  {output.stat().st_size // 1024} KiB")
    return output


def render_scene(browser, name: str, period: float, fps: int, target_width: int, intro: float) -> Path:
    svg_file = ASSETS / f"{name}.svg"
    native_width, native_height = dimensions(svg_file)
    target_height = round(native_height * target_width / native_width)
    context = browser.new_context(
        viewport={"width": target_width, "height": target_height},
        device_scale_factor=1,
        reduced_motion="no-preference",
    )
    page = context.new_page()
    page.goto(svg_file.as_uri(), wait_until="load")
    page.evaluate(
        """([width, height]) => {
            const svg = document.documentElement;
            svg.setAttribute('width', String(width));
            svg.setAttribute('height', String(height));
        }""",
        [target_width, target_height],
    )
    page.evaluate("() => document.fonts.ready")
    frames: list[Image.Image] = []
    frame_count = max(16, round(period * fps))
    for index in range(frame_count):
        set_animation_time(page, intro + period * index / frame_count)
        screenshot = page.screenshot(type="png", animations="allow")
        frame = Image.open(BytesIO(screenshot)).convert("RGB")
        frames.append(frame)
    context.close()
    return write_gif(name, frames, fps)


def render_cairo_scene(name: str, period: float, fps: int, target_width: int) -> Path:
    """Use an animated light sweep and signal particles over a static SVG frame."""
    os.environ.setdefault("XDG_CACHE_HOME", "/tmp/codmash-render-cache")
    Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)
    import cairosvg

    png = cairosvg.svg2png(
        url=str(ASSETS / f"{name}.svg"),
        output_width=target_width,
    )
    base = Image.open(BytesIO(png)).convert("RGBA")
    w, h = base.size
    frames = []
    count = max(16, round(period * fps))
    badge = name.startswith("badge-")
    for index in range(count):
        theta = 2 * math.pi * index / count
        progress = index / count
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")

        # A narrow diagonal highlight travels through the composition.
        x = -max(80, w // 5) + (w + max(160, w // 2)) * progress
        sweep_width = max(12, w // (7 if badge else 18))
        skew = max(6, h // 5)
        hue = (255, 255, 255) if badge else (255, 160, 65)
        draw.polygon(
            [(x, 0), (x + sweep_width, 0), (x - skew + sweep_width, h), (x - skew, h)],
            fill=(*hue, 50 if badge else 17),
        )
        draw.polygon(
            [(x + sweep_width // 2, 0), (x + sweep_width // 2 + 3, 0),
             (x - skew + sweep_width // 2 + 3, h), (x - skew + sweep_width // 2, h)],
            fill=(255, 240, 200, 45 if badge else 29),
        )
        if not badge:
            # Tiny amber/blue activity lights, staggered for a lively GIF.
            for dot in range(19):
                px = (dot * 137 + 41) % max(1, w - 24) + 12
                py = (dot * 71 + 13) % max(1, h - 24) + 12
                pulse = (math.sin(theta + dot * 1.83) + 1) / 2
                radius = 1 + (dot % 3 == 0)
                color = (255, 156, 58) if dot % 3 else (84, 181, 255)
                draw.ellipse(
                    (px - radius, py - radius, px + radius, py + radius),
                    fill=(*color, int(14 + 90 * pulse)),
                )
            # Small progress signal stays inside the image's existing frame.
            line_length = int((w - 36) * progress)
            draw.rounded_rectangle(
                (18, h - 5, 18 + line_length, h - 3),
                radius=1, fill=(255, 138, 43, 65),
            )
        frames.append(Image.alpha_composite(base, overlay).convert("RGB"))
    return write_gif(name, frames, fps)


def render_all(only: str | None = None, renderer: str = "auto") -> list[Path]:
    selected = {**SCENES}
    for badge in BADGES:
        selected[badge] = (2.8, 8, dimensions(ASSETS / f"{badge}.svg")[0], 0.0)
    if only:
        if only not in selected:
            raise ValueError(f"Unknown panel: {only}")
        selected = {only: selected[only]}

    if renderer == "cairo":
        return [
            render_cairo_scene(name, period, fps, width)
            for name, (period, fps, width, _intro) in selected.items()
        ]

    output: list[Path] = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None,
                args=["--no-sandbox"],
            )
            try:
                for name, (period, fps, width, intro) in selected.items():
                    print(f"Rendering {name}...", flush=True)
                    output.append(render_scene(browser, name, period, fps, width, intro))
            finally:
                browser.close()
        return output
    except Exception as exc:
        if renderer == "browser":
            raise
        print(f"Browser animation unavailable ({type(exc).__name__}); using static-SVG light-sweep rendering.")
        for name, (period, fps, width, _intro) in selected.items():
            if not (ASSETS / f"{name}.gif").exists() or name not in {p.stem for p in output}:
                output.append(render_cairo_scene(name, period, fps, width))
        return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="Render one named panel or badge")
    parser.add_argument("--renderer", choices=("auto", "browser", "cairo"), default="auto")
    args = parser.parse_args()
    render_all(args.only, args.renderer)
