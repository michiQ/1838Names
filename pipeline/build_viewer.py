#!/usr/bin/env python3
"""Export DB to JSON and build the self-contained interactive viewer HTML."""
import os, sqlite3, json, re

DB = os.environ.get("BM_DB", "/tmp/black_metropolis.db")
OUT = "/tmp/repo/index.html"
TPL = "/tmp/repo/pipeline/viewer_template.html"
ORG_ALIASES = "/tmp/repo/pipeline/org_aliases.json"

# organization name normalization: fold known spelling/punctuation variants of the same
# org into one canonical display name before counting/deduping. Curated by Michiko; see
# org_aliases.json. Display-layer only -- does not touch the DB or any people/events tables.
def _org_norm_key(s):
    return re.sub(r"\s+", " ", s or "").strip().lower()
ORG_ALIAS_LOOKUP = {}  # normalized variant/canonical string -> canonical display name
try:
    for group in json.load(open(ORG_ALIASES, encoding="utf-8")):
        canon = group["canonical"]
        ORG_ALIAS_LOOKUP[_org_norm_key(canon)] = canon
        for alias in group.get("aliases", []):
            ORG_ALIAS_LOOKUP[_org_norm_key(alias)] = canon
except FileNotFoundError:
    pass

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
    r"Club|Union|Committee|Company|Academy|Beneficial|Masons|Grand Lodge|Conference|Convention|School|"
    r"College|Colony|Studio|Circle))")
def org_clean(s):
    s = re.sub(r"\s+", " ", s).strip(" .,;-")
    s = re.sub(r"(?<=\w)-\s+(?=\w)", "-", s)   # OCR/line-break hyphen space: "Anti- Slavery" -> "Anti-Slavery"
    s = re.sub(r"^(?:of|the|to|at|in)\s+", "", s, flags=re.I)
    s = re.sub(r"\s+(?:meeting|annual meeting|celebration)$", "", s, flags=re.I)
    return s
org_members = {}  # org (canonical lower) -> {"label":..., "pids": set, "src": {pid: source}}
def _src_rank(s):  # newspaper page (linkable) > event > winch note
    return 2 if "i" in s else (1 if "e" in s else 0)
def add_org(pid, raw, src=None):
    label = org_clean(raw)
    if len(label) < 6: return
    label = ORG_ALIAS_LOOKUP.get(_org_norm_key(label), label)  # fold known spelling variants
    key = label.lower()
    e = org_members.setdefault(key, {"label": label, "pids": set(), "src": {}})
    e["pids"].add(pid)
    if src:
        cur = e["src"].get(pid)
        if cur is None or _src_rank(src) > _src_rank(cur):
            e["src"][pid] = src

for r in con.execute("SELECT person_id, note, citation FROM winch_references"):
    if r["person_id"] in people:
        people[r["person_id"]]["refs"].append({"n": r["note"], "c": r["citation"]})
        for m in ORG_RE.finditer(r["note"] or ""):
            add_org(r["person_id"], m.group(1), {"w": 1})

issues = {r["id"]: {"slug": r["filename"], "date": r["issue_date"]}
          for r in con.execute("SELECT id, filename, issue_date FROM issues")}

events = {r["id"]: {"id": r["id"], "name": r["name"], "date": r["event_date"],
                    "loc": r["location"], "desc": r["description"], "att": [],
                    "issue": issues.get(r["issue_id"], {}).get("slug"), "pg": r["page"]}
          for r in con.execute("SELECT * FROM events")}

articles = {r["id"]: {"id": r["id"], "hl": r["headline"], "au": r["author"], "ty": r["article_type"],
                      "sum": r["summary"], "pg": r["page"], "issue": issues.get(r["issue_id"], {}).get("slug")}
            for r in con.execute("SELECT * FROM articles")}

# mention -> article title attribution (added 2026-08-19, Michiko): a plain mention only knows
# its issue+page, so attach the curated article headline ONLY when exactly one article is on
# that page -- with 2+ articles the attribution would be a guess, so those show no title.
arts_on_page = {}
for a in articles.values():
    arts_on_page.setdefault((a["issue"], a["pg"]), []).append(a["hl"])
def page_article(isl, pg):
    hls = arts_on_page.get((isl, pg))
    return hls[0] if hls and len(hls) == 1 else None

# org names appearing in newspaper text near a person's name (OCR-tolerant, proximity-based)
ORG_CTX_RE = re.compile(
    r"(?:[A-Z][A-Za-z''&.\-]+[ ,]+){1,6}(?:Anti-Slavery Society|Society|Lodge|Church|Association|"
    r"Institute|League|Club|Committee|Convention|Conference|Academy|Library Company)")
ORG_STOP = re.compile(r"\b(?:The|This|That|Whereupon|Resolved|Mr|Mrs|Rev|Dr|On|In|Of|At|And|A|An)[ ,]", )
def ctx_orgs(pid, ctx, src=None):
    for m in ORG_CTX_RE.finditer(ctx or ""):
        s = m.group(0)
        # trim leading stop-words
        while True:
            sm = ORG_STOP.match(s)
            if sm: s = s[sm.end():].lstrip(" ,")
            else: break
        s = re.sub(r"[ ,]+", " ", s).strip(" .,;")
        if len(s.split()) >= 2 and len(s) >= 10 and not re.search(r"\d", s):
            add_org(pid, s, src)

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
        if r["role"] == "author":
            people[pid]["articles"].append({"a": r["article_id"], "role": r["role"]})
        else:
            # named IN an article (proprietor of an ad, subject of a review/obituary, etc.) --
            # surface under "Appears in the paper" with the article's title + their role, rather
            # than mislabel them as having written/signed it (added 2026-08-19).
            art = articles[r["article_id"]]
            people[pid]["mentions"].append({"i": isl, "p": r["page"], "ctx": r["context"],
                                            "role": r["role"], "amb": 0, "art": art["hl"]})
    elif r["role"] in ("mentioned", "mentioned?"):
        if r["role"].endswith("?"):
            continue  # ambiguous match (tied between >1 candidate person) -- too unreliable to show, drop entirely
        m = {"i": isl, "p": r["page"], "ctx": r["context"], "amb": 0}
        _hl = page_article(isl, r["page"])
        if _hl: m["art"] = _hl
        people[pid]["mentions"].append(m)
        ctx_orgs(pid, r["context"], {"i": isl, "p": r["page"]})
        if r["strength"] == 2:
            cooc.setdefault((isl, r["page"]), set()).add(pid)
    else:  # agent/other roles without event
        m = {"i": isl, "p": r["page"], "ctx": r["context"], "role": r["role"], "amb": 0}
        _hl = page_article(isl, r["page"])
        if _hl: m["art"] = _hl
        people[pid]["mentions"].append(m)

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
    urls = json.load(open("/tmp/repo/pipeline/issue_urls.json"))
except FileNotFoundError:
    urls = {}

# which issues have local page JPEGs rendered (pages/<slug>_p<N>.jpg) -- issues without
# any (e.g. a born-digital dissertation source) fall back to a page-anchored Drive link instead.
import glob as _glob, os as _os
PAGES_DIR = "/tmp/repo/pages"
jpeg_slugs = sorted({_os.path.basename(p).rsplit("_p", 1)[0]
                      for p in _glob.glob(f"{PAGES_DIR}/*_p*.jpg")})

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
# 1820 Philadelphia city directory (Black residents, cross-marked) -- source-record data only,
# like census: enriches the person with occupation/address/etc, no graph edges synthesized.
if has_table("directory_links"):
    d1820 = {r["rowid_"]: r for r in con.execute("SELECT * FROM directory_1820")}
    for pid, dirn, rid in con.execute("SELECT person_id, directory, row_id FROM directory_links"):
        if pid not in people: continue
        p = people[pid]
        if dirn == "1820" and rid in d1820:
            r = d1820[rid]
            rec = {"y": 1820, "name": f'{g(r,"second_name") or ""} {g(r,"first_name") or ""}'.strip(),
                   "occ": g(r,"occupation"), "addr": g(r,"address"), "pdfPage": g(r,"pdf_page"),
                   "conf": g(r,"confidence"), "needsReview": g(r,"needs_review"),
                   "ocr": g(r,"original_ocr_entry")}
            p.setdefault("directory", []).append(rec)

# orgs found in newspaper text near a person's name (from match_names pass)
if has_table("newspaper_orgs"):
    for pid, org, isl, pg in con.execute("SELECT DISTINCT person_id, org, issue, page FROM newspaper_orgs"):
        if pid in people: add_org(pid, org, {"i": isl, "p": pg})

# Institute for Colored Youth students & graduates named by Fanny Jackson Coppin
# (Reminiscences of School Life, 1913). Each becomes a member of one ICY org node,
# and gets a "coppin" record so they're kept and shown even with no other appearance.
if has_table("coppin_students"):
    for pid, note in con.execute("SELECT person_id, note FROM coppin_students"):
        if pid in people:
            people[pid].setdefault("coppin", []).append({"n": note or ""})
            add_org(pid, "Institute for Colored Youth", {"coppin": 1})

# orgs from event attendance (event names are org-flavored)
# Organizations from events (rewritten 2026-10-31, Michiko's org-list consolidation). An event adds its
# attendees to the organization NAMED in it, not to an "organization" made of the whole event title:
#   "Banneker Institute -- lecture by ..."            -> Banneker Institute
#   "Fourth Annual Meeting of the Western New York Anti-Slavery Society" -> Western New York Anti-Slavery Society
#   "John Brown sympathy meeting, National Hall"      -> (none: a meeting, stays in Events only)
# pipeline/event_orgs.json holds hand-reviewed overrides (null = no organization) and always wins.
ORG_WORDS_OLD = r"Society|Church|Conference|Convention|Club|Institute|Hall|College|Academy|Colony|Studio|Circle"
ORG_WORDS_SPLIT = ORG_WORDS_OLD + r"|Association|Company|Union|Lodge|Assembly|Order|Tabernacle"
ORG_END = {"Society","Association","Institute","Union","Church","Lodge","Company","Club","Academy","College","Assembly","Order","Tabernacle","Conference"}
CONNECT = {"of","the","and","for","&"}
LEAD = re.compile(r"^(?:(?:Death|Dedication|Founding|Organization|Consecration|Re-?opening|Anniversary|Annual|First|Second|Third|Fourth|Fifth|"
                  r"Sixth|Seventh|Eighth|Sixteenth|Twentieth|Meeting|Public|Mass|Great|Festival|Lecture|Reception|Concert|Convention|Call|"
                  r"Committee|Adjourned|Revival|Protracted|Quarterly|The|Expulsion|Donation|Corner-stone)\b[\w\s,'.-]*?\b(?:of|by|for|to|before)\s+(?:the\s+)?)", re.I)
INNER_EVENT = {"Fair","Meeting","Meetings","Anniversary","Festival","Celebration","Concert","Dinner","Lecture","Camp"}
ROLE = {"Clerk","Rev.","Rev","Bishop","Elder","Dr.","Dr","Brother","Sister","Mr.","Mrs."}
LOC = {"at","in","near","from"}
MEETING = re.compile(r"\b(?:meeting|meetings|celebration|reception|anniversary|exercises|dinner|fair|founded|lecture|sympathy|concert|"
                     r"convention|vote|notices|official staff|tour|debate|revival|funeral|proceedings|session|parade|festival|settles|"
                     r"installed|choir|entertainment|rescue|appointed|visits|admitted|formed|campaign|circular|pledges)\b", re.I)
def _w(t): return t.strip(",;:()\"—–")
def _brk(t): return t.endswith((",", ";", ":", ")")) or t in ("—","–","--")
def longest_org(nm):
    m = LEAD.match(nm)
    body = nm[m.end():] if m else nm
    toks = body.replace("—", " — ").replace("–", " – ").split()
    best = None; i = 0
    while i < len(toks):
        w = _w(toks[i])
        if not w or not (w[0].isupper() or w[0].isdigit()) or w in ROLE:
            i += 1; continue
        prev = _w(toks[i-1]).lower() if i else ""
        j = i; span_end = None
        while j < len(toks):
            wj = _w(toks[j])
            if not wj or not (wj[0].isupper() or wj[0].isdigit() or wj in CONNECT): break
            if wj in INNER_EVENT: span_end = None; i = j + 1     # restart after an event word
            if wj in ORG_END: span_end = j
            if _brk(toks[j]):
                nxt = _w(toks[j+1]) if j + 1 < len(toks) else ""
                if not (toks[j].endswith(",") and nxt[:1].isupper() and span_end is None): break
            j += 1
        if span_end is not None and i <= span_end and prev not in LOC:
            k = span_end
            while k + 1 < len(toks) and not _brk(toks[k]) and _w(toks[k+1]).lower() in ("of","the"):
                m2 = k + 1
                while m2 < len(toks) and _w(toks[m2]).lower() in ("of","the","and"): m2 += 1
                if m2 < len(toks) and _w(toks[m2])[:1].isupper():
                    k = m2
                    while k + 1 < len(toks) and not _brk(toks[k]) and _w(toks[k+1])[:1].isupper() and _w(toks[k+1]) not in INNER_EVENT: k += 1
                else: break
            span = " ".join(toks[i:k+1]).strip(" ,;:()")
            span = re.sub(r"\s*\(.*$", "", span)
            if len(span.split()) >= 2 and (best is None or len(span) > len(best)): best = span
        i = max(j, i + 1)
    return best
def event_org_name(nm):
    if " -- " in nm:
        pre = nm.split(" -- ", 1)[0].strip()
        if re.search(ORG_WORDS_SPLIT, pre) and not MEETING.search(pre):
            return pre
    if MEETING.search(nm) or LEAD.match(nm):
        return longest_org(nm)
    if re.search(ORG_WORDS_OLD, nm):
        return longest_org(nm) or nm
    return None

EVENT_ORG_OVERRIDES = {}
try:
    EVENT_ORG_OVERRIDES = json.load(open(os.path.join(os.path.dirname(TPL), "event_orgs.json"), encoding="utf-8"))["events"]
except FileNotFoundError:
    pass
for e in events.values():
    nm = e["name"]
    org_name = EVENT_ORG_OVERRIDES[nm] if nm in EVENT_ORG_OVERRIDES else event_org_name(nm)
    if not org_name:
        continue
    for pid, _ in e["att"]:
        if pid in people:
            add_org(pid, org_name, {"e": e["id"]})
# Hand-curated organizations (pipeline/curated_orgs.json, Michiko 2026-11-01: the vigilance committees
# kept as separate groups, plus the Frank Johnson Guards and Williams Assembly). Automatic labels in
# "drop" are removed first, then each curated org gets exactly the listed members, each with its role
# and citation. Curated orgs are always kept, even with no members, and carry a note shown in the panel.
CURATED = json.load(open(os.path.join(os.path.dirname(TPL), "curated_orgs.json"), encoding="utf-8"))
for lbl in CURATED.get("drop", []):
    gone = org_members.pop(lbl.lower(), None)
    if gone: print("   curated: dropped automatic org", repr(lbl), len(gone["pids"]), "members")
CURATED_NOTES = {}
for co in CURATED["orgs"]:
    key = co["name"].lower()
    e = org_members.setdefault(key, {"label": co["name"], "pids": set(), "src": {}})
    e["label"] = co["name"]; e["curated"] = True
    CURATED_NOTES[co["name"]] = co.get("note", "")
    for pid, sv in co["members"]:
        if pid not in people:
            print("   curated: WARNING member id", pid, "not in people for", co["name"]); continue
        e["pids"].add(pid); e["src"][pid] = sv
# Fold "<Org> <meeting description>" entries into <Org> (added 2026-10-31, Michiko's org-list
# consolidation). An entry folds only when it starts with another org's full name followed by
# punctuation or an event word (meeting, annual, anniversary, quarterly, delegation ...), and never
# into a generic name. Display-layer only; ORG_FOLD_LOG lists every fold for review.
ORG_EVENT_WORDS = r"(?:meeting|meetings|annual|anniversary|quarterly|commencement|lecture|lectures|exercises|election|delegation|delegates|special|winter|admitted|convention|first|second|third|fourth|public|celebration|fair|festival|examination)\b"
ORG_GENERIC = {"anti-slavery society", "african methodist episcopal church", "a.m.e. church", "methodist episcopal church",
               "presbyterian church", "baptist church", "episcopal church"}
ORG_FOLD_LOG = []
def _fold_target(label):
    best = None
    for k, e2 in org_members.items():
        kl = e2["label"]
        if kl == label or len(kl) >= len(label) or k in ORG_GENERIC or len(kl.split()) < 2: continue
        if not label.startswith(kl): continue
        rest = label[len(kl):]
        if re.match(r"\s*(?:[:,(]|—|–|--)", rest) or re.match(r"\s+" + ORG_EVENT_WORDS, rest, re.I):
            if best is None or len(kl) > len(org_members[best]["label"]): best = k
    return best
for key in sorted(org_members, key=lambda k: -len(org_members[k]["label"])):
    if key not in org_members: continue
    tgt = _fold_target(org_members[key]["label"])
    if tgt:
        src_e, dst_e = org_members.pop(key), org_members[tgt]
        dst_e["pids"] |= src_e["pids"]
        for pid, sv in src_e["src"].items():
            cur = dst_e["src"].get(pid)
            if cur is None or _src_rank(sv) > _src_rank(cur): dst_e["src"][pid] = sv
        ORG_FOLD_LOG.append((src_e["label"], dst_e["label"]))
print("org folds:", len(ORG_FOLD_LOG))
for a, b in ORG_FOLD_LOG: print("   fold:", a, "=>", b)
# finalize orgs: keep those with >=2 members
orgs_out = []
for key, e in org_members.items():
    # >=2 members, OR named in a curated event (a real organization even if only its secretary is known,
    # e.g. the 1827 Protecting Society -- added 2026-10-31, Michiko)
    if e.get("curated") or len(e["pids"]) >= 2 or any("e" in sv for sv in e["src"].values()):
        orgs_out.append({"name": e["label"], "members": sorted(e["pids"]), "src": e["src"],
                         **({"note": CURATED_NOTES[e["label"]]} if CURATED_NOTES.get(e["label"]) else {})})
orgs_out.sort(key=lambda o: (-len(o["members"]), o["name"]))
for o in orgs_out:
    for pid in o["members"]:
        if pid in people:
            people[pid].setdefault("orgs", []).append(o["name"])
print("orgs (>=2 members):", len(orgs_out), "| top:", [(o['name'], len(o['members'])) for o in orgs_out[:5]])

# Northern Liberties tour profiles (curated biographies + page-anchored PDF citations)
if has_table("nolibs_profiles"):
    for pid, story, cite, url in con.execute("SELECT person_id, story, cite, url FROM nolibs_profiles"):
        if pid in people:
            people[pid].setdefault("nolibs", []).append({"s": story, "c": cite, "u": url})

# William Still's Underground Railroad appearances (chapter + page-anchored Internet Archive link)
if has_table("ugrr_appearances"):
    for pid, chapter, page, url in con.execute("SELECT person_id, chapter, page, url FROM ugrr_appearances"):
        if pid in people:
            people[pid].setdefault("ugrr", []).append({"ch": chapter, "pg": page, "u": url})

# 1838 Black Metropolis StoryMaps (mob attacks) -- per-person snippet + link to the year's StoryMap.
# The attack itself is an event node (see the events table); this just adds each person's snippet.
if has_table("storymap_people"):
    for pid, key, title, sdate, url, role, snippet in con.execute(
            "SELECT person_id, story_key, title, story_date, url, role, snippet FROM storymap_people"):
        if pid in people:
            people[pid].setdefault("storymap", []).append(
                {"k": key, "t": title, "d": sdate, "u": url, "role": role, "s": snippet})

# 1838 Black Metropolis blog archive -- each post is its own source; every person named in a
# post gets a snippet + links (View Blog -> live URL, View PDF -> hosted blogs/<pdf>). Blog meta
# (title/url/pdf) is stored once per slug; each person just carries {slug, snippet}.
blogs_meta = {}
if has_table("blogs"):
    for slug, title, url, pdf in con.execute("SELECT slug, title, url, pdf FROM blogs"):
        blogs_meta[slug] = {"t": title, "u": url, "pdf": pdf}
if has_table("blog_appearances"):
    for pid, slug, snippet in con.execute("SELECT person_id, slug, snippet FROM blog_appearances"):
        if pid in people:
            people[pid].setdefault("blog", []).append({"slug": slug, "s": snippet})


# 1838 Mob Attack Statistics (Self-Defense & Resistance sheet) -- per-person entries with
# per-entry source links; the main-source footer credit links to /attackstats.
mobstats_meta = {}
if has_table("mobstats"):
    import json as _json
    for mid, attack, loc, typ, cat, desc, means, outcome, defenders, srcs in con.execute(
            "SELECT id,attack,location,type,category,description,means,outcome,defenders,sources FROM mobstats"):
        mobstats_meta[mid] = {"a": attack, "l": loc, "ty": typ, "cat": cat, "d": desc,
                              "m": means, "o": outcome, "df": defenders,
                              "src": _json.loads(srcs or "[]")}
if has_table("mobstats_people"):
    for pid, mid in con.execute("SELECT person_id, entry_id FROM mobstats_people"):
        if pid in people:
            people[pid].setdefault("mobstats", []).append(mid)

# prune people with no content at all (after census attach)
# Hand-curated person-to-person connections (pipeline/person_links.json, Michiko). Shown on both
# profiles ("Connected to") and added as a strong map link.
for lk in json.load(open(os.path.join(os.path.dirname(TPL), "person_links.json"), encoding="utf-8"))["links"]:
    a, b2 = lk["a"], lk["b"]
    if a in people and b2 in people:
        people[a].setdefault("links", []).append({"p": b2, "n": lk.get("note", "")})
        people[b2].setdefault("links", []).append({"p": a, "n": lk.get("note", "")})
        k = (min(a, b2), max(a, b2)); edges[k] = edges.get(k, 0) + 3
    else:
        print("   person_links: WARNING missing id", a, b2)
keep = {pid for pid, p in people.items() if p["refs"] or p["mentions"] or p["events"] or p["articles"] or p.get("census") or p.get("directory") or p.get("nolibs") or p.get("ugrr") or p.get("coppin") or p.get("storymap") or p.get("blog") or p.get("mobstats") or p.get("links")}
people = {pid: p for pid, p in people.items() if pid in keep}
edges = {k: v for k, v in edges.items() if k[0] in people and k[1] in people}

data = {"people": list(people.values()),
        "events": list(events.values()),
        "articles": list(articles.values()),
        "edges": [[a, b, w] for (a, b), w in edges.items()],
        "issueUrls": urls,
        "jpegIssues": jpeg_slugs,
        "orgs": [{"name": o["name"], "members": [p for p in o["members"] if p in people],
                  "src": {str(p): s for p, s in o["src"].items() if p in people},
                  **({"note": o["note"]} if o.get("note") else {})} for o in orgs_out],
        "blogs": blogs_meta,
        "mobstats": mobstats_meta}

import datetime
tpl = open(TPL, encoding="utf-8").read()
# Michiko 2026-11-01: no "VERIFY" wording in the public listings (the header says this is a curated
# passion project). Source files keep their [VERIFY] flags for review; they are stripped here, at display.
_VER_BRACKET = re.compile(r"\s*\[[^\[\]]*?\bVERIFY\b[^\[\]]*\]", re.I)
_VER_SCAN = re.compile(r"\s*-\s*verify against scan", re.I)
def _unverify(x):
    if isinstance(x, str):
        if "erif" not in x and "ERIF" not in x: return x
        y = _VER_SCAN.sub("", _VER_BRACKET.sub("", x))
        y = re.sub(r"\s*;\s*(?=$|[)\],])", "", y)          # dangling '; ' left where a flag was
        y = re.sub(r"\(\s*\)", "", y)                     # empty parentheses
        y = re.sub(r"\s+([,.;)])", r"\1", y)
        return re.sub(r"  +", " ", y).strip() if y != x else x
    if isinstance(x, list): return [_unverify(v) for v in x]
    if isinstance(x, dict): return {k: _unverify(v) for k, v in x.items()}
    return x
data = _unverify(data)
_left = len(re.findall(r"\bVERIFY\b|\bverify\b", json.dumps(data, ensure_ascii=False)))
print("   verify flags stripped from display; remaining 'verify' words:", _left)
js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
html = tpl.replace("/*__DATA__*/null", js)
# Optional baked "All connections" layout (see viewer_template.html / precompute_fullmap.js):
# inject it if present so the first open of the map is instant; otherwise leave null and the
# viewer settles the layout live in-browser (its previous behavior).
_fm_path = os.path.join(os.path.dirname(os.path.abspath(TPL)), "fullmap_layout.json")
_fm = open(_fm_path, encoding="utf-8").read().strip() if os.path.exists(_fm_path) else "null"
html = html.replace("/*__FULLMAP__*/null", _fm or "null")
html = html.replace("__BUILD__", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
open(OUT, "w", encoding="utf-8").write(html)
print("people:", len(people), "events:", len(events), "articles:", len(articles),
      "edges:", len(edges), "html bytes:", len(html))
