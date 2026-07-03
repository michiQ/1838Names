#!/usr/bin/env python3
"""Match Winch people against OCR'd newspaper pages -> appearances."""
import sqlite3, re, os, glob, json
from difflib import SequenceMatcher

DB = "/sessions/wonderful-nifty-ritchie/work/black_metropolis.db"
OCR_DIR = "/sessions/wonderful-nifty-ritchie/mnt/Newspapers/1838 Names Database/ocr_text"

PAPER = {"CA": "Colored American", "PF": "Pennsylvania Freeman", "FJ": "Freedom's Journal", "PP": "Pencil Pusher (Philadelphia Tribune)"}

def norm_tok(t):
    return re.sub(r"[^A-Za-z]", "", t)

def close(a, b):
    a, b = a.lower(), b.lower()
    if a == b: return True
    if len(a) >= 6 and len(b) >= 6 and abs(len(a)-len(b)) <= 1:
        return SequenceMatcher(None, a, b).ratio() >= 0.86
    return False

def main():
    con = sqlite3.connect(DB)
    for col in ("issue_id INT", "page INT", "strength INT"):
        try: con.execute(f"ALTER TABLE appearances ADD COLUMN {col}")
        except sqlite3.OperationalError: pass
    con.execute("DELETE FROM appearances")
    con.execute("DELETE FROM issues")
    people = con.execute("SELECT id, canonical_name FROM people").fetchall()
    # parse "Surname, First Middle" -> (surname, [given tokens])
    idx = {}  # surname_lower -> list of (pid, surname, givens)
    for pid, name in people:
        if "," not in name: continue
        sur, given = name.split(",", 1)
        sur = sur.strip()
        givens = [g for g in re.split(r"[ .]+", given.strip()) if g and g[0].isupper()]
        if len(sur) < 4: continue  # too ambiguous
        idx.setdefault(sur.lower()[:4], []).append((pid, sur, givens))

    issue_ids = {}
    total = 0
    for path in sorted(glob.glob(f"{OCR_DIR}/*_p*.txt")):
        base = os.path.basename(path)[:-4]
        slug, pg = base.rsplit("_p", 1)
        code, date = slug.split("_", 1)
        if slug not in issue_ids:
            np_id = con.execute("SELECT id FROM newspapers WHERE name=?", (PAPER[code],)).fetchone()[0]
            cur = con.execute("INSERT OR IGNORE INTO issues(newspaper_id, issue_date, filename, ocr_status) VALUES(?,?,?, 'done')",
                              (np_id, date, slug))
            issue_ids[slug] = con.execute("SELECT id FROM issues WHERE filename=?", (slug,)).fetchone()[0]
        iid = issue_ids[slug]
        text = open(path, encoding="utf-8", errors="replace").read()
        clean = re.sub(r"\s+", " ", text)
        toks = [(m.group(0), m.start()) for m in re.finditer(r"[A-Za-z][A-Za-z''\-]*", clean)]
        span_matches = {}  # span_key -> list of (pid, strength, pos)
        for i, (tok, pos) in enumerate(toks):
            if not tok[0].isupper() or len(tok) < 4: continue
            key = tok.lower()[:4]
            for pid, sur, givens in idx.get(key, []):
                if not close(tok, sur): continue
                matched = False; strength = 0
                for back in (1, 2, 3):
                    if i - back < 0: break
                    ptok = toks[i-back][0]
                    if givens and ptok[0].isupper():
                        g0 = givens[0]
                        if close(ptok, g0): matched = True; strength = 2; break
                        if len(ptok) <= 2 and g0 and ptok[0].lower() == g0[0].lower():
                            matched = True; strength = 1; break
                if not matched: continue
                span_matches.setdefault(pos // 60, []).append((pid, strength, pos))
        for span, ms in span_matches.items():
            best = max(s for _, s, _ in ms)
            keep = [(p, s, po) for p, s, po in ms if s == best]
            amb = 1 if len(keep) > 1 else 0
            for pid, strength, pos in keep:
                ctx = clean[max(0, pos-160):pos+180].strip()
                con.execute("INSERT INTO appearances(person_id, role, context, issue_id, page, strength) VALUES(?,?,?,?,?,?)",
                            (pid, "mentioned" + ("?" if amb else ""), ctx, iid, int(pg), strength))
                total += 1
    con.commit()
    print("appearances:", total)
    for r in con.execute("""SELECT p.canonical_name, COUNT(*) c FROM appearances a
                            JOIN people p ON p.id=a.person_id GROUP BY p.id ORDER BY c DESC LIMIT 15"""):
        print(r)

if __name__ == "__main__":
    main()
