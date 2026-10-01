# Website principles and architecture

A playbook for anyone (human or AI) maintaining this site. Read before changing templates.

## Stack

- **Hugo extended ≥ 0.148.2** (CI pins 0.152.2). Static output only.
- **Hugo Blox `blox-tailwind` v0.10.0**, imported as a Go module and vendored in `_vendor/` (committed, so builds are hermetic; `go.sum` is committed too). Every page type used by this site is rendered by project templates in `layouts/`, which take precedence over Blox's; Blox is kept as the module base so its partials stay available to copy from (`_vendor/.../layouts/_partials/…` → `layouts/_partials/…`; note `_partials`, not `partials`).
- **Styling**: one stylesheet, `assets/css/custom.css`, with colour tokens on `:root`. No Tailwind build step is needed for the project templates.
- **Search**: Pagefind, indexed in CI after Hugo (`npx pagefind --site public`). The modal (`layouts/_partials/components/search-modal.html`) loads `pagefind/pagefind.js` through `relURL` (no leading slash) on first open, supports Ctrl/⌘-K, arrow keys and Esc, and falls back to a Google `site:` search.
- **Hosting**: GitHub Pages via `.github/workflows/deploy.yml` on every push to `main`.

## URLs

- `baseURL` in `hugo.yaml` is the final `https://` address and must end in `/`. It is **not** overridden from CI, so canonical links, `og:url` and the sitemap always use https.
- Never write a literal leading `/` in templates or content: use `{{ "path/" | relURL }}` in templates, `{{</* staticrel "files/x.pdf" */>}}` in Markdown, and `files/x.pdf` (no slash) in front-matter `links`.
- Content folder name = permanent slug (`permalinks: :contentbasename`). Never rename a folder once live; change `title:` instead. Use `aliases:` for extra short URLs.

## Content model

- `content/publication/<slug>/index.md` — articles (`journal_article`) and preprints under review (`under_review`). Work under review without a public preprint, the thesis and conference presentations are deliberately not listed.
- `data/people.json` maps each full author name to its short citation form and BibTeX family name; the owner entry has `owner: true` (rendered bold).
- `data/research_areas.json` — the six research areas (key, name, blurb) and subcategories (tag groups used by See Also). Pages opt in with `research_areas: [key, …]`.
- `tools/` — the one-off generator used for the initial build from the C.V. Do not re-run it (it rewrites content) unless starting over.

## Templates (layouts/)

- `baseof.html` — shell: skip link, navbar, `<main data-pagefind-body>`, footer, search modal.
- `home.html` and `landing/list.html` — homepage: hero (photo left, text right; stacked ≤ 640 px), recent publications.
- `publication/list.html` — Publications page: server-rendered dense list of publications (and talks, if a `content/talk/` section is ever added) (all entries in the HTML), sticky tabs (only tabs with content), sidebar filters (text, area, year), sort, live count, BibTeX export of visible entries, hash state (`#tab?area=…&years=…&q=…&sort=…`, pushState for tab/filter clicks so Back works).
- `_partials/pub_single_body.html` — single page for publications/talks: breadcrumb, full author names, venue/date, link buttons, abstract (`#abstract`), See Also. Never shows the internal type label.
- `_partials/related_finder.html` — See Also, computed at build time: explicit `related_*` → `see_also` → Dataverse → subcategory siblings → scoring (+2 title token, +1 co-author, +2 tag; threshold 4, or 2 with < 3 explicit picks), dedup by normalised title, cap 8.
- `_partials/scholarly_meta.html` — `citation_*` tags + `ScholarlyArticle`/`CreativeWork` JSON-LD. `site_head_custom.html` adds the homepage `Person` JSON-LD and the generator meta tag (both gated by `params.mysite.discovery`).
- `robots.txt`, `static/llms.txt`, `home.json` (machine-readable list of works at `/index.json`).

## Design

- Layout modelled on brandonstewart.org. Colour scheme: white background (`#ffffff`), light blue-grey bands and sidebar (`#f3f6fa`), ink text, ETH blue accent `#215caf` (links, buttons, active tab, journal names, favicon), serif display headings (Charter/Georgia stack) over the native sans body, navy footer (`#14213a`).
- All colours are tokens on `:root` at the top of `assets/css/custom.css`; change the scheme there. The favicon PNG/ICO files in `static/` use the accent colour and need regenerating if it changes.
- Dense citation lines, hairline separators, no card grids for writings. Primary actions = filled/outlined buttons; inline navigation = text links with →.
- Always light mode; focus outlines in light blue; `prefers-reduced-motion` respected.

## Editorial rules

- Homepage intro and Bio narrative must stay different texts.
- No process notes or sourcing commentary on public pages; flags for the owner go in HTML comments.
- Understated tone, shared credit, no superlatives. Author names spelled as on the papers; unverified given names are kept as initials.
- Labels live in `i18n/en.yaml`.

## Known limitations at handover

- No publisher cover images (the build environment could not download them). Drop `featured.jpg` next to an `index.md` to add one.
- Abstracts that Crossref does not carry were added by hand from the publisher pages (kept in `tools/abstracts_extra.py` for the record). Isotope mass numbers, km², km³ and common oxides in abstracts are written with Unicode super/subscripts because abstracts are rendered as plain text.
