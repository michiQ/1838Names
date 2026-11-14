import json
A=[];E=[];N=[];F=[]
for l in 'ABC':
    d=json.load(open('/tmp/repo/pipeline/run93_wip/ext_%s.json'%l))
    A+=d['articles'];E+=d['events']
    N+=['[Reader %s] %s'%(l,x) for x in d.get('notes',[])]
    F+=['[Reader %s] %s'%(l,x) for x in d.get('flags',[])]
def art(issue,pre): 
    r=[a for a in A if a['issue']=='CR_1865-'+issue and a['headline'].startswith(pre)]
    assert len(r)==1,(issue,pre,len(r)); return r[0]
def ev(issue,pre):
    r=[e for e in E if e['issue']=='CR_1865-'+issue and e['name'].startswith(pre)]
    assert len(r)==1,(issue,pre,len(r)); return r[0]
def addp(dst,src,key):
    seen={p[0] for p in dst.get(key,[])}
    for p in src.get(key,[]):
        if p[0] not in seen: dst.setdefault(key,[]).append(p); seen.add(p[0])
# reprinted notices and repeat ads: keep the first printing, carry names over
for (i1,p1,i2,p2) in [
 ('07-22','Information Wanted (Edith','08-05','Information Wanted (Edith'),
 ('07-22','Minutes of P. S. E. R.','08-05','Minutes of P. S. E. R.'),
 ('07-15','Notice to the Afflicted','08-05','Notice to the Afflicted'),
 ('07-22','Notice (Annual Meeting of the Penn','08-05','Annual Meeting of the Penn'),
 ('07-15','The Colored People','09-02','The Colored People'),
 ('08-19','Special Notice. Bureau','09-02','Special Notice. Bureau'),
 ('08-19','Notice (celebration of benevolent','09-02','Notice (celebration of benevolent'),
 ('08-26','Information Wanted (Daniel','09-02','Information Wanted (Daniel')]:
    k=art(i1,p1); d=art(i2,p2); addp(k,d,'people'); A.remove(d)
A.remove(art('09-23','Trimmings and Fancy Goods'))   # Georgina Gleaves card, on the ads page since June 3
for (i1,p1,i2,p2) in [
 ('07-22','Pennsylvania State Equal Rights League: Annual','08-05','Pennsylvania State Equal Rights League -- annual meeting called'),
 ('08-19','Celebration of several','09-02','Celebration of several')]:
    k=ev(i1,p1); d=ev(i2,p2); addp(k,d,'attendees'); E.remove(d)
# Apple Dumpling Festival: one event, at the corrected date
k=ev('08-12','Apple Dumpling'); d=ev('08-05','Apple Dumpling'); addp(k,d,'attendees'); E.remove(d)
k['name']='Apple Dumpling Festival, A.M.E. Wesley Church (Hurst Street)'
# Bethel Sabbath School excursion: announcement folded into the report
k=ev('09-02','Bethel A. M. E. Sabbath School excursion'); d=ev('08-26','Bethel Sabbath School'); addp(k,d,'attendees'); E.remove(d)
# Harrisburg annual meeting: three instalments, one event
k=ev('08-26','Pennsylvania State Equal Rights League -- annual meeting at Harrisburg')
for (i,p) in [('08-19','Pennsylvania State Equal Rights League -- annual meeting at Harrisburg'),('09-02',"Pennsylvania State Equal Rights' League, annual meeting")]:
    d=ev(i,p); addp(k,d,'attendees')
    k['description']+=' || From the Christian Recorder of %s, page %s: '%({'08-19':'August 19','09-02':'September 2'}[i],d['page'])+d['description'].split(' || ')[0]
    E.remove(d)
k['name']='Pennsylvania State Equal Rights League: annual meeting at Harrisburg'
# ads with no image box are typed as notices
for a in A:
    if a['type']=='advertisement' and not a['headline'].startswith(('Coal Yard','Stove Store (','Mrs. Amelia','New Grocery')): a['type']='notice'
import re
for e in E:
    e['description']=re.sub(r'^(STREETCAR exclusion|PARADE|SOCIETY MEETING|STREETCAR|PROCESSION)[.:]\s*','',e['description'])
# the memoir, the tributes and the death are one man: file them together
for a in A:
    for p in a.get('people',[]):
        if p[0]=='James Henry Wilson': p[0]='James H. Wilson'
for e in E:
    for p in e.get('attendees',[]):
        if p[0]=='James Henry Wilson': p[0]='James H. Wilson'
A.sort(key=lambda a:(a['issue'],a['page'])); E.sort(key=lambda e:(e['issue'],e['page']))
out={"_note":"Christian Recorder Jul 1 - Sep 30, 1865 (Run #93, 2026-11-14). 14 issues, 54 pages: Sept 16 (No. 37) lacks pages 1-2 (library card 'first sheet missing'); the film has a second exposure of Sept 23 page 3. Readers A (July), B (August), C (September), one pass each with pages 1 and 4 read from image crops. Names the readers flagged as uncertain are kept in the text only. Reprinted notices and repeat ads were entered once; the three instalments of the Harrisburg Equal Rights League meeting are one event; ads without an image box are typed as notices.",
 "articles":A,"events":E,"notes":N,"flags":F}
json.dump(out,open('/tmp/repo/pipeline/extractions88.json','w'),indent=1,ensure_ascii=False)
print(len(A),len(E),len(N),len(F))
