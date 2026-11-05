"""Import the 1811 Philadelphia city directory's "Directory of Coloured Persons" (printed pp. 366-385;
Internet Archive item philadelphiadire1811phil, PDF pp. 372-391) as its own source (added 2026-11-04,
Michiko; transcribed from the page images into pipeline/1811_directory_source.csv, same columns as the
1820 file plus Printed Page).

Same rules as import_1820_directory.py: every row is its own record (no deduping by name); a row links to
a Winch person only when exactly one Winch person (canonical name or confirmed alias) has that given name
+ surname; otherwise it becomes a new person with source='1811directory'. Never auto-merges.

Differences from the 1820 script, on purpose:
- It does NOT drop directory_links (that would wipe the 1820 rows); it deletes and rewrites only its own
  rows (directory='1811') and its own people, so it is safe to run on every rebuild.
- 1811directory people are kept OUT of the other loaders' automatic name matching (match_names,
  load_extractions, load_blogs, load_mobstats, load_ugrr, load_nolibs), like the coppin/storymap
  sources, so adding ~700 'Surname, Given' records cannot make existing matches ambiguous. Possible
  duplicates surface in find_merge_candidates for review instead.
Run FIRST in the rebuild chain (before match_names)."""
import os, sqlite3, re, unicodedata
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get("BM_DB", "/tmp/black_metropolis.db")
CSV = os.path.join(HERE, "1811_directory_source.csv")

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()

def parse_any(name):
    name = re.sub(r"\(.*?\)", "", name or "").strip()
    if not name: return None
    if "," in name:
        sur, given = [x.strip() for x in name.split(",", 1)]
    else:
        toks = name.split()
        if len(toks) < 2: return None
        sur, given = toks[-1], " ".join(toks[:-1])
    g1 = given.split()[0] if given.split() else ""
    return (sur, g1) if g1 and sur else None

con = sqlite3.connect(DB)
df = pd.read_csv(CSV, dtype=str, keep_default_na=False)
df.columns = [re.sub(r"\W+", "_", c.strip()).strip("_").lower() for c in df.columns]
df.to_sql("directory_1811", con, if_exists="replace", index_label="rowid_")

pidx = {}
for pid, name, aliases in con.execute("SELECT id, canonical_name, aliases FROM people WHERE source='winch'"):
    for v in [name] + [a for a in (aliases or "").split(" | ") if a]:
        pa = parse_any(v)
        if pa: pidx.setdefault(norm(f"{pa[1]} {pa[0]}"), set()).add(pid)

con.execute("CREATE TABLE IF NOT EXISTS directory_links(person_id INT, directory TEXT, row_id INT)")
con.execute("DELETE FROM directory_links WHERE directory='1811'")
# reuse existing 1811 records (same name, in id order) so ids stay stable between rebuilds
old = {}
for pid, cn in con.execute("SELECT id, canonical_name FROM people WHERE source='1811directory' ORDER BY id"):
    old.setdefault(cn, []).append(pid)
linked = created = 0
for rid, given, surname in con.execute("SELECT rowid_, second_name, first_name FROM directory_1811").fetchall():
    surname, given = (surname or "").strip(), (given or "").strip()
    if not surname: continue
    key = norm(f"{given} {surname}")
    pids = pidx.get(key, set()) if given else set()
    if len(pids) == 1:
        pid = next(iter(pids)); linked += 1
    else:
        disp = f"{surname}, {given}" if given else surname
        pid = old[disp].pop(0) if old.get(disp) else con.execute(
            "INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?,'1811directory')", (disp, key)).lastrowid
        created += 1
    con.execute("INSERT INTO directory_links VALUES(?,?,?)", (pid, "1811", rid))
for ids in old.values():   # left-over 1811 records with nothing pointing at them
    for pid in ids:
        if not con.execute("SELECT 1 FROM appearances WHERE person_id=?", (pid,)).fetchone():
            con.execute("DELETE FROM people WHERE id=?", (pid,))
con.commit()
print("1811 directory rows:", len(df), "| winch-linked:", linked, "| new directory people:", created)
