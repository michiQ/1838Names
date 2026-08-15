#!/usr/bin/env python3
"""Split the over-grouped Samuel Williams census person (Michiko, 2026-08-14).

The census import groups same-name rows into one person, which lumped five
distinct households under one Samuel Williams. Michiko's ruling: it's a very
common name -- every record is its own individual EXCEPT the 235 S. 7th &
29 Washington porter-house keeper (1847 row 724), who is the Boyer House
Tavern owner (Mob Attack Statistics m07/m61) and William Still's Samuel
Williams (UGRR p.126), all kept on the one merged record (merges.json group,
keep id 351596).

Splits off, each as its own source='census' person:
  1838 row 3167  (PINE AB QUINCE, Ward 7, porter)
  1847 row 2482  (4 Guilelmina, porter)
  1847 row 3967  (158 Queen Street, public porter)
  1847 row 3968  (Cedar Street, refectory)
(Verified 2026-08-14: none of these appear in census_matches.)

Idempotent: only repoints a census_link if it currently points at the person
who also holds the 1847-724 link; already-split links are left alone. Runs
with the other split fixes BEFORE apply_merges.
"""
import sqlite3, os, re, unicodedata

DB = os.environ.get("BM_DB", "/tmp/black_metropolis.db")

SPLITS = [  # (census, row_id, canonical_name for the new person)
    ("1838", 3167, "WILLIAMS, SAMUEL"),
    ("1847", 2482, "Williams, Samuel"),
    ("1847", 3967, "Williams, Samuel"),
    ("1847", 3968, "Williams, Samuel"),
]
KEEP_ROW = ("1847", 724)

def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()

con = sqlite3.connect(DB)
keep = con.execute("SELECT person_id FROM census_links WHERE census=? AND row_id=?",
                   KEEP_ROW).fetchone()
if not keep:
    print("split_swilliams: keep row 1847/724 not linked -- no-op"); raise SystemExit
keep_pid = keep[0]

n = 0
for census, row_id, name in SPLITS:
    cur = con.execute("SELECT person_id FROM census_links WHERE census=? AND row_id=?",
                      (census, row_id)).fetchone()
    if not cur or cur[0] != keep_pid:
        continue  # already split (or points elsewhere) -- leave alone
    new_pid = con.execute(
        "INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?,'census')",
        (name, norm(name))).lastrowid
    con.execute("UPDATE census_links SET person_id=? WHERE census=? AND row_id=?",
                (new_pid, census, row_id))
    n += 1
    print(f"  split {census} row {row_id} -> new person #{new_pid} ({name})")
con.commit()
print(f"split_swilliams: {n} household(s) split off; kept 1847/724 on person #{keep_pid}")
