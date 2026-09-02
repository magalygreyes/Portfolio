# Magaly Gonzalez Reyes — Portfolio

Single-page static portfolio. No build step, no framework.

## Files

- `index.html`  the whole site (HTML + CSS + ~30 lines of JS)
- `assets/favicon.svg`  MG monogram, cobalt on ice
- `assets/og-image.png`  1200×630 share image for LinkedIn / Slack / iMessage previews
- `resume/`  drop the résumé PDF here (see To do)
- `netlify.toml`  publish config + security headers

## Run locally

Double-click `index.html`, or from this folder run `python -m http.server 8000` and open http://localhost:8000.

## Deploy (Netlify)

1. Netlify dashboard → Add new site → Deploy manually → drag this whole folder in.
2. Or connect the GitHub repo: build command empty, publish directory `.`
3. After the first deploy, set the real site URL in `index.html`: search for `magalygonzalezreyes.netlify.app` and replace all 6 occurrences (canonical, OG, JSON-LD).

## To do before sharing the link

- [ ] **LinkedIn URL.** Search `index.html` for `YOUR-HANDLE` (3 places) and replace with the real handle.
- [ ] **Résumé PDF.** Export the .docx as PDF and save it as `resume/Magaly-Gonzalez-Reyes-Business-Analyst.pdf`. All three "Download résumé" buttons already point there.
- [ ] **Headshot.** Replace the hero placeholder with `<img src="assets/headshot.jpg" alt="Magaly Gonzalez Reyes">` inside the `.headshot` div, 4:5 ratio (e.g. 800×1000).
- [ ] **Project images (4).** 16:10, e.g. 1600×1000. Put an `<img>` inside each card's `.slot` and delete the caption chip.
- [ ] **Case-study images (4).** A: 4:3 before/after + 16:9 Power Automate flow. B: 4:3 process map + 16:9 dashboard.
- [ ] Scrub client-identifying data (names, matter numbers, patient data) from every screenshot before publishing.

## Adding an image to a placeholder

Before:
```html
<div class="slot" role="img" aria-label="..."><span class="cap">Dashboard · 16:10</span></div>
```
After:
```html
<div class="slot"><img src="assets/kp-dashboard.png" alt="Self-service operations dashboard built in SharePoint" loading="lazy"></div>
```
The striped background disappears automatically once the image covers it.

## Spec

Built from `portfolio-build-spec.md` in this folder. Tokens, layout, copy and behavior follow it verbatim.
