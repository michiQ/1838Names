#!/usr/bin/env python3
"""Match Winch people against OCR'd newspaper pages -> appearances."""
import sqlite3, re, os, glob, json
from difflib import SequenceMatcher

DB = "/tmp/black_metropolis.db"
OCR_DIR = "/tmp/ocr"

PAPER = {"CA": "Colored American", "PF": "Pennsylvania Freeman", "FJ": "Freedom's Journal", "PP": "Pencil Pusher (Philadelphia Tribune)"}

DATE_OVERRIDE = {
 "PP_000": "1914-10-24", "PP_001": "1912-11-16", "PP_002": "1913-02-15", "PP_003": "1912-01-27",
 "PP_004": "1913-04-19", "PP_005": "1914-06-20", "PP_006": "1914-05-02", "PP_007": "1912-11-23",
 "PP_008": "1914-05-09", "PP_009": "1912-10-19", "PP_010": "1914-04-04", "PP_011": "1912-08-24",
 "PP_015": "1912-12-21", "PP_016": "1912-10-26", "PP_017": "1913-03-01", "PP_018": "1913-05-03",
 "PP_019": "1913-11-29", "PP_020": "1914-01-24", "PP_021": "1912-04-06", "PP_022": "1913-12-06",
 "PP_023": "1913-08-02", "PP_024": "1912-04-20", "PP_025": "1914-07-18", "PP_026": "1914-03-28",
 "PP_027": "1913-01-25", "PP_028": "1913-01-18",
 "PP_012": "1913-11-01", "PP_013": "1912-03-02", "PP_014": "1914-05-30",
 "PP_029": "1912-03-09", "PP_030": "1912-03-02", "PP_031": "1912-02-03", "PP_032": "1914-05-23",
 "PP_033": "1913-02-22", "PP_034": "1912-08-31", "PP_035": "1914-03-07", "PP_036": "1914-09-26",
 "PP_037": "1912-04-27", "PP_038": "1912-07-13", "PP_039": "1912-04-13", "PP_040": "1913-09-27",
 "PP_041": "1914-02-07", "PP_042": "1913-07-26", "PP_043": "1912-12-28",
 "PP_044": "1912-03-23", "PP_045": "1912-06-08", "PP_046": "1914-08-01", "PP_047": "1914-01-31",
 "PP_048": "1912-08-03", "PP_049": "1912-07-20", "PP_050": "1912-06-29", "PP_051": "1914-10-03",
 "PP_052": "1912-10-12", "PP_053": "1912-03-16", "PP_054": "1914-04-25", "PP_055": "1914-01-17",
 "PP_056": "1913-10-18", "PP_057": "1912-05-18", "PP_059": "1914-08-15", "PP_060": "1913-11-08", "PP_061": "1912-06-15", "PP_062": "1912-05-25",
 "PP_063": "1914-06-13", "PP_064": "1914-07-25", "PP_065": "1913-01-11", "PP_066": "1912-10-05",
 "PP_067": "1912-07-27", "PP_068": "1914-07-11", "PP_069": "1912-09-07", "PP_070": "1912-06-22",
 "PP_071": "1912-05-11",
 "PP_058": "1912-02-10"}

ORG_TXT_RE = re.compile(
    r"(?:[A-Z][A-Za-z''&.\-]+[ ,]+){1,6}(?:Anti-Slavery Society|Society|Lodge|Association|"
    r"Institute|League|Library Company|Literary Company)"
    r"|(?:[A-Z][A-Za-z''&.\-]+[ ]+){1,4}(?:Church|Club|Academy)")
ORG_LEAD_STOP = re.compile(r"^(?:The|This|That|Whereupon|Resolved|Mr|Mrs|Rev|Dr|On|In|Of|At|And|A|An|To|For|From|By|With|Our|His|Her|Their|Its|Was|Is|Are|Were|Be|Been|Said|New|Late|Old)[ ,]+")
def clean_org(s):
    s = re.sub(r"[ ,]+", " ", s).strip(" .,;")
    while True:
        m = ORG_LEAD_STOP.match(s)
        if not m: break
        s = s[m.end():]
    return s if len(s.split()) >= 2 and len(s) >= 10 and not re.search(r"\d", s) else None

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
    con.execute("CREATE TABLE IF NOT EXISTS newspaper_orgs(person_id INT, org TEXT, issue TEXT, page INT)")
    con.execute("DELETE FROM newspaper_orgs")
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
                              (np_id, DATE_OVERRIDE.get(slug, date), slug))
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
        page_orgs = []
        for m in ORG_TXT_RE.finditer(clean):
            label = clean_org(m.group(0))
            if label: page_orgs.append((label, m.start()))
        for span, ms in span_matches.items():
            best = max(s for _, s, _ in ms)
            keep = [(p, s, po) for p, s, po in ms if s == best]
            amb = 1 if len(keep) > 1 else 0
            for pid, strength, pos in keep:
                ctx = clean[max(0, pos-160):pos+180].strip()
                con.execute("INSERT INTO appearances(person_id, role, context, issue_id, page, strength) VALUES(?,?,?,?,?,?)",
                            (pid, "mentioned" + ("?" if amb else ""), ctx, iid, int(pg), strength))
                total += 1
                if strength == 2 and not amb:
                    seen_po = set()
                    for label, opos in page_orgs:
                        if abs(opos - pos) <= 600 and label not in seen_po:
                            seen_po.add(label)
                            con.execute("INSERT INTO newspaper_orgs VALUES(?,?,?,?)", (pid, label, slug, int(pg)))
    con.commit()
    print("appearances:", total)
    for r in con.execute("""SELECT p.canonical_name, COUNT(*) c FROM appearances a
                            JOIN people p ON p.id=a.person_id GROUP BY p.id ORDER BY c DESC LIMIT 15"""):
        print(r)

if __name__ == "__main__":
    main()
