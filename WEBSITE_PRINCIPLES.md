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

- `content/publication/<slug>/index.md` — articles (`journal_article`), work in review (`under_review`), thesis (`thesis`).
- `content/talk/<slug>/index.md` — first-authored conference presentations (`presentation`); C.V. gives only years, so `date` is Jan 1 and `weight` keeps C.V. order within a year.
- `content/authors/<slug>/_index.md` — one profile per co-author or supervised student (`user_groups`: Students / Collaborators; optional `role`, `website`). `data/people.json` maps each full author name to its slug and short citation form ("Szymanowski D."); the owner entry has `owner: true` (rendered bold, not linked).
- `data/research_areas.json` — the six research areas (key, name, blurb) and subcategories (tag groups used by See Also). Pages opt in with `research_areas: [key, …]`.
- `data/cv.yaml` — structured C.V. sections for the Bio page.
- `tools/` — the one-off generator used for the initial build from the C.V. Do not re-run it (it rewrites content) unless starting over.

## Templates (layouts/)

- `baseof.html` — shell: skip link, navbar, `<main data-pagefind-body>`, footer, search modal.
- `home.html` and `landing/list.html` — homepage: hero (photo left, text right; stacked ≤ 640 px), research-area accordions (`<details>`, 5 recent articles each + "View all" link to the filtered Writings page), recent publications.
- `publication/list.html` — Writings: server-rendered dense list of publications **and** talks (all entries in the HTML), sticky tabs (only tabs with content), sidebar filters (text, area, year), sort, live count, BibTeX export of visible entries, hash state (`#tab?area=…&years=…&q=…&sort=…`, pushState for tab/filter clicks so Back works).
- `_partials/pub_single_body.html` — single page for publications/talks: breadcrumb, full author names (linked to People), venue/date, link buttons, abstract (`#abstract`), See Also. Never shows the internal type label.
- `_partials/related_finder.html` — See Also, computed at build time: explicit `related_*` → `see_also` → Dataverse → subcategory siblings → scoring (+2 title token, +1 co-author, +2 tag; threshold 4, or 2 with < 3 explicit picks), dedup by normalised title, cap 8.
- `_partials/scholarly_meta.html` — `citation_*` tags + `ScholarlyArticle`/`CreativeWork` JSON-LD. `site_head_custom.html` adds the homepage `Person` JSON-LD and the generator meta tag (both gated by `params.mysite.discovery`).
- `authors/list.html` — both the People page (cards grouped Students → Co-authors, by number of joint works) and each person's page (their joint works).
- `robots.txt`, `static/llms.txt`, `home.json` (machine-readable list of works at `/index.json`).

## Design

- Visual model: brandonstewart.org — warm cream background (`#fdfaf4`), banded sections (`#f6efe5`), ink text, burnt-umber accent `#a84b0e` (buttons, active tab, favicon), serif display headings (Charter/Georgia stack) over the native sans body, dark footer.
- ETH blue (`#215caf`) appears only as the link hover colour.
- Dense citation lines, hairline separators, no card grids for writings. Primary actions = filled/outlined buttons; inline navigation = text links with →.
- Always light mode; focus outlines in warm gold; `prefers-reduced-motion` respected.

## Editorial rules

- Homepage intro and Bio narrative must stay different texts.
- No process notes or sourcing commentary on public pages; flags for the owner go in HTML comments.
- Understated tone, shared credit, no superlatives. Author names spelled as on the papers; unverified given names are kept as initials.
- Labels live in `i18n/en.yaml`.

## Known limitations at handover

- No publisher cover images (the build environment could not download them). Drop `featured.jpg` next to an `index.md` to add one.
- Several abstracts are missing because Crossref does not carry them; add `abstract:` by hand where wanted.
- Most co-authors have no verified external link yet.
