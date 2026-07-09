#!/usr/bin/env python3
"""Detect likely duplicate people; write pipeline/merge_candidates.md for review.
Never merges automatically — output is a review list for Michiko."""
import sqlite3, re, json, unicodedata, os
from difflib import SequenceMatcher

DB = "/tmp/merge2/black_metropolis.db"
PIPE = "/sessions/charming-magical-davinci/mnt/Newspapers/1838 Names Database/pipeline"
OUT = f"{PIPE}/merge_candidates.md"

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii","ignore").decode()
    return re.sub(r"[^a-z ]", " ", s.lower())

def parse(name):
    """-> (surname, [given tokens]) from 'Last, First' or 'First Last' styles."""
    name = re.sub(r"\(.*?\)", "", name).strip()
    if "," in name:
        sur, given = name.split(",", 1)
    else:
        toks = name.split()
        if len(toks) < 2: return norm(name).strip(), []
        sur, given = toks[-1], " ".join(toks[:-1])
    givens = [t for t in re.split(r"[ .]+", norm(given)) if t]
    givens = [g for g in givens if g not in ("rev","dr","mr","mrs","miss","jr","sr","col","capt","bishop")]
    return norm(sur).strip(), givens

def tok_compat(ta, tb):
    if ta == tb: return True
    if len(ta) == 1 and tb.startswith(ta): return True
    if len(tb) == 1 and ta.startswith(tb): return True
    return len(ta) >= 4 and len(tb) >= 4 and SequenceMatcher(None, ta, tb).ratio() >= .85

def given_compatible(g1, g2):
    """Positional: first given must match first given; extra trailing tokens allowed."""
    if not g1 or not g2: return False
    for ta, tb in zip(g1, g2):
        if not tok_compat(ta, tb): return False
    return True

con = sqlite3.connect(DB)
already = set()
mpath = f"{PIPE}/merges.json"
if os.path.exists(mpath):
    for g in json.load(open(mpath)):
        already.add(norm(g["keep"]).strip())
        for a in g.get("aliases", []): already.add(norm(a).strip())

people = []
for pid, name, src in con.execute("SELECT id, canonical_name, source FROM people"):
    napp = con.execute("SELECT COUNT(*) FROM appearances WHERE person_id=?", (pid,)).fetchone()[0]
    nref = con.execute("SELECT COUNT(*) FROM winch_references WHERE person_id=?", (pid,)).fetchone()[0]
    ncen = con.execute("SELECT COUNT(*) FROM census_links WHERE person_id=?", (pid,)).fetchone()[0]
    if napp + nref + ncen == 0: continue   # inert records add noise
    sur, giv = parse(name)
    if len(sur) < 3: continue
    people.append((pid, name, src, sur, giv, napp, nref, ncen))

by_sur = {}
for p in people:
    by_sur.setdefault(p[3][:5], []).append(p)

pairs = []
for key, grp in by_sur.items():
    if len(grp) > 40: continue  # mega-surnames like Brown: skip (too ambiguous to score)
    for i in range(len(grp)):
        for j in range(i+1, len(grp)):
            a, b = grp[i], grp[j]
            if norm(a[1]).strip() in already and norm(b[1]).strip() in already: continue
            surs_close = a[3] == b[3] or SequenceMatcher(None, a[3], b[3]).ratio() >= .88
            if not surs_close: continue
            if not given_compatible(a[4], b[4]): continue
            # score: cross-source pairs and initial-expansion pairs are most valuable
            score = 0
            if a[2] != b[2]: score += 2
            if len(" ".join(a[4])) != len(" ".join(b[4])): score += 1
            if a[3] != b[3]: score -= 1  # fuzzy surname = weaker
            exact_given = a[4] == b[4]
            if exact_given and a[3] == b[3] and a[2] == b[2]: continue  # same-source identical names: genuine distinct people (e.g., Winch's several John Browns)
            pairs.append((score, a, b))

pairs.sort(key=lambda x: -x[0])
lines = ["# Possible duplicate people — review list",
         "",
         "Auto-generated each run. To confirm a merge, add a group to `merges.json`",
         '(format: {"keep": "Canonical Name", "aliases": ["Other spelling", ...]}) — the next run applies it.',
         "Records are never merged automatically; aliases preserve every original spelling.",
         ""]
for score, a, b in pairs[:120]:
    def desc(p):
        bits = [p[2]]
        if p[5]: bits.append(f"{p[5]} appearances")
        if p[6]: bits.append(f"{p[6]} Winch refs")
        if p[7]: bits.append(f"{p[7]} census records")
        return f"**{p[1]}** ({', '.join(bits)})"
    lines.append(f"- [{'HIGH' if score>=2 else 'maybe'}] {desc(a)} ↔ {desc(b)}")
open(OUT, "w").write("\n".join(lines) + "\n")
print(f"candidates: {len(pairs)} (top 120 written to merge_candidates.md)")
for score, a, b in pairs[:10]:
    print(f"  [{score}] {a[1]}  <->  {b[1]}")
