# Stability check: md5 of people, appearances, directory_links in the rebuilt db. Two rebuilds in a row must print the same lines.
import sqlite3,hashlib
import os
c=sqlite3.connect(os.environ.get('BM_DB','/tmp/black_metropolis.db'))
for t,q in [('people','select id,canonical_name,source,aliases from people order by id'),('appearances','select person_id,article_id,event_id,role,issue_id from appearances order by 1,2,3,4,5'),('directory_links','select * from directory_links order by 1,2,3')]:
    print(t,hashlib.md5(repr(c.execute(q).fetchall()).encode()).hexdigest())
