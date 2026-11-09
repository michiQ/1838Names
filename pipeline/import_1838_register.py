"""Import the 1838 Register of Trades of the Colored People in the City of Philadelphia and Districts
(Philadelphia: Merrihew and Gunn, 1838; Library of Congress copy via the Internet Archive) as its own
source (added 2026-11-08, Michiko). Transcribed by hand from the page images into
pipeline/1838_register_of_trades_source.csv: one row per printed line, with the trade heading, the
asterisk ('These carry on business'), the name, any '(and ...)' second trade, and the address.

Matching (never auto-merges):
- A row links to a Julie Winch record when exactly one Winch person has that given name + surname
  (abbreviations like Jos./Geo./Wm. expanded). When several Winch people share the name, the row links
  only if exactly one of them cites the Register of Trades in Winch's notes (and, if still more than
  one, only if exactly one note also gives the same street address). Otherwise it becomes a new person
  with source='1838register'.
- Rows printed twice under two trades for the same person (same name, same address, e.g. 'Copeland,
  Allen, (and shoemaker)' / '(and bleeder)') share one new record.
- 1838register people are kept out of the other loaders' automatic name matching, like the 1811
  directory. Ambiguous names are written to pipeline/register_1838_matches.md for review.
Run in the rebuild chain right after import_1811_directory (before match_names)."""
import os, re, sqlite3, unicodedata
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get("BM_DB", "/tmp/black_metropolis.db")
CSV = os.path.join(HERE, "1838_register_of_trades_source.csv")
ABBR = {"jos": "joseph", "geo": "george", "wm": "william", "jas": "james", "robt": "robert",
        "dan": "daniel", "thos": "thomas"}

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z ]", " ", s.lower()).split())

def given_key(g):
    toks = norm(g).split()
    return " ".join(ABBR.get(t, t) for t in toks)

con = sqlite3.connect(DB)
df = pd.read_csv(CSV, dtype=str, keep_default_na=False)
df.to_sql("register_1838", con, if_exists="replace", index_label="rowid_")

# Winch index: full given + surname, and first given token + surname
full, first = {}, {}
wentry, cname = {}, {}
for pid, name, aliases, we in con.execute("SELECT id, canonical_name, aliases, winch_entry FROM people WHERE source='winch'"):
    wentry[pid] = we or ""; cname[pid] = name
    for v in [name] + [a for a in (aliases or "").split(" | ") if a]:
        if "," not in v: continue
        sur, given = [x.strip() for x in v.split(",", 1)]
        given = re.sub(r"\(.*?\)", "", given)
        given = re.sub(r"\b(Jr|Sr|Rev|Dr|Mrs|Miss|Mr)\.?", "", given).strip()
        if not given: continue
        full.setdefault(f"{given_key(given)} {norm(sur)}", set()).add(pid)
        first.setdefault(f"{given_key(given).split()[0]} {norm(sur)}", set()).add(pid)

def pick(cands, addr, suf, trade):
    if len(cands) == 1: return next(iter(cands)), "unique"
    rot = {p for p in cands if "Register of Trades" in wentry.get(p, "")}
    if len(rot) == 1: return next(iter(rot)), "the only one Winch cites in the Register"
    pool = rot or set(cands)
    if suf:   # 'Brown, jr., Morris' -> the Winch record named '... Jr.'
        s = {p for p in pool if re.search(r"\b" + suf.rstrip(".") + r"\b", cname[p], re.I)}
        if len(s) == 1: return next(iter(s)), "suffix"
    if len(rot) > 1:
        stem = re.sub(r"[^a-z]", "", trade.lower())[:6]   # 'Dress-Makers' -> 'dressm', matches 'Dressmaker'
        s = {p for p in rot if stem and stem in re.sub(r"[^a-z]", "", wentry[p].lower())}
        if len(s) == 1: return next(iter(s)), "trade matches Winch's note"
        a = norm(addr).split()[:2]
        if a:
            hit = {p for p in rot if " ".join(a) in norm(wentry[p])}
            if len(hit) == 1: return next(iter(hit)), "address matches Winch's note"
    return None, ""

con.execute("CREATE TABLE IF NOT EXISTS directory_links(person_id INT, directory TEXT, row_id INT)")
con.execute("DELETE FROM directory_links WHERE directory='1838rot'")
old = {}
for pid, nn in con.execute("SELECT id, norm_name FROM people WHERE source='1838register' ORDER BY id"):
    old.setdefault(nn, []).append(pid)
made = {}   # same name + address within the Register -> one new record
linked = created = 0
review = []
for r in con.execute("SELECT rowid_, surname, given, suffix, address, trade, as_printed FROM register_1838").fetchall():
    rid, sur, given, suf, addr, trade, printed = r
    gk = given_key(given)
    pid, why = (None, "")
    if gk:
        cands = full.get(f"{gk} {norm(sur)}") or set()
        if not cands:   # 'Bustill, Charles' -> Winch 'Bustill, Charles H.' (still needs a unique or Register-citing match)
            cands = first.get(f"{gk.split()[0]} {norm(sur)}") or set()
        if cands:
            pid, why = pick(cands, addr, suf, trade)
            if pid is None:
                review.append(f"- {printed} ({trade}) -- {len(cands)} Winch records: " +
                              ", ".join(f"#{c}" for c in sorted(cands)))
    if pid is not None:
        linked += 1
    else:
        disp = f"{sur}, {given}" + (f" {suf.capitalize()}" if suf else "") if given else sur
        nkey = norm(f"{given} {sur} {suf}") + " rot1838 " + norm(addr)
        if nkey in made:
            pid = made[nkey]
        else:
            pid = old[nkey].pop(0) if old.get(nkey) else con.execute(
                "INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?,'1838register')", (disp, nkey)).lastrowid
            made[nkey] = pid; created += 1
    con.execute("INSERT INTO directory_links VALUES(?,?,?)", (pid, "1838rot", rid))
for ids in old.values():
    for pid in ids:
        if not con.execute("SELECT 1 FROM appearances WHERE person_id=?", (pid,)).fetchone() and \
           not con.execute("SELECT 1 FROM directory_links WHERE person_id=?", (pid,)).fetchone():
            con.execute("DELETE FROM people WHERE id=?", (pid,))
con.commit()
with open(os.path.join(HERE, "register_1838_matches.md"), "w", encoding="utf-8") as f:
    f.write("# 1838 Register of Trades -- names held back for review\n\n"
            "Each line below shares its name with more than one Julie Winch record, and the Register entry could "
            "not be tied to one of them (by Winch citing the Register, or by address). It was given its own "
            "record instead. To link one, add an id-qualified group to merges.json.\n\n")
    f.write("\n".join(review) + "\n")
print("1838 register rows:", len(df), "| winch-linked:", linked, "| new register people:", created,
      "| held for review:", len(review))
