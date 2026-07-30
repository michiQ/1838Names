#!/usr/bin/env python3
"""Load the 1838 Black Metropolis blog archive (74 narrative posts) as a source.

Each blog is its own "newspaper": a row in `blogs` carrying the post title, the
live blog URL (View Blog) and the hosted PDF path (View PDF). Every person named
in a post (extracted from the post text, see pipeline/blogs.json) becomes a
`blog_appearances` row (person_id, slug, snippet) so the post surfaces on that
person's card with a story snippet + both links.

Names are resolved to EXISTING people where confident (so a post about Octavius
Catto enriches his existing node); unmatched names are created as source='blog'
people so every named person appears (Michiko: "every name mentioned"). Ambiguous
same-name collisions are NOT auto-linked -- they're written to blog_matches.md for
Michiko to confirm via merges.json, mirroring the ICY/StoryMap review flow.

Runs AFTER apply_merges + the other loaders (so it links to final canonical
nodes) and BEFORE find_merge_candidates/build_viewer. Idempotent: blogs and
blog_appearances are rebuilt each run; existing-person matches re-resolve; new
blog people are reused via get_or_create(name,'blog').
"""
import sqlite3, json, re, unicodedata, os

HERE = os.path.dirname(os.path.abspath(__file__))
DB  = os.environ.get("BM_DB", os.path.join(HERE, "..", "black_metropolis.db"))
SRC = os.environ.get("BLOGS_SRC", os.path.join(HERE, "blogs.json"))

HON = {"mr","mrs","miss","ms","dr","rev","reverend","bishop","gen","general","capt",
       "captain","col","colonel","sir","hon","prof","professor","elder","deacon",
       "father","mother","sister","brother","aunt","uncle","st","madame","mme"}
SUFFIX = {"jr","sr","ii","iii","esq"}

def strip_accents(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()

def toks(name):
    n = strip_accents(name).lower()
    n = re.sub(r"[^a-z ]", " ", n)
    return [t for t in n.split() if t]

def content_toks(name):
    """alpha tokens >1 char, minus honorifics -- the identity-bearing words. Jr/Sr/II/III
    are KEPT: they distinguish father from son (Jacob C. White Sr. vs Jr.) and are exactly
    what makes an otherwise-ambiguous same-name match resolvable."""
    return [t for t in toks(name) if len(t) > 1 and t not in HON]

def okey(name):
    return frozenset(content_toks(name))

def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", strip_accents(s).lower())).strip()

con = sqlite3.connect(DB)
con.execute("""CREATE TABLE IF NOT EXISTS blogs(
    slug TEXT PRIMARY KEY, title TEXT, url TEXT, pdf TEXT)""")
con.execute("""CREATE TABLE IF NOT EXISTS blog_appearances(
    person_id INT, slug TEXT, snippet TEXT)""")
con.execute("DELETE FROM blogs")
con.execute("DELETE FROM blog_appearances")

# ---- build match index over EXISTING (non-blog) people --------------------------
# exact-set index (identity-bearing token set) and a surname+first-given index, each
# mapping key -> list of (pid, canonical_name). Aliases participate too.
exact = {}            # frozenset -> [(pid,name)]
surn_first = {}       # (surname, first_given) -> [(pid,name)]
def parse_forms(name):
    """yield (surname, first_given) guesses for both 'Surname, First' and 'First Last'."""
    if "," in name:
        sur, _, rest = name.partition(",")
        st, rt = content_toks(sur), content_toks(rest)
        if st and rt: yield (st[0], rt[0])
        if st: yield (st[0], st[0])  # mononym-ish guard
    else:
        t = content_toks(name)
        if len(t) >= 2:
            yield (t[-1], t[0])      # First ... Last

for pid, cn, src, al in con.execute(
        "SELECT id, canonical_name, source, aliases FROM people WHERE source IS NOT 'blog'"):
    forms = [cn] + ([a for a in al.split(" | ") if a.strip()] if al else [])
    for f in forms:
        k = okey(f)
        if len(k) >= 2:
            exact.setdefault(k, []).append((pid, cn))
        for sf in parse_forms(f):
            surn_first.setdefault(sf, []).append((pid, cn))

def dedup(cands):
    seen = {}; out = []
    for pid, nm in cands:
        if pid not in seen:
            seen[pid] = 1; out.append((pid, nm))
    return out

def match(name):
    """return ('one', pid) | ('many', [cands]) | ('none', None)."""
    k = okey(name)
    if len(k) >= 2:
        c = dedup(exact.get(k, []))
        if len(c) == 1: return ("one", c[0][0])
        if len(c) > 1:  return ("many", c)
    # surname + first-given fallback (handles 'Westward Keeling' -> 'Keeling, Westward F.')
    cand = []
    for sf in parse_forms(name):
        cand += surn_first.get(sf, [])
    c = dedup(cand)
    if len(c) == 1: return ("one", c[0][0])
    if len(c) > 1:  return ("many", c)
    return ("none", None)

def get_or_create_blog(name):
    r = con.execute("SELECT id FROM people WHERE canonical_name=? AND source='blog'", (name,)).fetchone()
    if r: return r["id"] if False else r[0]
    cur = con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?, 'blog')",
                      (name, norm(name)))
    return cur.lastrowid

# ---- resolve every unique blog name ONCE ---------------------------------------
data = json.load(open(SRC, encoding="utf-8"))
uniq_names = sorted({p["name"] for b in data for p in b["people"]})
resolved = {}          # blog name -> person_id (or None if held for review)
ambiguous = []         # (name, cands)
created = []           # names newly created as blog people
linked = []            # (name, pid, existing_name)
for nm in uniq_names:
    kind, val = match(nm)
    if kind == "one":
        resolved[nm] = val; linked.append(nm)
    elif kind == "many":
        # ambiguous: DON'T auto-pick one of several same-name records. Create a blog node so the
        # post's connection is preserved (not dropped), and surface the candidates so Michiko can
        # merge it into the right one via merges.json -- same as the StoryMap/ICY review flow.
        resolved[nm] = get_or_create_blog(nm); ambiguous.append((nm, val))
    else:
        resolved[nm] = get_or_create_blog(nm); created.append(nm)

# ---- register blogs + appearances ----------------------------------------------
n_app = 0
for b in data:
    con.execute("INSERT OR REPLACE INTO blogs(slug,title,url,pdf) VALUES(?,?,?,?)",
                (b["slug"], b.get("title"), b.get("blog_url"), b.get("pdf")))
    seen = set()
    for p in b["people"]:
        pid = resolved.get(p["name"])
        if pid is None or pid in seen:   # skip held-for-review names + per-blog dupes
            continue
        seen.add(pid)
        con.execute("INSERT INTO blog_appearances(person_id, slug, snippet) VALUES(?,?,?)",
                    (pid, b["slug"], p.get("snippet", "")))
        n_app += 1
# drop orphaned blog people from earlier runs -- names since removed from blogs.json (e.g. the
# one-word mentions Michiko pruned) leave a source='blog' row with no remaining blog_appearance.
con.execute("DELETE FROM people WHERE source='blog' AND id NOT IN (SELECT person_id FROM blog_appearances)")
con.commit()

# ---- review file ---------------------------------------------------------------
lines = ["# Blog archive -- name matches to confirm", "",
         f"{len(data)} posts loaded. Of {len(uniq_names)} unique names: "
         f"{len(linked)} linked to existing people, {len(created)} created as new blog people, "
         f"{len(ambiguous)} held as ambiguous (NOT linked -- confirm below).", "",
         "## Ambiguous (same name as MORE THAN ONE existing record -- not auto-linked)",
         "Add a group to merges.json (id-qualified) to attach the blog mentions to the right one:", ""]
for nm, cands in ambiguous:
    lines.append(f"- **{nm}** (blog)  ↔  " + ", ".join(f"{cn}#{pid}" for pid, cn in cands))
lines += ["", "## Newly created as blog-only people (review: merge variants / delete non-subjects)",
          "e.g. honorific/nickname variants of existing people, or national/modern figures to prune.", ""]
for nm in created:
    lines.append(f"- {nm}")
open(os.path.join(HERE, "blog_matches.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

print(f"blogs: {len(data)} posts, {n_app} person-appearances | "
      f"{len(linked)} linked to existing, {len(created)} new blog people, "
      f"{len(ambiguous)} ambiguous held -> blog_matches.md")
