#!/usr/bin/env python3
"""Generate Hugo content + data files for Dawid Szymanowski's site from pubs_data / talks_data.
Run once for the initial build; afterwards content is edited directly as Markdown.
WARNING: re-running DELETES content/publication, content/talk and content/authors and rebuilds them.
Usage: python3 tools/gen.py --force"""
import json, re, os, unicodedata, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from pubs_data import PUBS, THESIS, UNDER_REVIEW
from talks_data import TALKS

SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OWNER = "Dawid Szymanowski"
C = os.path.join(SITE, "content")
D = os.path.join(SITE, "data")

STOP = set("a an and the of for in on to with by at as is are be or from into using via new not no it its we our their you your this that these those but if than then so can will would could should may might also more most some all any each every who whom which what when where why how about between among through over under after before upon across per vs de la les et du".split())

def ascii_fold(s):
    s = s.replace("–", " ").replace("—", " ").replace("µ", "micro").replace("ł", "l").replace("Ł", "L").replace("ß", "ss").replace("’", "").replace("'", "")
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()

def slugify(title, maxw=8):
    t = ascii_fold(title).lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    words = [w for w in t.split() if w not in STOP]
    return "-".join(words[:maxw])

def name_slug(name):
    return re.sub(r"[^a-z0-9]+", "-", ascii_fold(name).lower()).strip("-")

# family-name handling for short citation names
PARTICLES = {"von", "van", "de", "der", "den", "du", "da"}
FAMILY_OVERRIDES = {
    "Caroline Bouvet de Maisonneuve": ("Bouvet de Maisonneuve", "Caroline"),
    "Antomat A. Macêdo Filho": ("Macêdo Filho", "Antomat A."),
    "M. P. Castellanos Melendez": ("Castellanos Melendez", "M. P."),
    "Chutimun Chanmuang N.": ("Chanmuang N.", "Chutimun"),
    "Mário Neto Cavalcanti de Araújo": ("Cavalcanti de Araújo", "Mário Neto"),
    "EARTHTIME U-Pb ID-TIMS Working Group": ("EARTHTIME U-Pb ID-TIMS Working Group", ""),
    "R. Bastian Georg": ("Georg", "R. Bastian"),
    "C. Brenhin Keller": ("Keller", "C. Brenhin"),
    "C. Forrest Town": ("Town", "C. Forrest"),
    "Maria Helena Hollanda": ("Hollanda", "Maria Helena"),
}
def split_name(n):
    if n in FAMILY_OVERRIDES: return FAMILY_OVERRIDES[n]
    parts = n.split()
    i = len(parts) - 1
    while i > 0 and parts[i-1].lower() in PARTICLES: i -= 1
    return " ".join(parts[i:]), " ".join(parts[:i])

def initials(given):
    out = []
    for tok in given.split():
        if "-" in tok.strip("."):
            out.append("-".join(x[0] + "." for x in tok.split("-") if x))
        else:
            out.append(tok[0] + ".")
    return "".join(o if o.endswith(".") else o for o in out)

def short(n):
    fam, giv = split_name(n)
    if not giv: return fam
    return f"{fam} {initials(giv)}"

def yq(s):
    """YAML-safe double-quoted string."""
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'

def ylist(xs):
    return "[" + ", ".join(yq(x) for x in xs) + "]"

def venue(p):
    v = p.get("journal", "")
    if p.get("vol"): v += f" {p['vol']}"
    if p.get("issue"): v += f"({p['issue']})"
    if p.get("pages"): v += (", " if p.get("vol") else " ") + p["pages"]
    return v

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f: f.write(text)

if "--force" not in sys.argv:
    sys.exit("Refusing to overwrite content without --force (see docstring).")
# reset generated sections
for sec in ["publication", "talk", "authors"]:
    shutil.rmtree(os.path.join(C, sec), ignore_errors=True)

all_people = {}   # name -> count
used = set()
def uniq(slug):
    s = slug; k = 2
    while s in used: s = f"{slug}-{k}"; k += 1
    used.add(s); return s

AREA_TAGS = {"magma": "magma reservoirs", "methods": "geochronology methods", "refmat": "reference materials",
             "lip": "Earth history", "ore": "ore deposits", "moon": "planetary science"}

def pub_md(p, slug, ptype, venue_str, date, weight=None):
    fm = ["---", f"title: {yq(p['title'])}", f"date: {date}", f"authors: {ylist(p['authors'])}",
          f"publication_types: [{yq(ptype)}]", f"publication: {yq(venue_str)}"]
    if p.get("doi"): fm.append(f"doi: {yq(p['doi'])}")
    if p.get("abstract"): fm.append(f"abstract: {yq(p['abstract'])}")
    links = []
    if p.get("doi"):
        links.append(("Preprint" if p.get("status") == "under_review" else "Publisher's Version", "https://doi.org/" + p["doi"]))
    for name, url in p.get("press", []):
        links.append((name, url))
    if links:
        fm.append("links:")
        for name, url in links:
            fm.append(f"  - name: {yq(name)}\n    url: {yq(url)}")
    if p.get("notes"): fm.append(f"author_notes: {yq(p['notes'])}")
    fm.append(f"research_areas: {ylist(p.get('areas', []))}")
    fm.append(f"tags: {ylist(p.get('tags', []))}")
    if p.get("status"): fm.append(f"status: {p['status']}")
    if weight is not None: fm.append(f"weight: {weight}")
    fm.append("---\n")
    return "\n".join(fm)

# ---- publications ----
legacy = {}
for p in PUBS:
    slug = uniq(slugify(p["title"]))
    v = venue(p)
    write(f"{C}/publication/{slug}/index.md", pub_md(p, slug, "journal_article", v, p["date"]))
    for a in p["authors"]: all_people[a] = all_people.get(a, 0) + 1


for i, p in enumerate([q for q in UNDER_REVIEW if q.get("doi")]):
    slug = uniq(p["slug"])
    q = dict(p); q["status"] = "under_review"
    write(f"{C}/publication/{slug}/index.md", pub_md(q, slug, "under_review", p["venue"], p.get("date", "2026-09-01")))
    for a in p["authors"]: all_people[a] = all_people.get(a, 0) + 1

write(f"{C}/publication/_index.md", """---
title: "Writings"
---
""")

used.clear()
# ---- talks (first-authored presentations from the C.V.; CV gives year only) ----
n = len(TALKS)
for i, (date, title, authors, event, invited, areas) in enumerate([]):
    slug = uniq(slugify(title))
    year = date[:4]
    fm = ["---", f"title: {yq(title)}", f"date: {year}-01-01", f"authors: {ylist(authors)}",
          'publication_types: ["presentation"]', f"publication: {yq(event)}", f"event: {yq(event)}",
          f"invited: {'true' if invited else 'false'}", f"research_areas: {ylist(areas)}",
          f"tags: {ylist([AREA_TAGS[a] for a in areas])}", f"weight: {i+1}", "---\n"]
    write(f"{C}/talk/{slug}/index.md", "\n".join(fm))
    for a in authors: all_people[a] = all_people.get(a, 0) + 1



# ---- people ----
STUDENTS = [  # from the C.V. "Teaching and supervision" section
    ("Travis Steiner-Leach", "PhD project, Princeton University (since 2019)"),
    ("Liam O’Connor", "Senior thesis, Princeton University (2019–2020)"),
    ("Gabriel Rojas", "MSc thesis, ETH Zürich"),
    ("Marco Hunziker", "MSc thesis, ETH Zürich"),
    ("Joelle Marbach", "MSc thesis, ETH Zürich"),
    ("Josefine Koefoed", "MSc thesis (co-supervised), ETH Zürich"),
]
ALIASES = {"G. Rojas": "Gabriel Rojas"}
for a, b in ALIASES.items():
    if a in all_people:
        all_people[b] = all_people.get(b, 0) + all_people.pop(a)

# External links: resolved by web search (website > university page > LinkedIn). Unverified names stay unlinked.
LINKS = {
    "Olivier Bachmann": "https://geopetro.ethz.ch/people/profile.olivier-bachmann.html",
    "Ben S. Ellis": "https://geopetro.ethz.ch/people/person-detail.html?persid=190551",
    "Marcel Guillong": "https://erdw.ethz.ch/en/people/profile.NjI5ODI=.TGlzdC83NzMsOTI0MjA1OTI2.html",
    "Jörn-Frederik Wotzlaw": "https://erdw.ethz.ch/en/people/profile.MjE0NTg2.TGlzdC83NzMsOTI0MjA1OTI2.html",
    "Blair Schoene": "https://geosciences.princeton.edu/people/blair-schoene",
    "Cyril Chelle-Michou": "https://mineralsystems.ethz.ch/people.html",
    "Francesca Forni": "https://www.unimi.it/en/ugov/person/francesca-forni",
    "Urs Schaltegger": "https://www.unige.ch/sciences/terre/en/people/personals-pages/urs-schaltegger",
    "Maria Ovtcharova": "https://www.linkedin.com/in/maria-ovtcharova-4861773a/",
}

people_data = {}
student_names = [s for s, _ in STUDENTS]
all_people.pop(OWNER, None)
write(f"{C}/authors/_index.md", """---
title: "People"
summary: "Dawid’s research is highly collaborative. These are the students he has supervised and the colleagues he has published with."
---
""")
for name in sorted(set(list(all_people) + student_names), key=lambda x: ascii_fold(split_name(x)[0]).lower()):
    if name.startswith("EARTHTIME"):
        grp = "Collaborators"
    grp = "Students" if name in student_names else "Collaborators"
    slug = name_slug(name)
    role = dict(STUDENTS).get(name, "")
    fm = ["---", f"title: {yq(name)}", f"short_name: {yq(short(name))}", f"user_groups: [{yq(grp)}]",
          "superuser: false", f"joint_works: {all_people.get(name, 0)}"]
    if role: fm.append(f"role: {yq(role)}")
    if name in LINKS: fm.append(f"website: {yq(LINKS[name])}")
    fm.append("---\n")
    body = ""
    if name not in LINKS and not name.startswith("EARTHTIME"):
        body = "<!-- No external page verified for this person; add `website:` above if you know it. -->\n"
    write(f"{C}/authors/{slug}/_index.md", "\n".join(fm) + body)
    people_data[name] = {"slug": slug, "short": short(name)}

people_data[OWNER] = {"slug": "", "short": short(OWNER), "owner": True}
for a, b in ALIASES.items():
    people_data[a] = people_data[b]
os.makedirs(D, exist_ok=True)
json.dump(people_data, open(f"{D}/people.json", "w"), ensure_ascii=False, indent=1)
json.dump({k: {"url": v, "type": "university" if "linkedin" not in v else "linkedin"} for k, v in LINKS.items()},
          open(f"{D}/coauthors.json", "w"), ensure_ascii=False, indent=1)
print("pubs", len(PUBS), "talks", len(TALKS), "people", len(people_data))
