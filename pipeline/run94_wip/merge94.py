import json,re
A=[];E=[];N=[];F=[]
for l in 'ABC':
    d=json.load(open('/tmp/repo/pipeline/run94_wip/ext_%s.json'%l))
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
MON={'10':'October','11':'November','12':'December'}
def fold(k,d,key='attendees',text=True):
    addp(k,d,key)
    if text and key=='attendees':
        i=d['issue'][8:]; k['description']+=' || From the Christian Recorder of %s %d, 1865, page %s: '%(MON[i[:2]],int(i[3:]),d['page'])+d['description'].split(' || ')[0]
    (E if key=='attendees' else A).remove(d)
# reprinted notices and repeat ads: keep the first printing, carry names over
for (i1,p1,i2,p2) in [
 ('10-07','Information Wanted (Richard Parker)','11-04','Information Wanted (Richard Parker)'),
 ('10-28',"Colored Soldiers' and Seamen's U. S. Government Claim Office",'11-04',"Colored Soldiers' and Seamen's U.S. Government Claim Office"),
 ('10-28',"Colored Soldiers' and Seamen's U. S. Government Claim Office",'12-09',"Colored Soldiers' and Seamen's U.S. Government Claim Office"),
 ('10-21','Dr. David Rosell','11-04','Dr. David Rosell'),
 ('10-14','New Fall and Winter Dry Goods','11-11','S. Shorter Hawkins, New Fall'),
 ('10-14','New Fall and Winter Dry Goods','12-09','S. Shorter Hawkins: New Fall'),
 ('11-04','U.S. Agency for Colored Soldiers','12-09','U.S. Agency for Colored Soldiers'),
 ('12-02','Joseph H. Cole, Continental','12-09','Joseph H. Cole, Continental'),
 ('12-16',"Wm. H. Davis's 'Amateur's Companion'",'12-23',"Wm. H. Davis's 'Amateur's Companion'"),
 ('12-16',"Wm. H. Davis's 'Amateur's Companion'",'12-30',"Wm. H. Davis, Amateur's Companion"),
 ('11-04','A Grand Location for our Book Concern','12-09','A Grand Location for our Book Concern'),
 ('12-02',"An Appeal: Ladies' Union Sewing Circle",'12-09',"An Appeal: Ladies' Union Sewing Circle")]:
    fold(art(i1,p1),art(i2,p2),'people',False)
A.remove(art('10-07',"Bowers' Coal Depot"))   # T. J. Bowers coal: on the ads page since Runs #92-#93
# one event per occasion
k=ev('10-28','Reception of colored soldiers at Harrisburg')
k['name']='Reception of the colored soldiers of Pennsylvania at Harrisburg (Garnet League), Nov. 14, 1865'
for (i,p) in [('11-04','Complimentary reception to colored soldiers'),('11-18','Harrisburg celebration and procession'),('12-23','Garnet Equal Rights League: reception')]: fold(k,ev(i,p))
k=ev('10-28','Union A. M. E. Church, Coates St.')
k['name']='Union A.M.E. Church, Coates St.: all-day services and debt jubilee, Oct. 29, 1865'
for (i,p) in [('11-04','Union A.M.E. Church, special Sabbath'),('11-11','Union A.M.E. Church debt jubilee')]: fold(k,ev(i,p))
k=ev('11-18',"Pennsylvania State Equal Rights' League, annual meeting")
k['name']="Pennsylvania State Equal Rights League: annual meeting at Harrisburg, Aug. 9-10, 1865 (proceedings continued, Nov.-Dec. 1865)"
for (i,p) in [('11-25',"Pennsylvania State Equal Rights' League, annual"),('12-02',"Pennsylvania State Equal Rights' League, annual")]: fold(k,ev(i,p))
k=ev('12-02',"Fair of the Ladies' Union Sewing Circle"); k['date']='1865-12-13'
fold(k,ev('12-09',"Ladies' Union Sewing Circle of Wesley"))
k=ev('12-02','Meeting of the A.M.E. Bishops'); fold(k,ev('12-09','Meeting of the A.M.E. Bishops'))
k=ev('12-16','Welcome-home address'); k['name']='Welcome-home sermon to the returned colored soldiers, Bethel Church, Dec. 10, 1865'
fold(k,ev('12-09','Welcome-home sermon'))
k=ev('11-25','Grand concert for the A.M.E. Church of Wilmington'); fold(k,ev('12-23','Concert by a company of Philadelphia'))
for e in E:
    e['description']=re.sub(r'^(STREETCAR exclusion|PARADE|SOCIETY MEETING|STREETCAR|PROCESSION)[.:]\s*','',e['description'])
for a in A:
    if a['headline'].startswith('James W. Brown, Steam-Dyeing'): a['issue']='CR_1865-12-02'; a['summary']+=' (First printed Dec. 2, 1865, page 4; also Dec. 9.)'
KEEP_AD=('New Fall and Winter Dry Goods (S. Shorter','Joseph H. Cole, Continental','James W. Brown, Steam-Dyeing',"Colored Soldiers' and Seamen's U. S. Government Claim",'U.S. Agency for Colored Soldiers')
for a in A:
    if a['type']=='advertisement' and not a['headline'].startswith(KEEP_AD): a['type']='notice'
# Michiko's rulings, 2026-11-14
for x in A+E:
    for k in ('summary','description'):
        if k in x: x[k]=x[k].replace("John C. Bowers [VERIFY; printed 'Bonors']","John C. Bowers (printed 'Bonors')").replace("Jacob O. White (as printed; probably Jacob C. White, see flags)","Jacob O. White (as printed; Jacob C. White, Jr., per Michiko)")
for x in E:
    if x['issue']=='CR_1865-12-30' and x['name'].startswith('Adjourned public meeting'): x['attendees'].append(['John C. Bowers',"spoke on the resolutions (printed 'Bonors'; John C. Bowers per Michiko)"])
    if x['issue']=='CR_1865-10-21' and x['name'].startswith('Public meeting of the colored citizens of Philadelphia for the National Lincoln'): x['attendees'].append(['Jacob C. White, Jr.',"co-signer of the call (printed 'Jacob O. White'; the son, per Michiko)"])
for x in A:
    if x['issue']=='CR_1865-12-30' and x['headline'].startswith('Meeting of the Colored Citizens'): x['people'].append(['John C. Bowers',"spoke on the resolutions (printed 'Bonors')"])
    if x['issue']=='CR_1865-10-21' and x['headline'].startswith('Notice (public meeting for the National Lincoln'): x['people'].append(['Jacob C. White, Jr.',"co-signer of the call (printed 'Jacob O. White')"])
A.sort(key=lambda a:(a['issue'],a['page'])); E.sort(key=lambda e:(e['issue'],e['page']))
out={"_note":"Christian Recorder Oct 7 - Dec 30, 1865 (Run #94, 2026-11-14). 13 complete issues, 52 pages. Readers A (October), B (November and Dec 2), C (Dec 9-30), one pass each with pages 1 and 4 read column by column from image crops. Names the readers flagged as uncertain are kept in the text only. Reprinted notices and repeat ads were entered once; the Harrisburg reception of Nov 14, the Union A.M.E. debt jubilee, the continued Harrisburg League proceedings, the Wesley fair, the Bishops' meeting, the Bethel welcome-home sermon and the Wilmington concert are each one event; ads without an image box are typed as notices. Michiko's rulings: 'Jacob O. White' (Oct 21) is Jacob C. White, Jr.; 'John C. Bonors' (Dec 30) is John C. Bowers; Union Bethel's 'J. P. Gibbs' is NOT R. P. Gibbs; Mrs. Hawkins's address stays 615 Lombard (515 on Dec 30 is a misprint); H. G. Rhodes and H. J. Rhodes: unknown, kept as printed.",
 "articles":A,"events":E,"notes":N,"flags":F}
json.dump(out,open('/tmp/repo/pipeline/extractions89.json','w'),indent=1,ensure_ascii=False)
print(len(A),len(E),len(N),len(F))
