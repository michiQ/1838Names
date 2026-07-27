#!/usr/bin/env python3
"""Load appearances in William Still's *The Underground Rail Road* (Philadelphia, 1872)
onto matching people, plus create the freedom-seekers / aiders named in the book who are
not yet in the database.

Source file: pipeline/ugrr_appearances.json  (one entry per person-per-chapter).
Each entry: {"find": {...}, "chapter": "<TOC chapter title>", "page": <TOC page of that chapter>}
  find is resolved the same way as load_nolibs.py:
    {"name": "Ash, Sarah", "source": "winch"}  -> existing curated person (stable id)
    {"create": {"name": "Tubman, Harriet", "source": "ugrr"}}  -> new person
  optional "q": explicit Internet-Archive search term (defaults to the person's surname)

The viewer link points at the *chapter's* page in the online scan. Internet Archive's
reader has two front-matter leaves, so the book's printed page N is leaf N+2 there; the
?q=<surname> makes the name highlight on the page. Example (Sarah Ash, "Woman Escaping in
a Box", book p.608):
  https://archive.org/details/undergroundrailr00lcstil/page/610/mode/1up?q=ash

Runs AFTER load_nolibs (so all merges/renames are final) and BEFORE
find_merge_candidates / build_viewer. Idempotent: rebuilds the ugrr_appearances table
from scratch every run and re-resolves every person by canonical name + source.
"""
import sqlite3, json, re, unicodedata, os, sys

DB  = os.environ.get("BM_DB", "/tmp/run_ugrr/black_metropolis.db")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("UGRR_SRC", os.path.join(HERE, "ugrr_appearances.json"))
ARCHIVE_ID = "undergroundrailr00lcstil"
FRONT_MATTER_OFFSET = 2   # printed page N -> Internet Archive leaf N+2

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()

def surname(name):
    """'Ash, Sarah' -> 'Ash'; 'Harriet Tubman' -> 'Tubman'."""
    if "," in name:
        return name.split(",", 1)[0].strip()
    return name.strip().split()[-1] if name.strip() else ""

def q_term(name, override):
    if override:
        return override
    # lower-case, letters only -- what archive.org's ?q= expects
    return re.sub(r"[^a-z]", "", surname(name).lower())

def archive_url(page, q):
    leaf = int(page) + FRONT_MATTER_OFFSET
    frag = f"?q={q}" if q else ""
    return f"https://archive.org/details/{ARCHIVE_ID}/page/{leaf}/mode/1up{frag}"

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
con.execute("CREATE TABLE IF NOT EXISTS ugrr_appearances("
            "person_id INT, chapter TEXT, page INT, url TEXT)")
con.execute("DELETE FROM ugrr_appearances")

def get_or_create(name, source):
    r = con.execute("SELECT id FROM people WHERE canonical_name=? AND source=?",
                    (name, source)).fetchone()
    if r:
        return r["id"]
    cur = con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?,?)",
                      (name, norm(name), source))
    return cur.lastrowid

def resolve(find):
    if "create" in find:
        return [get_or_create(find["create"]["name"], find["create"].get("source", "ugrr"))]
    if "name" in find:
        if find.get("source"):
            rs = con.execute("SELECT id FROM people WHERE canonical_name=? AND source=?",
                             (find["name"], find["source"])).fetchall()
        else:
            rs = con.execute("SELECT id FROM people WHERE canonical_name=?",
                             (find["name"],)).fetchall()
        return [r["id"] for r in rs]
    return []

data = json.load(open(SRC, encoding="utf-8"))
ok = amb = miss = created = 0
seen_created = set()
for e in data["appearances"]:
    find = e["find"]
    pids = resolve(find)
    label = json.dumps(find, ensure_ascii=False)
    if not pids:
        print("  MISS:", label); miss += 1; continue
    if len(pids) > 1:
        print(f"  AMBIG ({len(pids)}): {label} -> {pids} (using first)"); amb += 1
    pid = pids[0]
    if "create" in find and find["create"]["name"] not in seen_created:
        seen_created.add(find["create"]["name"]); created += 1
    # name used for the archive.org ?q= highlight
    disp_name = find.get("create", {}).get("name") or find.get("name") or ""
    q = q_term(disp_name, e.get("q"))
    url = archive_url(e["page"], q)
    con.execute("INSERT INTO ugrr_appearances(person_id, chapter, page, url) VALUES(?,?,?,?)",
                (pid, e["chapter"], int(e["page"]), url))
    ok += 1

con.commit()
n_people = con.execute("SELECT COUNT(DISTINCT person_id) FROM ugrr_appearances").fetchone()[0]
print(f"ugrr_appearances: {ok} appearances across {n_people} people "
      f"({created} newly created), {amb} ambiguous, {miss} unresolved")
