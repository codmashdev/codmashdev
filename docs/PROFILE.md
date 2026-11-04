# Codmash profile maintenance

The README follows the supplied anime profile reference: hero, Team 7 dance, ninja philosophy, torch-lit technology grid, swinging studio ID, portfolio, contribution village, contact panel and walking sign-off. The male Codmash lead uses original generated artwork.

All fonts, artwork, badges and GIFs are local. Each panel embeds its own fonts and raster artwork so GitHub can render it as an `<img>` without JavaScript, iframe support, external CSS, or an image-generation service. SVG CSS/SMIL supplies the entrance effects, role cycling, glowing chips, particles, card sway and contact highlights. The hero character gently floats; it is an animated illustration, not a frame-by-frame character video. The three chibi GIFs provide character animation.

## Rebuild

```sh
python3 build_assets.py
python3 build_assets.py --refresh
python3 build_assets.py --preview
python3 -m http.server 8768 --bind 127.0.0.1
```

Open `http://127.0.0.1:8768/.preview/index.html` for the local README preview. Edit `templates/*.svg` for layout/copy and `build_assets.py` for data cards or the contribution city, then rebuild. Generated `assets/*.svg` are the files GitHub displays.

`data/github.json` is a checked-in snapshot of public `codmashdev` data. Counts are real; the city includes one block per calendar day and only raises buildings for days with contributions. A failed or incomplete fetch aborts before replacing the snapshot. The GitHub Actions workflow refreshes daily at 01:30 UTC (07:00 India time), on relevant pushes, or through **Run workflow** once these files are pushed and Actions is enabled. It uses the repository's built-in token and Python's standard library.

The repository is currently named `codmashdev/profile`. Its README displays on that repository. For GitHub's personal profile overview, the special public repository must be named `codmashdev/codmashdev`; copy these files there if that is the intended destination. Publishing this README does not rename the repository.

The contact cards inside an SVG image are visual; the HTML image links and five badges beneath the contact panel are the actual clickable targets. Core profile content has descriptive alt text. SVG CSS respects reduced-motion preferences; GIFs and some SMIL effects still animate.

## Artwork prompts

Generated with the built-in imagegen tool, then copied into this repository. The WebP exports are used by the panels; the PNG files preserve the original generation results.

- `assets/codmash-ninja.png`: Adult male anime ninja developer, spiky black hair, warm brown skin, amber eyes, code-bracket forehead protector, orange/charcoal techwear; peace sign beside his face, seated behind a code-branded laptop; crisp professional cel shading, orange and blue rim light, transparent background.
- `assets/codmash-squad.png`: The Codmash male lead and Naruto standing back to back, arms crossed and thumbs-up poses, head-to-mid-thigh framing, matching orange/charcoal anime illustration, transparent background.
- `assets/codmash-torch.png`: The Codmash male lead faces right, extending a flashlight at chest level, other hand in pocket; detailed cel shading, orange and blue rim light, transparent background; SVG adds the light beam.
