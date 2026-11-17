# garyseid.com

Gary Seid's real estate website — The Blu Group, powered by Keller Williams Marquee.
Deployed on Netlify at https://www.garyseid.com (blustl.com redirects here).

## How deploys work

Netlify is linked to this repository. **Every push to `main` triggers a production
deploy** (~15 Netlify credits each), so batch changes into as few pushes as possible.

- `/site` — the built website, published as-is (no build command on Netlify)
- `/netlify/functions/links.mjs` — the short-link service (`/s/<name>` redirects,
  `/api/links` admin API used by the `/links/` page). Requires the `LINKS_KEY`
  environment variable in Netlify (already set).
- `/netlify.toml` — Netlify config: publish dir, functions dir, headers
- `/src` — sources: `template.html` (master), `build.py` (single-file version),
  `build_netlify.py` (builds the multi-page site), images, and
  `fnbuild/links.src.mjs` (unbundled function source)

## Rebuilding the site after editing the template

```sh
cd src
python3 build.py              # single-file gary-seid-site.html + preview.html
mkdir -p fnbuild && cp ../netlify/functions/links.mjs fnbuild/links.mjs
python3 build_netlify.py      # outputs netlify/garyseid-site/
rm -rf ../site && cp -r netlify/garyseid-site ../site
rm -rf ../site/netlify ../site/netlify.toml   # function + toml live at repo root
```

## Rebundling the function after editing `src/fnbuild/links.src.mjs`

```sh
cd src/fnbuild
npm i esbuild @netlify/blobs
npx esbuild links.src.mjs --bundle --format=esm --platform=node --target=node18 --outfile=../../netlify/functions/links.mjs
```

Short links are stored in Netlify Blobs (store `shortlinks`) — creating one at
https://www.garyseid.com/links/ needs no redeploy.
