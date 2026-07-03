#!/usr/bin/env python3
"""Export DB to JSON and build the self-contained interactive viewer HTML."""
import sqlite3, json, re

DB = "/tmp/black_metropolis.db"
OUT = "/sessions/loving-determined-fermi/mnt/outputs/1838_black_metropolis_viewer.html"
TPL = "/sessions/loving-determined-fermi/mnt/outputs/viewer_template.html"

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

people = {}
for r in con.execute("SELECT id, canonical_name, life_dates, winch_entry, source FROM people"):
    people[r["id"]] = {"id": r["id"], "name": r["canonical_name"], "dates": r["life_dates"],
                       "src": r["source"], "refs": [], "mentions": [], "events": [], "articles": []}

for r in con.execute("SELECT person_id, note, citation FROM winch_references"):
    if r["person_id"] in people:
        people[r["person_id"]]["refs"].append({"n": r["note"], "c": r["citation"]})

issues = {r["id"]: {"slug": r["filename"], "date": r["issue_date"]}
          for r in con.execute("SELECT id, filename, issue_date FROM issues")}

events = {r["id"]: {"id": r["id"], "name": r["name"], "date": r["event_date"],
                    "loc": r["location"], "desc": r["description"], "att": []}
          for r in con.execute("SELECT * FROM events")}

articles = {r["id"]: {"id": r["id"], "hl": r["headline"], "au": r["author"], "ty": r["article_type"],
                      "sum": r["summary"], "pg": r["page"], "issue": issues.get(r["issue_id"], {}).get("slug")}
            for r in con.execute("SELECT * FROM articles")}

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
        people[pid]["mentions"].append({"i": isl, "p": r["page"], "ctx": r["context"],
                                        "amb": 1 if r["role"].endswith("?") else 0})
        if r["strength"] == 2 and not r["role"].endswith("?"):
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

# prune people with no content at all (keep all winch though — they have refs)
keep = {pid for pid, p in people.items() if p["refs"] or p["mentions"] or p["events"] or p["articles"]}
people = {pid: p for pid, p in people.items() if pid in keep}
edges = {k: v for k, v in edges.items() if k[0] in people and k[1] in people}

try:
    urls = json.load(open("/sessions/loving-determined-fermi/mnt/Newspapers/1838 Names Database/pipeline/issue_urls.json"))
except FileNotFoundError:
    urls = {}
data = {"people": list(people.values()),
        "events": list(events.values()),
        "articles": list(articles.values()),
        "edges": [[a, b, w] for (a, b), w in edges.items()],
        "issueUrls": urls}

tpl = open(TPL, encoding="utf-8").read()
js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
html = tpl.replace("/*__DATA__*/null", js)
open(OUT, "w", encoding="utf-8").write(html)
print("people:", len(people), "events:", len(events), "articles:", len(articles),
      "edges:", len(edges), "html bytes:", len(html))
