# Updating your website

Everything on the site is plain text in this repository. Edit a file on GitHub (open it, click the pencil icon, change it, "Commit changes"), and the site rebuilds and goes live by itself about two minutes later. You never need to install anything.

## Where things live

| To change… | Edit this |
|---|---|
| Homepage intro (the short paragraph under your name) | `content/_index.md` → the `intro:` line |
| Bio narrative | `content/bio/index.md` |
| Photo | replace `static/images/dawid-szymanowski.jpg` (square, ~640×640) |
| Email, title, ORCID, Scholar, postal address | `hugo.yaml` → `params.owner` |
| Keyword list (filter order) | `data/keywords.json` |
| Menu items | `hugo.yaml` → `menu.main` |
| Button and label wording | `i18n/en.yaml` |

## Add a paper

1. In `content/publication/`, create a new folder named with a short, lowercase, hyphenated slug, e.g. `lipari-rhyolite-melt-production`. **The folder name becomes the permanent URL — never rename it later.**
2. Inside it, create `index.md` and copy this template:

```yaml
---
title: "Evolution of rhyolite melt production on Lipari"
date: 2027-03-15
authors: ["Dawid Szymanowski", "Francesca Forni", "Gabriel Rojas", "Olivier Bachmann"]
publication_types: ["journal_article"]     # or "under_review" (preprints)
publication: "Journal of Petrology 68, egaa001"
doi: "10.1093/petrology/egaa001"
abstract: "Paste the abstract here."
links:
  - name: "Publisher's Version"
    url: "https://doi.org/10.1093/petrology/egaa001"
research_areas: ["magma"]                  # magma, methods, refmat, lip, ore, moon
tags: ["Lipari", "rhyolite", "zircon"]
keywords: ["Zircon", "ID-TIMS", "Magma reservoir"]   # pick from the list in data/keywords.json; add new ones there
---
```

3. Commit. The paper appears on the Publications page, the homepage (if recent), the matching research area, and "See also" links are worked out automatically.

Tips:
- Write author names exactly as they appear on other papers (e.g. "Ben S. Ellis", "Jörn-Frederik Wotzlaw") so they link to the same person.
- A preprint under review: use `publication_types: ["under_review"]`, set `publication: "In review at Geology (preprint on EGUsphere)"`, and link the preprint DOI with `name: "Preprint"`. When it is published, change the type to `journal_article` and fill in the venue and DOI — keep the same folder.
- To host a PDF yourself, put it in `static/files/` and add a link with `url: "files/your-file.pdf"` (no leading slash).
- To force particular "See also" entries, add `related_papers: ["folder-name-of-other-paper"]`.

## Preview before publishing (optional)

If you install [Hugo extended](https://gohugo.io/installation/) (version 0.148.2 or newer) you can preview locally:

```
hugo server
```

then open the address it prints. Search only works in a full build (`hugo && npx pagefind --site public`).

## Footer credit and invisible marker

`hugo.yaml` → `params.mysite`: `credit: false` hides the "Created using GaryKing.org/mysite" footer line (currently hidden, as you chose); `discovery: true` keeps an invisible `<meta name="generator">` tag and structured data that help search engines (currently on, as you chose).
