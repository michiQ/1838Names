"""Topic timeline pages (2026-11-24, Michiko: "a report on the street car discrimination ... a timeline
linked back to the articles"). Called from build_viewer.py after the topic section, so it always uses the
article and event ids of the current build. One page per topic that has a "timeline" entry in
pipeline/topics.json: {"file": "streetcar.html", "title": ..., "intro": ..., "phases": [{"from", "to", "title", "note"}]}.
Each entry links to the database viewer (index.html#a<id> for an article, #e<id> for an event, #p<id> for a person),
to the scanned page, and to the full issue (Drive) and the Internet Archive item where known."""
import html, os, re

PAPERS = {"CA": "Colored American", "PF": "Pennsylvania Freeman", "FJ": "Freedom's Journal",
          "PP": "Philadelphia Tribune (Pencil Pusher)", "NS": "The North Star", "CR": "Christian Recorder",
          "CAM": "Colored American Magazine"}
MONTHS = "January February March April May June July August September October November December".split()


def nice_date(d):
    if not d: return ""
    p = d.split("-")
    try:
        if len(p) == 3: return f"{MONTHS[int(p[1]) - 1]} {int(p[2])}, {p[0]}"
        if len(p) == 2: return f"{MONTHS[int(p[1]) - 1]} {p[0]}"
    except (ValueError, IndexError):
        pass
    return d


_VER_BRACKET = re.compile(r"\s*\[[^\[\]]*?\bVERIFY\b[^\[\]]*\]", re.I)


def clean(s):
    """Same display rule as build_viewer.py: no [VERIFY ...] flags in public pages; no em dashes."""
    s = s or ""
    if "VERIFY" in s or "verify" in s:
        s = _VER_BRACKET.sub("", s)
        s = re.sub(r"\s*;\s*(?=$|[)\],])", "", s)
        s = re.sub(r"\(\s*\)", "", s)
        s = re.sub(r"\s+([,.;)])", r"\1", s)
        s = re.sub(r"  +", " ", s).strip()
    return s.replace(" \u2014 ", ", ").replace("\u2014", ", ")


def esc(s): return html.escape(clean(s), quote=True)


def short(s, n=420):
    s = clean(s).strip()
    if len(s) <= n: return s
    cut = s[:n].rsplit(" ", 1)[0]
    return cut.rstrip(",;:") + " ..."


CSS = """:root{--bg:#f3ede2;--panel:#fbf8f2;--ink:#2a2118;--dim:#6f6352;--line:#d9cfbd;--gold:#8a6418;--sel:#efe3c9;--rust:#a5472a;--teal:#2f6f68;
  --display:"Libre Caslon Display","Libre Caslon Text",Georgia,serif;--body:"Libre Caslon Text",Georgia,serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 var(--body)}
a{color:var(--gold)}
.top{display:flex;align-items:center;gap:12px;padding:10px 16px;border-bottom:1px solid var(--line);background:var(--panel);position:sticky;top:0;z-index:5}
.top a.back{background:var(--sel);color:var(--ink);border:1px solid var(--gold);border-radius:4px;font:13px var(--body);padding:6px 12px;text-decoration:none}
.top .ttl{font:12px var(--mono);letter-spacing:.12em;color:var(--dim)}
main{max-width:900px;margin:0 auto;padding:22px 16px 56px}
.eyebrow{font:11px var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--dim)}
h1{font:400 clamp(30px,5vw,44px)/1.08 var(--display);margin:6px 0 12px;text-wrap:balance}
.lede{max-width:70ch;margin:0 0 10px}
.read{background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:10px 14px;margin:14px 0}
.stats{font:12px var(--mono);color:var(--dim);margin:6px 0 4px}
nav.jump{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0 6px}
nav.jump a{font:12px var(--mono);border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:999px;padding:5px 11px;text-decoration:none}
nav.jump a:hover{border-color:var(--gold)}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0 4px}
.chip{font:12px var(--mono);border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:999px;padding:5px 12px;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
#q{font:14px var(--body);padding:7px 12px;border:1px solid var(--line);border-radius:999px;background:var(--panel);color:var(--ink);flex:1 1 200px;max-width:320px;min-width:0}
#q:focus,.chip:focus-visible,a:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
section.phase{margin-top:34px}
section.phase h2{font:400 26px/1.15 var(--display);margin:0 0 4px}
section.phase .pnote{color:var(--dim);margin:0 0 12px;max-width:70ch}
ol.tl{list-style:none;margin:0;padding:0 0 0 22px;border-left:2px solid var(--line)}
ol.tl li{position:relative;margin:0 0 16px;padding:0}
ol.tl li::before{content:"";position:absolute;left:-29px;top:7px;width:12px;height:12px;border-radius:50%;background:var(--panel);border:2px solid var(--gold)}
ol.tl li.ev::before{background:var(--teal);border-color:var(--teal)}
.when{font:600 14.5px var(--mono);color:var(--ink);letter-spacing:.02em}
.when .loc{font-weight:400;font-size:12px;color:var(--dim)}
.kind{font:10.5px var(--mono);text-transform:uppercase;letter-spacing:.12em;border-radius:3px;padding:1px 6px;margin-left:6px;border:1px solid var(--line);color:var(--dim)}
li.ev .kind{color:var(--teal);border-color:var(--teal)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:10px 14px;margin-top:4px}
.card h3{font:700 16px/1.3 var(--body);margin:0 0 4px}
.card h3 a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--gold)}
.card h3 a:hover{color:var(--gold)}
.card p{margin:0 0 6px;font-size:14.5px}
.who{font-size:13.5px;margin:2px 0 6px}
.who a{text-decoration:none;border-bottom:1px dotted var(--gold);color:var(--ink)}
.src{font:11.5px var(--mono);color:var(--dim)}
.foot{font-size:12.5px;color:var(--dim);margin-top:40px;max-width:80ch}
.hide{display:none!important}
.inc{margin:22px 0 8px;padding:16px 16px 12px;background:var(--panel);border:1px solid var(--line);border-radius:4px}
.inc h2{font:400 26px/1.15 var(--display);margin:0 0 6px}
.inc .lede{font-size:14.5px;color:var(--ink)}
.tiles{display:flex;flex-wrap:wrap;gap:10px 28px;margin:10px 0 6px}
.tile b{display:block;font:400 40px/1 var(--display);color:var(--ink)}
.tile span{font:11.5px var(--mono);color:var(--dim);letter-spacing:.04em}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;font:12px var(--mono);color:var(--dim);margin:12px 0 2px}
.legend i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:6px;vertical-align:-1px}
.chartwrap{position:relative}
svg.chart{width:100%;height:auto;display:block;overflow:visible}
svg.chart .bar{cursor:pointer}
svg.chart .bar .hit{fill:transparent}
svg.chart .bar:hover .hit,svg.chart .bar:focus .hit{fill:rgba(138,100,24,.08)}
svg.chart .bar[aria-pressed="true"] .hit{fill:rgba(138,100,24,.16)}
svg.chart .bar:focus{outline:none}
svg.chart text{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;fill:var(--dim)}
svg.chart text.v{fill:var(--ink);font-weight:500}
#tip{position:absolute;pointer-events:none;background:var(--ink);color:var(--bg);font:12px/1.4 var(--body);padding:6px 9px;border-radius:4px;max-width:260px;opacity:0;transition:opacity .1s;z-index:3}
.hint{font:11.5px var(--mono);color:var(--dim);margin:4px 0 0}
details.ilist{margin-top:12px}
details.ilist summary{cursor:pointer;font:13px var(--mono);color:var(--gold)}
details.ilist ol{margin:10px 0 0;padding-left:22px;font-size:14px}
details.ilist li{margin:0 0 7px}
details.ilist .pl{font:11px var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--dim)}
.ibadge{font-size:13.5px;margin:0 0 6px;padding:5px 9px;border-left:3px solid var(--rust);background:#f6eadf}
.ibadge.o{border-left-color:#2a7fa8;background:#e9f0f4}
#yf{font:12px var(--mono);color:var(--dim)}
#yf button{font:12px var(--mono);background:none;border:0;color:var(--gold);text-decoration:underline;cursor:pointer;padding:0 0 0 6px}
@media (max-width:600px){ol.tl{padding-left:16px}ol.tl li::before{left:-23px}
  svg.chart text{font-size:25px}svg.chart text.v{font-size:28px}svg.chart text.g{font-size:17px}.tile b{font-size:32px}.inc{padding:14px 12px 10px}}"""


def make(cfg, topic, articles, events, people, issues, urls, ia_urls, jpeg_slugs, out_dir):
    idate = {v["slug"]: (v["date"] or "") for v in issues.values()}
    jpeg = set(jpeg_slugs)
    items = []
    for aid in topic["articles"]:
        a = articles[aid]
        items.append({"k": "a", "id": aid, "date": idate.get(a["issue"]) or "", "title": a["hl"], "text": a.get("sum") or "",
                      "issue": a["issue"], "pg": a["pg"], "ppl": a.get("ppl", []), "ty": a.get("ty") or ""})
    for eid in topic["events"]:
        e = events[eid]
        d = e.get("date") or idate.get(e["issue"]) or ""
        items.append({"k": "e", "id": eid, "date": d, "title": e["name"], "text": e.get("desc") or "",
                      "issue": e["issue"], "pg": e["pg"], "ppl": e.get("att", []), "loc": e.get("loc") or ""})
    items.sort(key=lambda x: (x["date"] or "9999", 0 if x["k"] == "e" else 1, x["pg"] or 0))

    phases = cfg.get("phases") or [{"from": "0000", "to": "9999", "title": "Timeline"}]
    def phase_of(d):
        for i, p in enumerate(phases):
            if p["from"] <= (d or "9999") <= p["to"] + "~": return i
        return len(phases) - 1

    def src_line(it):
        slug, pg = it["issue"], it["pg"]
        if not slug: return ""
        paper = PAPERS.get(slug.split("_")[0], slug.split("_")[0])
        bits = [f"{esc(paper)}, {esc(nice_date(idate.get(slug)))}" + (f", p. {pg}" if pg else "")]
        if slug in jpeg and pg: bits.append(f'<a href="pages/{esc(slug)}_p{pg}.jpg" target="_blank" rel="noopener">scanned page</a>')
        if urls.get(slug): bits.append(f'<a href="{esc(urls[slug])}" target="_blank" rel="noopener">full issue</a>')
        if ia_urls.get(slug): bits.append(f'<a href="{esc(ia_urls[slug])}" target="_blank" rel="noopener">Internet Archive</a>')
        return " &middot; ".join(bits)

    def who(it):
        seen, out = set(), []
        for pid, role in it["ppl"]:
            if pid in seen or pid not in people: continue
            seen.add(pid)
            nm = people[pid]["name"]
            out.append(f'<a href="index.html#p{pid}" title="{esc(role)}">{esc(nm)}</a>')
        if not out: return ""
        more = ""
        if len(out) > 14: more = f" and {len(out) - 14} more"; out = out[:14]
        return f'<div class="who">Named: {", ".join(out)}{more}</div>'

    # Incidents (2026-11-24, Michiko: "a chart of ejections ... so people can quickly see the numbers").
    # Hand-classified from the summaries in topics.json "incidents"; each points at one timeline entry.
    PH, OTHER = "#a5472a", "#2a7fa8"
    incs = []
    for n, x in enumerate(cfg.get("incidents", [])):
        r = x["ref"]
        if "a" in r:
            hit = [i for i in topic["articles"] if articles[i]["issue"] == r["a"]["issue"] and articles[i]["hl"] == r["a"]["headline"]]
            key = ("a", hit[0]) if hit else None
        else:
            hit = [i for i in topic["events"] if (events[i]["issue"] or "") == (r["e"]["issue"] or "") and events[i]["name"] == r["e"]["name"]]
            key = ("e", hit[0]) if hit else None
        if not key: raise SystemExit(f"timeline incident has no entry in the topic: {x}")
        incs.append(dict(x, key=key, n=n + 1))
    inc_by_item = {}
    for x in incs: inc_by_item.setdefault(x["key"], []).append(x)

    secs = [[] for _ in phases]
    for it in items: secs[phase_of(it["date"])].append(it)

    body = []
    nav = []
    for i, (p, lst) in enumerate(zip(phases, secs)):
        if not lst: continue
        nav.append(f'<a href="#ph{i}">{esc(p["title"])}</a>')
        lis = []
        for it in lst:
            link = f'index.html#{it["k"]}{it["id"]}'
            kind = "Event" if it["k"] == "e" else ("Article" if it.get("ty") not in ("advertisement", "notice") else it["ty"].capitalize())
            when = esc(nice_date(it["date"])) or "date unknown"
            if it.get("loc"): when += f' <span class="loc">&middot; {esc(it["loc"])}</span>'
            search = esc((it["title"] + " " + it["text"] + " " + " ".join(people[p]["name"] for p, _ in it["ppl"] if p in people)).lower())
            mine = inc_by_item.get((it["k"], it["id"]), [])
            badges = "".join(f'<div class="ibadge{"" if x["place"] == "Philadelphia" else " o"}"><b>Incident {x["n"]}</b>, {esc(x["when"])}: {esc(x["what"])}</div>' for x in mine)
            iy = " ".join(str(x["y"]) for x in mine)
            lis.append(f'<li id="i{it["k"]}{it["id"]}" class="{"ev" if it["k"] == "e" else "ar"}" data-k="{it["k"]}" data-iy="{iy}" data-s="{search}">'
                       f'<div class="when">{when}<span class="kind">{kind}</span></div>'
                       f'<div class="card">{badges}<h3><a href="{link}" title="Open in the database">{esc(it["title"])}</a></h3>'
                       f'<p>{esc(short(it["text"]))}</p>{who(it)}<div class="src">{src_line(it)}</div></div></li>')
        body.append(f'<section class="phase" id="ph{i}"><h2>{esc(p["title"])}</h2>'
                    + (f'<p class="pnote">{esc(p["note"])}</p>' if p.get("note") else "")
                    + f'<ol class="tl">{"".join(lis)}</ol></section>')

    links = "".join(f'<div class="read"><b>Read more:</b> <a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["title"])}</a>'
                    f' <span class="src">({esc(l.get("source", ""))})</span></div>' for l in topic.get("links", []))
    chart = ""
    if incs:
        years = sorted({x["y"] for x in incs})
        cnt = {y: [sum(1 for x in incs if x["y"] == y and x["place"] == "Philadelphia"),
                   sum(1 for x in incs if x["y"] == y and x["place"] != "Philadelphia")] for y in years}
        W, H, top, base, left = 860, 250, 24, 210, 34
        mx = max(sum(v) for v in cnt.values())
        unit = (base - top) / max(mx, 1)
        # one slot per year that has an incident; a narrow labelled gap where years are skipped
        slots, prev = [], None
        for y in years:
            if prev is not None and y - prev > 1: slots.append(("gap", y - prev - 1))
            slots.append(("y", y)); prev = y
        sw = (W - left - 10) / (sum(1 if k == "y" else 0.8 for k, _ in slots))
        bw = min(46, sw * 0.62)
        g, x0 = [], left
        for y in range(2, mx + 1, 2):
            yy = base - y * unit
            g.append(f'<line x1="{left}" x2="{W - 10}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#e6dccb" stroke-width="1"/>'
                     f'<text x="{left - 8}" y="{yy + 4:.1f}" text-anchor="end" font-size="11">{y}</text>')
        for k, v in slots:
            if k == "gap":
                w = sw * 0.8
                g.append(f'<text x="{x0 + w / 2:.1f}" y="{base - 8}" text-anchor="middle" font-size="11">&#8943;</text>'
                         f'<text x="{x0 + w / 2:.1f}" y="{base + 18}" text-anchor="middle" font-size="10" class="g">{v} yrs</text>')
                x0 += w; continue
            ph, ot = cnt[v]; cx = x0 + sw / 2; bx = cx - bw / 2
            parts = []
            h1 = ph * unit; h2 = ot * unit
            def seg(yb, h, col, rounded):
                if h <= 0: return ""
                yt = yb - h
                if not rounded: return f'<rect x="{bx:.1f}" y="{yt:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{col}"/>'
                r = min(4, h, bw / 2)
                return (f'<path d="M{bx:.1f},{yb:.1f} V{yt + r:.1f} Q{bx:.1f},{yt:.1f} {bx + r:.1f},{yt:.1f} H{bx + bw - r:.1f} '
                        f'Q{bx + bw:.1f},{yt:.1f} {bx + bw:.1f},{yt + r:.1f} V{yb:.1f} Z" fill="{col}"/>')
            parts.append(seg(base, h1, PH, ot == 0))
            parts.append(seg(base - h1 - (2 if ph and ot else 0), h2 - (2 if ph and ot else 0) if ph and ot else h2, OTHER, True))
            tot = ph + ot
            lab = f"{v}: {tot} incident{'s' if tot != 1 else ''}" + (f", {ph} in Philadelphia" if ph and ot else (" in Philadelphia" if ph else " elsewhere"))
            g.append(f'<g class="bar" tabindex="0" role="button" aria-pressed="false" data-y="{v}" data-tip="{esc(lab)}" aria-label="{esc(lab)}. Show these on the timeline">'
                     f'<rect class="hit" x="{x0 + 2:.1f}" y="{top - 16}" width="{sw - 4:.1f}" height="{base - top + 40}" rx="4"/>'
                     + "".join(parts)
                     + f'<text class="v" x="{cx:.1f}" y="{base - tot * unit - 7:.1f}" text-anchor="middle" font-size="13">{tot}</text>'
                     f'<text x="{cx:.1f}" y="{base + 18}" text-anchor="middle" font-size="12">{v}</text></g>')
            x0 += sw
        g.append(f'<line x1="{left}" x2="{W - 10}" y1="{base}" y2="{base}" stroke="#bfb29b" stroke-width="1"/>')
        nph = sum(1 for x in incs if x["place"] == "Philadelphia")
        first_ph = min((x for x in incs if x["place"] == "Philadelphia"), key=lambda x: x["y"])
        rows = "".join(f'<li><span class="pl">{esc(x["place"])}</span> &middot; <b>{esc(x["when"])}</b>: {esc(x["what"])} '
                       f'(<a href="#i{x["key"][0]}{x["key"][1]}">on the timeline</a> &middot; <a href="index.html#{x["key"][0]}{x["key"][1]}">in the database</a>)</li>'
                       for x in incs)
        chart = f"""<section class="inc" aria-labelledby="inch"><h2 id="inch">Riders put off, refused and attacked</h2>
<div class="tiles"><div class="tile"><b>{len(incs)}</b><span>incidents found so far</span></div>
<div class="tile"><b>{nph}</b><span>in Philadelphia</span></div>
<div class="tile"><b>{first_ph["y"]}</b><span>earliest in Philadelphia so far</span></div></div>
<p class="lede">{esc(cfg.get("incidents_intro", ""))}</p>
<div class="legend"><span><i style="background:{PH}"></i>Philadelphia ({nph})</span><span><i style="background:{OTHER}"></i>Elsewhere ({len(incs) - nph})</span></div>
<div class="chartwrap"><svg class="chart" viewBox="0 0 {W} {H}" role="group" aria-label="Incidents by year. Select a year to show its incidents on the timeline.">{"".join(g)}</svg><div id="tip" role="tooltip"></div></div>
<p class="hint">Select a bar to show that year's incidents in the timeline below.</p>
<details class="ilist"><summary>See all {len(incs)} incidents as a list</summary><ol>{rows}</ol></details></section>"""

    na, ne = len(topic["articles"]), len(topic["events"])
    yrs = [it["date"][:4] for it in items if it["date"]]
    span = f"{min(yrs)} to {max(yrs)}" if yrs else ""
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(cfg.get("title", topic["label"]))} &middot; 1838 Black Metropolis</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="top"><a class="back" href="index.html#t-{esc(topic["slug"])}">&#8592; Database</a><span class="ttl">1838 BLACK METROPOLIS &middot; TIMELINE</span></div>
<main>
<div class="eyebrow">A topic in the 1838 Names Database</div>
<h1>{esc(cfg.get("title", topic["label"]))}</h1>
<p class="lede">{esc(cfg.get("intro") or topic.get("note", ""))}</p>
<div class="stats">{na} articles &middot; {ne} events &middot; {esc(span)}</div>
{chart}
{links}
<nav class="jump" aria-label="Jump to a period">{"".join(nav)}</nav>
<div class="controls"><input id="q" type="search" placeholder="Search names, places, words" aria-label="Search the timeline">
<button class="chip" data-f="all" aria-pressed="true">All</button><button class="chip" data-f="e" aria-pressed="false">Events</button><button class="chip" data-f="a" aria-pressed="false">Articles</button>{'<button class="chip" data-f="inc" aria-pressed="false">Incidents</button>' if incs else ''}
<span class="stats" id="cnt"></span><span id="yf"></span></div>
{"".join(body)}
<p class="foot">Each entry opens in the database, where the people named link to everything else we know about them. Dates are the event date when the paper gives one, otherwise the issue date. Summaries come from our reading of the microfilm; names we could not read with certainty are left out of the links. Click "scanned page" to read the original.</p>
</main>
<script>
(function(){{
  var lis=[].slice.call(document.querySelectorAll('ol.tl li')), q=document.getElementById('q'), cnt=document.getElementById('cnt'), yf=document.getElementById('yf'), f='all', yr='';
  var bars=[].slice.call(document.querySelectorAll('svg.chart .bar'));
  function run(){{ var t=(q.value||'').toLowerCase().trim(), n=0;
    lis.forEach(function(li){{ var iy=li.dataset.iy||'';
      var kind = f==='all' || (f==='inc' ? iy!=='' : li.dataset.k===f);
      var yok = !yr || (' '+iy+' ').indexOf(' '+yr+' ')>=0;
      var ok=kind&&yok&&(!t||li.dataset.s.indexOf(t)>=0); li.classList.toggle('hide',!ok); if(ok)n++; }});
    document.querySelectorAll('section.phase').forEach(function(s){{ s.classList.toggle('hide', !s.querySelector('li:not(.hide)')); }});
    cnt.textContent = n+' shown';
    yf.innerHTML = yr ? 'incidents of '+yr+'<button type="button" id="yclr">show all</button>' : '';
    var c=document.getElementById('yclr'); if(c) c.onclick=function(){{ setYear(''); }};
    bars.forEach(function(b){{ b.setAttribute('aria-pressed', b.dataset.y===yr?'true':'false'); }}); }}
  function setChip(v){{ f=v; document.querySelectorAll('.chip').forEach(function(c){{ c.setAttribute('aria-pressed', c.dataset.f===v?'true':'false'); }}); }}
  function setYear(y){{ yr=y; if(y) setChip('inc'); run();
    if(y){{ var first=lis.filter(function(li){{ return !li.classList.contains('hide'); }})[0]; if(first) first.scrollIntoView({{behavior:'smooth',block:'start'}}); }} }}
  q.addEventListener('input',run);
  document.querySelectorAll('.chip').forEach(function(b){{ b.addEventListener('click',function(){{ setChip(b.dataset.f); if(b.dataset.f!=='inc') yr=''; run(); }}); }});
  var tip=document.getElementById('tip'), wrap=document.querySelector('.chartwrap');
  bars.forEach(function(b){{
    b.addEventListener('click',function(){{ setYear(yr===b.dataset.y?'':b.dataset.y); }});
    b.addEventListener('keydown',function(e){{ if(e.key==='Enter'||e.key===' '){{ e.preventDefault(); setYear(yr===b.dataset.y?'':b.dataset.y); }} }});
    function show(){{ var r=b.getBoundingClientRect(), w=wrap.getBoundingClientRect(); tip.textContent=b.dataset.tip;
      tip.style.left=Math.max(0,Math.min(w.width-tip.offsetWidth, r.left-w.left+r.width/2-tip.offsetWidth/2))+'px'; tip.style.top=(r.top-w.top-34)+'px'; tip.style.opacity=1; }}
    b.addEventListener('mouseenter',show); b.addEventListener('focus',show);
    b.addEventListener('mouseleave',function(){{ tip.style.opacity=0; }}); b.addEventListener('blur',function(){{ tip.style.opacity=0; }});
  }});
  run();
}})();
</script>
</body>
</html>
"""
    open(os.path.join(out_dir, cfg["file"]), "w", encoding="utf-8").write(page)
    return len(items)
