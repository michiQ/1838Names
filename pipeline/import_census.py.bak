#!/usr/bin/env python3
"""Import 1838 census, 1847 census (SOFAAC), and 1838-1847 matches; link to people by name."""
import sqlite3, re, unicodedata
import pandas as pd

DB = "/tmp/org1/black_metropolis.db"
F1838 = "/sessions/charming-magical-davinci/mnt/Newspapers/1838 Names Database/census/1838 Census Finding Aid.xlsx"
FMATCH = "/sessions/charming-magical-davinci/mnt/Newspapers/1838 Names Database/census/1838-1847-matches.xlsx"
F1847 = "/sessions/charming-magical-davinci/mnt/Newspapers/1838 Names Database/census/sofaac-normalized.csv"

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii","ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()

con = sqlite3.connect(DB)

# --- 1838 census ---
df38 = pd.read_excel(F1838)
df38.columns = [re.sub(r"\W+","_",c.strip()).strip("_").lower() for c in df38.columns]
df38.to_sql("census_1838", con, if_exists="replace", index_label="rowid_")
print("census_1838:", len(df38))

# --- 1847 census ---
df47 = pd.read_csv(F1847, encoding="utf-8-sig", dtype=str)
df47.columns = [re.sub(r"\W+","_",c.strip()).strip("_").lower() for c in df47.columns]
df47.to_sql("census_1847", con, if_exists="replace", index_label="rowid_")
print("census_1847:", len(df47))

# --- matches ---
dfm = pd.read_excel(FMATCH, header=1)
dfm.columns = [re.sub(r"\W+","_",str(c).strip()).strip("_").lower() for c in dfm.columns]
dfm.to_sql("census_matches", con, if_exists="replace", index_label="rowid_")
print("census_matches:", len(dfm), "| cols:", list(dfm.columns)[:8])

# --- link to people (unambiguous winch matches only) ---
pidx = {}
for pid, name in con.execute("SELECT id, canonical_name FROM people WHERE source='winch'"):
    if "," not in name: continue
    sur, given = [x.strip() for x in name.split(",", 1)]
    given = re.sub(r"\(.*?\)", "", given).strip()
    g1 = given.split()[0] if given.split() else ""
    if g1:
        pidx.setdefault(norm(f"{g1} {sur}"), set()).add(pid)

con.execute("DROP TABLE IF EXISTS census_links")
con.execute("""CREATE TABLE census_links(person_id INT, census TEXT, row_id INT)""")
con.execute("DELETE FROM people WHERE source='census'")
cidx = {}  # norm name -> census-person pid
linked = created = 0

def resolve(first, last):
    """Winch person if unambiguous; else find-or-create a census-source person."""
    global linked, created
    if not str(last).strip() or str(last).strip().lower() == "nan":
        return None
    key = norm(f"{first} {last}")
    if not key: return None
    pids = pidx.get(key, set())
    if len(pids) == 1:
        linked += 1
        return next(iter(pids))
    if key in cidx: return cidx[key]
    disp = f"{str(last).strip()}, {str(first).strip()}" if str(first).strip() and str(first).strip().lower() != "nan" else str(last).strip()
    cur = con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?, 'census')", (disp, key))
    cidx[key] = cur.lastrowid; created += 1
    return cur.lastrowid

for r in con.execute("SELECT rowid_, first_name_of_head_of_family, last_name_of_head_of_family FROM census_1838"):
    pid = resolve(r[1], r[2])
    if pid: con.execute("INSERT INTO census_links VALUES(?,?,?)", (pid, "1838", r[0]))
for r in con.execute("SELECT rowid_, first_name, last_name FROM census_1847"):
    pid = resolve(r[1], r[2])
    if pid: con.execute("INSERT INTO census_links VALUES(?,?,?)", (pid, "1847", r[0]))
con.commit()
print("winch-linked rows:", linked, "| new census people:", created)
