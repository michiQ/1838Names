#!/usr/bin/env python3
"""Import the 1820 Philadelphia city directory (Black residents, cross-marked '†') as a new
source; link to existing Winch people by name where unambiguous. Modeled on import_census.py but
with one deliberate difference: it does NOT dedupe same-name rows within the source into a single
person (import_census.py's cidx cache does that for census households). A spot-check of this CSV
found 120 rows (~60 name-pairs, e.g. two different "Adams, John" entries -- woodsawyer/back 459
south Second vs mariner/84 Gaskill court) that share a first+last name but have distinct
occupation/address and are evidently different people (zero identical full rows found), so
deduping by name here would silently merge distinct individuals. Every unmatched row therefore
gets its own new person record. NEVER auto-merges: an unambiguous (exactly one) name match against
a Winch person links to that person; anything else (zero or multiple candidates) becomes a new
person tagged source='1820directory'. Matching considers both the Winch canonical_name and any
previously-confirmed aliases (people.aliases, populated by apply_merges.py from merges.json), same
as a person would be found by newspaper OCR matching after a merge is confirmed.

Run alongside import_census.py, BEFORE match_names.py (this script only touches the people table
and its own directory_1820/directory_links tables -- it never writes to appearances/issues, so
unlike match_names.py it's safe to run before or after that script; PIPELINE.md's rebuild order
lists it with the source imports up front for consistency)."""
import sqlite3, re, unicodedata
import pandas as pd

DB = "/tmp/run21/black_metropolis.db"
CSV = "/sessions/wizardly-exciting-dijkstra/mnt/Newspapers/1838 Names Database/pipeline/1820_directory_source.csv"

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()

con = sqlite3.connect(DB)

# --- load directory rows ---
# Source CSV columns: First Name, Second Name, Occupation, Address, PDF Page, Confidence,
# Needs Review, Original OCR Entry. Directory-style surname-first name order: "First Name" column
# holds the SURNAME, "Second Name" holds the GIVEN name (verified against Original OCR Entry text,
# e.g. "Abel,Peter,...,\"fAbel Peter, tinplateworker 83 Cedar\"" -- the OCR text itself is
# surname-then-given, matching directory convention). All columns loaded as text: one source row
# (Blackston, Catharine, PDF Page 442) has a column-shift OCR artifact where non-numeric text
# ended up in the PDF Page/Confidence fields -- loading as TEXT preserves it without crashing
# rather than silently dropping/coercing it; flagged for Michiko in the row's own Needs Review text.
df = pd.read_csv(CSV, dtype=str, keep_default_na=False)
df.columns = [re.sub(r"\W+", "_", c.strip()).strip("_").lower() for c in df.columns]
con.execute("DROP TABLE IF EXISTS directory_1820")
df.to_sql("directory_1820", con, if_exists="replace", index_label="rowid_")
print("directory_1820:", len(df))

# --- link to people (unambiguous winch matches only; else create a new directory-source person) ---
def parse_any(name):
    """-> (surname, first-given-token) from 'Surname, Given' or 'Given ... Surname' text."""
    name = re.sub(r"\(.*?\)", "", name or "").strip()
    if not name:
        return None
    if "," in name:
        sur, given = name.split(",", 1)
        sur = sur.strip(); given = given.strip()
    else:
        toks = name.split()
        if len(toks) < 2:
            return None
        sur, given = toks[-1], " ".join(toks[:-1])
    g1 = given.split()[0] if given.split() else ""
    if not g1 or not sur:
        return None
    return sur, g1

pidx = {}  # norm("given surname") -> set of winch person ids (canonical_name AND aliases indexed)
for pid, name, aliases in con.execute("SELECT id, canonical_name, aliases FROM people WHERE source='winch'"):
    variants = [name] + [a for a in (aliases or "").split(" | ") if a]
    for v in variants:
        parsed = parse_any(v)
        if parsed:
            sur, g1 = parsed
            pidx.setdefault(norm(f"{g1} {sur}"), set()).add(pid)

con.execute("DROP TABLE IF EXISTS directory_links")
con.execute("CREATE TABLE directory_links(person_id INT, directory TEXT, row_id INT)")
con.execute("DELETE FROM people WHERE source='1820directory'")
linked = created = 0

def resolve(given, surname):
    """Winch person if unambiguous (name or alias match); else create a new 1820directory person.
    Deliberately does NOT cache/dedupe by name across rows -- see module docstring."""
    global linked, created
    surname = (surname or "").strip()
    given = (given or "").strip()
    if not surname:
        return None
    key = norm(f"{given} {surname}")
    if not key:
        return None
    pids = pidx.get(key, set())
    if len(pids) == 1:
        linked += 1
        return next(iter(pids))
    disp = f"{surname}, {given}" if given else surname
    cur = con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?, '1820directory')", (disp, key))
    created += 1
    return cur.lastrowid

for r in con.execute("SELECT rowid_, second_name, first_name FROM directory_1820"):
    pid = resolve(r[1], r[2])
    if pid:
        con.execute("INSERT INTO directory_links VALUES(?,?,?)", (pid, "1820", r[0]))
con.commit()
print("1820 directory rows:", len(df), "| winch-linked:", linked, "| new directory people:", created)
