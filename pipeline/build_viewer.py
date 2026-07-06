#!/usr/bin/env python3
"""Export DB to JSON and build the self-contained interactive viewer HTML."""
import sqlite3, json, re

DB = "/tmp/black_metropolis.db"
OUT = "/sessions/loving-determined-fermi/mnt/outputs/1838_black_metropolis_viewer.html"
TPL = "/sessions/loving-determined-fermi/mnt/outputs/viewer_template.html"

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

people = {}
has_aliases = bool(con.execute("SELECT 1 FROM pragma_table_info('people') WHERE name='aliases'").fetchone())
cols = "id, canonical_name, life_dates, winch_entry, source" + (", aliases" if has_aliases else "")
for r in con.execute(f"SELECT {cols} FROM people"):
    people[r["id"]] = {"id": r["id"], "name": r["canonical_name"], "dates": r["life_dates"],
                       "src": r["source"], "refs": [], "mentions": [], "events": [], "articles": [],
                       **({"aka": r["aliases"]} if has_aliases and r["aliases"] else {})}

ORG_RE = re.compile(
    r"(?:Member|Members|Secretary|Treasurer|President|Vice[- ][Pp]resident|Trustee|Deacon|Elder|"
    r"Manager|Director|Steward|Founder|Delegate|Vestryman|Officer|Chaplain|Agent|Librarian|Counsellor)"
    r"s?,?\s+(?:of\s+|to\s+|at\s+|in\s+)?(?:the\s+)?"
    r"([A-Z][A-Za-z''&.\- ]{5,70}?(?:Society|Lodge|Church|Association|Assoc\.|Institute|League|"
    r"Club|Union|Committee|Company|Academy|Beneficial|Masons|Grand Lodge|Conference|Convention|School))")
def org_clean(s):
    s = re.sub(r"\s+", " ", s).strip(" .,;-")
    s = re.sub(r"^(?:of|the|to|at|in)\s+", "", s, flags=re.I)
    s = re.sub(r"\s+(?:meeting|annual meeting|celebration)$", "", s, flags=re.I)
    return s
org_members = {}  # org (canonical lower) -> {"label":..., "pids": set}
def add_org(pid, raw):
    label = org_clean(raw)
    if len(label) < 6: return
    key = label.lower()
    e = org_members.setdefault(key, {"label": label, "pids": set()})
    e["pids"].add(pid)

for r in con.execute("SELECT person_id, note, citation FROM winch_references"):
    if r["person_id"] in people:
        people[r["person_id"]]["refs"].append({"n": r["note"], "c": r["citation"]})
        for m in ORG_RE.finditer(r["note"] or ""):
            add_org(r["person_id"], m.group(1))

issues = {r["id"]: {"slug": r["filename"], "date": r["issue_date"]}
          for r in con.execute("SELECT id, filename, issue_date FROM issues")}

events = {r["id"]: {"id": r["id"], "name": r["name"], "date": r["event_date"],
                    "loc": r["location"], "desc": r["description"], "att": []}
          for r in con.execute("SELECT * FROM events")}

articles = {r["id"]: {"id": r["id"], "hl": r["headline"], "au": r["author"], "ty": r["article_type"],
                      "sum": r["summary"], "pg": r["page"], "issue": issues.get(r["issue_id"], {}).get("slug")}
            for r in con.execute("SELECT * FROM articles")}

# org names appearing in newspaper text near a person's name (OCR-tolerant, proximity-based)
ORG_CTX_RE = re.compile(
    r"(?:[A-Z][A-Za-z''&.\-]+[ ,]+){1,6}(?:Anti-Slavery Society|Society|Lodge|Church|Association|"
    r"Institute|League|Club|Committee|Convention|Conference|Academy|Library Company)")
ORG_STOP = re.compile(r"\b(?:The|This|That|Whereupon|Resolved|Mr|Mrs|Rev|Dr|On|In|Of|At|And|A|An)[ ,]", )
def ctx_orgs(pid, ctx):
    for m in ORG_CTX_RE.finditer(ctx or ""):
        s = m.group(0)
        # trim leading stop-words
        while True:
            sm = ORG_STOP.match(s)
            if sm: s = s[sm.end():].lstrip(" ,")
            else: break
        s = re.sub(r"[ ,]+", " ", s).strip(" .,;")
        if len(s.split()) >= 2 and len(s) >= 10 and not re.search(r"\d", s):
            add_org(pid, s)

# appearances
cooc = {}  # (issue,page) -> set of pids (for mention co-occurrence)
for r in con.execute("SELECT * FROM appearances"):
    pid = r["person_id"]
    if pid not in people: continue
    isl = issues.get(r["issue_id"], {}).get("slug")
    if r["event_id"] and r["event_id"] in events:
        events[r["event_id"]]["att"].append([pid, r["role"]])
        people[pid]["events"].append({"e": r["event_id"], "role": r["role"]})
    elif r["article_id"] and r["article_id"] in articles:
        people[pid]["articles"].append({"a": r["article_id"], "role": r["role"]})
    elif r["role"] in ("mentioned", "mentioned?"):
        if r["role"].endswith("?"):
            continue  # ambiguous match (tied between >1 candidate person) -- too unreliable to show, drop entirely
        people[pid]["mentions"].append({"i": isl, "p": r["page"], "ctx": r["context"], "amb": 0})
        ctx_orgs(pid, r["context"])
        if r["strength"] == 2:
            cooc.setdefault((isl, r["page"]), set()).add(pid)
    else:  # agent/other roles without event
        people[pid]["mentions"].append({"i": isl, "p": r["page"], "ctx": r["context"], "role": r["role"], "amb": 0})

# edges: event co-attendance (strong) + same-page mention co-occurrence (weak)
edges = {}
for e in events.values():
    ids = sorted({p for p, _ in e["att"]})
    for i in range(len(ids)):
        for j in range(i+1, len(ids)):
            k = (ids[i], ids[j])
            edges[k] = edges.get(k, 0) + 3
for (isl, pg), ids in cooc.items():
    ids = sorted(ids)
    for i in range(len(ids)):
        for j in range(i+1, len(ids)):
            k = (ids[i], ids[j])
            edges[k] = edges.get(k, 0) + 1

try:
    urls = json.load(open("/sessions/loving-determined-fermi/mnt/Newspapers/1838 Names Database/pipeline/issue_urls.json"))
except FileNotFoundError:
    urls = {}

# census records per person
def has_table(t):
    return con.execute("SELECT 1 FROM sqlite_master WHERE name=?", (t,)).fetchone()
if has_table("census_links"):
    c38 = {r["rowid_"]: r for r in con.execute("SELECT * FROM census_1838")}
    c47 = {r["rowid_"]: r for r in con.execute("SELECT * FROM census_1847")}
    m38 = {}; m47 = {}
    for r in con.execute("SELECT * FROM census_matches"):
        m38.setdefault(str(r["1838_id"]), r); m47.setdefault(str(r["1847_id"]), r)
    def g(row, key):
        try: v = row[key]
        except (KeyError, IndexError): return None
        return None if v is None or str(v).strip() in ("", "nan", "None") else str(v).strip()
    for pid, cen, rid in con.execute("SELECT person_id, census, row_id FROM census_links"):
        if pid not in people: continue
        p = people[pid]
        if cen == "1838" and rid in c38:
            r = c38[rid]
            rec = {"y": 1838, "name": f'{g(r,"first_name_of_head_of_family") or ""} {g(r,"last_name_of_head_of_family") or ""}'.strip(),
                   "addr": g(r,"address"), "ward": g(r,"ward"), "occM": g(r,"male_occupation_title"),
                   "occF": g(r,"female_s_occupational_title"), "fam": g(r,"number_in_family"),
                   "church": g(r,"first_church_attended"), "wealth": g(r,"total_family_wealth"),
                   "cid": g(r,"id")}
            m = m38.get(rec["cid"] or "")
            if m: rec["match"] = {"cert": g(m,"match_certainty"), "addr47": g(m,"1847_address"), "id47": g(m,"1847_id")}
            p.setdefault("census", []).append(rec)
        elif cen == "1847" and rid in c47:
            r = c47[rid]
            rec = {"y": 1847, "name": f'{g(r,"first_name") or ""} {g(r,"last_name") or ""}'.strip(),
                   "addr": " ".join(x for x in (g(r,"residence_street_number"), g(r,"residence_street_name")) if x),
                   "occM": g(r,"male_occupation_1"), "occF": g(r,"female_occupation_1"),
                   "read": g(r,"can_read"), "write": g(r,"can_write"), "born_slaves": g(r,"born_slaves"),
                   "region": g(r,"region"), "cid": g(r,"id")}
            m = m47.get(rec["cid"] or "")
            if m: rec["match"] = {"cert": g(m,"match_certainty"), "addr38": g(m,"1838_address"), "id38": g(m,"1838_id")}
            p.setdefault("census", []).append(rec)
# orgs found in newspaper text near a person's name (from match_names pass)
if has_table("newspaper_orgs"):
    for pid, org in con.execute("SELECT DISTINCT person_id, org FROM newspaper_orgs"):
        if pid in people: add_org(pid, org)

# orgs from event attendance (event names are org-flavored)
for e in events.values():
    for pid, _ in e["att"]:
        if pid in people and re.search(r"Society|Church|Conference|Convention|Club|Institute|Hall", e["name"]):
            add_org(pid, e["name"])
# finalize orgs: keep those with >=2 members
orgs_out = []
for key, e in org_members.items():
    if len(e["pids"]) >= 2:
        orgs_out.append({"name": e["label"], "members": sorted(e["pids"])})
orgs_out.sort(key=lambda o: (-len(o["members"]), o["name"]))
for o in orgs_out:
    for pid in o["members"]:
        if pid in people:
            people[pid].setdefault("orgs", []).append(o["name"])
print("orgs (>=2 members):", len(orgs_out), "| top:", [(o['name'], len(o['members'])) for o in orgs_out[:5]])

# prune people with no content at all (after census attach)
keep = {pid for pid, p in people.items() if p["refs"] or p["mentions"] or p["events"] or p["articles"] or p.get("census")}
people = {pid: p for pid, p in people.items() if pid in keep}
edges = {k: v for k, v in edges.items() if k[0] in people and k[1] in people}

data = {"people": list(people.values()),
        "events": list(events.values()),
        "articles": list(articles.values()),
        "edges": [[a, b, w] for (a, b), w in edges.items()],
        "issueUrls": urls,
        "orgs": [{"name": o["name"], "members": [p for p in o["members"] if p in people]} for o in orgs_out]}

import datetime
tpl = open(TPL, encoding="utf-8").read()
js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
html = tpl.replace("/*__DATA__*/null", js)
html = html.replace("__BUILD__", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
open(OUT, "w", encoding="utf-8").write(html)
print("people:", len(people), "events:", len(events), "articles:", len(articles),
      "edges:", len(edges), "html bytes:", len(html))
