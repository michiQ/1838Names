import json, re, sqlite3
from difflib import SequenceMatcher
people=json.load(open('/tmp/ugrr/extracted_people.json'))
tbl=json.load(open('/tmp/ugrr/chapter_table.json')); CT={t['i']:t for t in tbl}
con=sqlite3.connect('/tmp/bm.db'); con.row_factory=sqlite3.Row
CUR=('winch','newspaper','dissertation','nolibs')
dbp=con.execute(f"SELECT id,canonical_name,source FROM people WHERE source IN {CUR}").fetchall()
def parse(nm):
    nm=nm.strip()
    if ',' in nm:
        s,g=nm.split(',',1); s=s.strip(); gv=[x for x in re.split(r'[ .]+',g.strip()) if x]
    else:
        t=[x for x in re.split(r'[ .]+',nm) if x]
        t=[x for x in t if x.lower().rstrip('.') not in ('mr','mrs','miss','dr','rev','esq','jr','sr','hon','capt','col','gen','uncle','aunt')]
        if not t: return None
        s=t[-1]; gv=t[:-1]
    return s,gv
idx={}; surcount={}
for r in dbp:
    pr=parse(r['canonical_name'])
    if not pr: continue
    s,gv=pr; surcount[s.lower()]=surcount.get(s.lower(),0)+1
    if gv: idx.setdefault(s.lower(),[]).append((r['id'],r['canonical_name'],gv,r['source']))
def close(a,b):
    a,b=a.lower(),b.lower()
    if a==b: return True
    if len(a)>=5 and len(b)>=5 and abs(len(a)-len(b))<=1: return SequenceMatcher(None,a,b).ratio()>=0.86
    return False
def giv_ok(g1,g2,rare):
    a,b=g1[0],g2[0]
    if close(a,b): return True
    if rare and (len(a)<=2 or len(b)<=2) and a[0].lower()==b[0].lower(): return True
    return False
def canon(nm):
    pr=parse(nm)
    if not pr: return None
    s,gv=pr; return (s+', '+' '.join(gv)).strip(', ') if gv else s
person={}
def add(key,find,name,title,page):
    e=person.setdefault(key,{'find':find,'name':name,'chapters':set()}); e['chapters'].add((title,page))
for p in people:
    cn=canon(p['canonical'])
    if not cn: continue
    s,gv=parse(p['canonical'])
    if not gv: continue
    ct=CT.get(p['chapter_i'])
    if not ct: continue
    title,page=ct['title'],ct['page']; role=p.get('role','freedom_seeker'); did=False
    if role=='helper':
        rare=surcount.get(s.lower(),0)<=1; cands=[]
        for key in idx:
            if close(key,s):
                kr=surcount.get(key,0)<=1
                for (pid,nm,dgv,src) in idx[key]:
                    if giv_ok(gv,dgv,rare and kr): cands.append((pid,nm,src))
        if len({c[0] for c in cands})==1:
            pid,nm,src=cands[0]; add(f'pid:{pid}',{'name':nm,'source':src},nm,title,page); did=True
    if not did:
        if role=='helper' and all(len(g.strip('.'))<=2 for g in gv): continue
        find={'create':{'name':cn,'source':'ugrr'}}
        if p.get('aliases'):
            al='; '.join(a for a in p['aliases'] if a and len(a)>1)
            if al: find['create']['aliases']=al
        add(f'new:{cn.lower()}',find,cn,title,page)
r=con.execute("SELECT id FROM people WHERE canonical_name='Ash, Sarah' AND source='winch'").fetchone()
if r: add(f'pid:{r["id"]}',{'name':'Ash, Sarah','source':'winch'},'Ash, Sarah','Woman Escaping in a Box',608)
appearances=[]
for key,e in person.items():
    for (title,page) in sorted(e['chapters'],key=lambda x:x[1]):
        appearances.append({'find':e['find'],'chapter':title,'page':page})
json.dump({'appearances':appearances}, open('/tmp/ugrr/ugrr_appearances.json','w'), indent=1, ensure_ascii=False)
nnew=len({k for k in person if k.startswith('new:')}); nlinked=len({k for k in person if k.startswith('pid:')})
print(f"persons {len(person)} | linked {nlinked} | new {nnew} | appearances {len(appearances)}")
