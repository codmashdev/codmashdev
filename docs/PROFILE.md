# CodMash animated GitHub profile — maintenance guide

This profile is a seven-section CodMash studio experience: animated hero, philosophy, tech arsenal, studio identity, selected projects, contribution city, and contact. It uses the original **male CodMash ninja** and dark navy / orange design language.

## Asset pipeline

- `templates/*.svg` are editable design templates for the five main panels.
- `build_assets.py` creates the six complete panel SVGs (including the data-driven contribution city) and six badge SVGs in `assets/`.
- `render_gifs.py` converts **all 12 generated SVG display assets** into GIFs: `hero.gif`, `mission.gif`, `stack.gif`, `identity.gif`, `contribution.gif`, `contact.gif`, and all six `badge-*.gif` files.
- `README.md` references GIFs only for the CodMash design panels and badges; the five source SVG templates remain editable and are never linked directly.
- `team7-dance.gif`, `rasengan-run.gif`, and `chibi-walk.gif` are existing reference animations retained unchanged.
- Original PNG/WebP character artwork, fonts, project links, and public data are preserved.

When Chromium is available, the GIF renderer captures time-indexed frames of each SVG's original CSS/SMIL animation. Where the browser cannot launch (for example, in some restricted sandboxes), it falls back to CairoSVG and adds a subtle animated light sweep, progress signal, and particles. Both produce real multi-frame looping GIFs. The default mode automatically chooses.

## Rebuild locally

Install dependencies (Python 3.12 recommended):

```sh
python3 -m pip install -r requirements-gif.txt
python3 -m playwright install chromium
```

Then:

```sh
python3 build_assets.py              # Rebuild SVG sources and all 12 GIFs
python3 build_assets.py --svg-only   # Rebuild source art without exporting GIFs
python3 build_assets.py --refresh    # Fetch latest public GitHub data, then rebuild
python3 build_assets.py --preview    # Generate .preview/index.html
python3 render_gifs.py --only hero   # Regenerate only the hero
python3 render_gifs.py --renderer cairo  # Force browser-free animation fallback
python3 -m http.server 8768 --bind 127.0.0.1
```

Open `http://127.0.0.1:8768/.preview/index.html` for a quick local preview (the GitHub renderer remains the final authority for layout).

The source SVGs remain available for detailed editing. Rebuilding updates their exported GIF counterparts, which keeps the README visible and animated even when GitHub strips embedded SVG CSS.

## Automatic updates

The GitHub Actions workflow in `.github/workflows/refresh-profile.yml` runs daily at **01:30 UTC** (07:00 India Standard Time), when manually triggered, or on relevant pushes. It installs GIF dependencies, updates `data/github.json`, rebuilds the SVG/GIF assets, and commits the changed data and generated files.

The data fetch checks public repositories and the complete GitHub contribution calendar. It refuses to overwrite the current snapshot when the API response is incomplete or invalid. The contribution city faithfully represents public calendar activity: one tower per day, with taller towers on more active days.

## GitHub profile location

This repository may be named `codmashdev/profile`; its README displays in that repository. GitHub renders a README on the user's **profile overview** only from the public special repository named `codmashdev/codmashdev`. To make this the personal profile page, place these contents in that special repository.

## Useful details

- Keep image paths relative (for example `./assets/hero.gif`) so they work on GitHub.
- The contact-panel artwork is an image, not a clickable form. The badges and linked panels supply the actual click targets.
- All GIFs loop; users with reduced-motion preferences cannot automatically pause them through GitHub README markup.
- GIF export sizes and frame counts can be tuned in `render_gifs.py` for lower bandwidth.
- Font licenses and source/artwork attribution are in `docs/CREDITS.md`.

## Artwork

- `codmash-ninja.png/.webp`: male anime ninja developer with code-bracket forehead protector, orange/charcoal techwear and laptop.
- `codmash-squad.png/.webp`: male CodMash developer and ninja teammate.
- `codmash-torch.png/.webp`: male character with flashlight effect for the stack.
