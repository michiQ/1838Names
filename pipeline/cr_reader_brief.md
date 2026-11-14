# Extraction brief: Christian Recorder, October - December 1865

You are extracting names, articles and events from issues of *The Christian Recorder*
(Philadelphia, organ of the A.M.E. Church; Rev. Elisha Weaver, General Book Steward/editor;
office and AME Book Depository at No. 619 Pine Street) for the **1838 Black Metropolis names
database**, a public-history project recovering the free Black community of antebellum
Philadelphia (c. 1780-1865). The owner is a historian who values source-critical rigor: a wrong
name is worse than a missing one, and every uncertainty must be flagged, not smoothed over.

## Inputs (scratch dir S = /tmp/claude-0/-home-claude/19f25cf0-1195-5d2b-a392-127587d9c568/scratchpad/cr94)
- OCR text: `S/txt/CR_<date>_p<N>.txt` -- one file per page, 7 columns per page separated by
  `[column N]` markers, top to bottom within each column. Microfilm OCR: names are often garbled.
- Page images: `S/jpg/CR_<date>_p<N>.jpg` (2000px wide, whole page). For READING names you need
  higher resolution: render a crop from the source PDF instead. Frame numbers: ALWAYS look the frame up in S/jobs.txt
  ('frame:slug:page'). Pages not in jobs.txt DO NOT EXIST in our copy. Cite by DATE and the issue page (1-4).
  October-December 1865 (Vol. V, Nos. 40-52): 13 complete issues, four frames each, nothing missing: Oct 7 (frames 1-4),
  Oct 14 (5-8), Oct 21 (9-12), Oct 28 (13-16), Nov 4 (17-20), Nov 11 (21-24), Nov 18 (25-28), Nov 25 (29-32), Dec 2 (33-36),
  Dec 9 (37-40), Dec 16 (41-44), Dec 23 (45-48), Dec 30 (49-52). Crops: render from the PDF with
  ```
  python3 S/crop.py <frame> <x0frac> <y0frac> <x1frac> <y1frac> <out.png>
  ```
  then Read the png. Write your crops into a folder of your own, `S/crops_<your-label>/`. A single column is ~1/7 of the width;
  crops of ~1/7 width x ~1/5 height read comfortably. This file's scans are 600 ppi with small pages: crop.py renders at
  DPI=1000 by default; use `DPI=1200 python3 S/crop.py ...` for rechecks. Run ONE crop at a time (two other readers share the
  machine). Use the 2000px JPEG (also cropped, e.g. with PIL) to locate things first.
- OCR and image of a page should be used together: OCR to find what is there, the image to read
  names, addresses and numbers exactly.
- READ PAGES 1 AND 4 OF EVERY ISSUE IN FULL FROM IMAGE CROPS, column by column (7 columns, about five slices each, ONE column per crop, not two-column or wider strips), on your
  FIRST pass. Do NOT triage these pages from the OCR text or from headings. In the last run all three readers triaged them and
  had to be sent back; a report that says pages 1 and 4 were not read in full will be sent back again. Page 1 carries letters
  and church news, page 4 the ads and notices. Read the local, notice, marriage, death and advertisement columns of pages 2 and 3
  from crops as well, and the foot of page 3. This is slow work: expect well over an hour, and take the time.
- SAVE YOUR JSON AFTER EACH ISSUE (rewrite the whole file each time), so nothing is lost if you are interrupted.
- In your report, list exactly which pages and columns you read from the image and which you could not read. Never write in
  the JSON that a page was read in full unless every strip was viewed.

## Extraction rule (the owner's, for this paper)
Philadelphia-focused deep read:
- CAPTURE: Philadelphia AME and other Black church affairs (Bethel, Union, Wesley/Little Wesley,
  St. Thomas, the Presbyterian and Baptist churches, Frankford, West Philadelphia, Germantown);
  Philadelphia Annual Conference business; meetings, societies, lodges, benevolent and literary
  associations, Sabbath schools, schools (Institute for Colored Youth etc.); notices with named
  officers; signed letters and their signers; marriages and deaths; lists of subscribers/agents/
  donors when Philadelphia or nearby (Bristol, Burlington, Camden, Westchester, Frankford,
  Germantown, Norristown, NJ circuits of the Philadelphia Conference count); ADVERTISEMENTS by
  named proprietors with addresses (these are gold: Black businesses and their addresses).
- NON-Philadelphia names (Baltimore, New York, Ohio, Canada, the West, etc.): mention them in the
  description/summary text only. Do NOT list them as linked `attendees`/`people`, because they
  collide with same-named Philadelphia census people. Exception: AME bishops and Philadelphia
  Conference clergy anywhere (Nazrey, Quinn, Payne, Weaver, Campbell, Brown etc.) may be linked.
- SKIP: devotional essays, reprinted sermons/selections, poetry, general/foreign news and
  white-run commercial ads (insurance, railroads, patent medicines) unless a Black Philadelphian
  or a named Black institution is involved. A note in the issue summary that they exist is enough.
- RECURRING ADS: an ad that repeats every week is captured ONCE, at its clearest impression in
  your issues; later repeats are not re-entered (say so in your notes).

## Output: write JSON to `S/ext_<your-label>.json`
```json
{
  "articles": [
    {"issue": "CR_1861-01-19", "page": 2, "headline": "Our City Carriers (notice)",
     "author": "", "type": "notice",
     "summary": "Opening sentences only, lightly cleaned transcription, enough to identify the piece.",
     "people": [["James Wiggins", "city carrier"], ["W. T. Jones", "city carrier"]]}
  ],
  "events": [
    {"issue": "CR_1861-01-19", "page": 2, "name": "Publication Society of Philadelphia -- meeting called",
     "date": "1861-01-21", "location": "No. 619 Pine street, Philadelphia",
     "description": "Substantive: who, what, the roster with roles and addresses as printed.",
     "attendees": [["Mrs. Lawes", "president (as reported)"]]}
  ],
  "notes": ["per-issue observations, OCR rescues (e.g. 'Wiggivs' = WIGGINS), flags"],
  "flags": ["every uncertain reading, with issue/page and what is uncertain"]
}
```
- `type` is one of: advertisement, notice, letter, editorial, report, obituary, marriage, review,
  sermon, article. Marriages/deaths may be grouped one article per issue-page with all couples/
  deceased as `people` (roles like "groom", "bride", "deceased", "officiating minister").
- Article `summary` = the opening few sentences only (owner's rule). Event `description` =
  substantive, carrying the roster and context.
- `author` = the signer, plain name (e.g. "W. Nazrey"), or "" if unsigned/editorial.
- `people`: everyone named IN an article who is not its author and is in scope (ad proprietors,
  obituary subjects, persons in a notice). Without this field they are invisible in the database.
- NAME FORMAT for `people`/`attendees`: the name as printed, WITHOUT honorifics: "Peter Gardiner"
  not "Rev. Peter Gardiner"; put "Rev."/"Bishop"/"Dr." into the role ("pastor (Rev.)"). Keep
  "Mrs."/"Miss"/"Mr." only when there is no given name ("Mrs. Lawes"). Keep initials as printed
  ("W. T. Jones"). Expand nothing you cannot see; do not normalize spellings.
- Dates ISO (yyyy-mm-dd) when the date of the event is stated or computable; else omit `date`.

## Already captured in Runs #74-#88 (1861, 1862, 1863 and January-June 1864; nothing after June 25, 1864 is in the database yet) -- do NOT re-enter unless changed
Recurring: Book Depository of the AME Church (619 Pine; E. Weaver); city carriers James Wiggins & W. T. Jones; Ellis J. Peer's
Fine Cake Bakery (South St.); Mrs. H. S. Duterte, undertaker (634 Lombard); Thomas W. Allmond, furnishing undertaker (1027
Rodman); A. Burris, teacher of vocal music; teachers of the piano; Daughters of Cornish Society standing notice; Nazrey's
"Episcopal Appointments"; "Our Disciplines" appeal; James Downs, clothing; Hope Grand Union (Daughters of Temperance)
notice; Miss Mary Still's school, Clarksborough; hymn-book and carrier notices; the full 1861 Philadelphia Conference
appointments; Wm. Still, coal and stoves (107 N. Fifth); Mrs. E. A. Palmer, trimmings (N. Fifth); the Grand United Order
of Brothers and Sisters of Love and Charity officer list; the Rev. Willis Nazrey Society meeting notice (Aaron Bell, president);
the Daughters of Cornish notice (now with a secretary); Mrs. Jane Johnson and Mrs. Ann Ware, laying out the dead
(641 Lombard); the United Beneficial Sisters of Rev. J. Woodlin Society notice. From Jan-Mar 1862: Joseph H. Cole's Continental Restaurant
(717 Lombard); Mrs. S. Shorter Hawkins (615 Lombard); Mrs. Rebecca O'Donnell, china and glass (South St.); Mrs. E. A. Palmer's
Dry Goods and Trimmings (105 N. Fifth); 'Good News' cutting system (Wm. Bradley; Mrs. Mary C. Weaver); 'Wanted, charge of a
Public School' (J. W. A., 1641 Helmuth St.); Harriet Jacobs's 'Linda' for sale at 107 N. Fifth; the Dorcas Society of Bethel
officers; the Philadelphia Grand Lodge installation roster. From Apr-Jun 1862 (Run #79): Thomas Charnock, General Furnishing Undertaker (427 S. 6th St., second door below Bethel Church), ad and editorial puff; Mrs. S. Shorter Hawkins's 'New Spring Goods' puff (615 Lombard); Miss Mary Still as the Recorder's city and county canvasser ('Our City Canvass', June 28); Rev. Henry Davis boarding notice (Wood St.) and illness notice; A. L. Stanford's twelve lectures at Wesley, Hurst St.; the SCSA Port Royal subscription and donor list; the Bucks County certificate (Emily Johnson); the Nazrey/Quinn 'Recommendation to the Districts'; the 1862 Philadelphia Conference appointments (Campbell to Bethel, Stanford to Wesley, H. Davis to Union, Roberson to Frankford); the Book Concern trustees; John S. Rock's lectures; the death of Rev. William Douglass of St. Thomas'; the J. Woodlin Society anniversary; recurring quarterly-meeting notices for the NJ and West Chester circuits. From Jul-Sep 1862 (Run #81): Miss Jane Johnson, laying out and shrouding the dead (618 South 8th St.) ad and notice; Mrs. Martha Collins's infant school (730 Russell St. above Fitzwater) ad; Banaker House (Cape May) and Union Cottage (Atlantic City) ads (out of town); Miss Mary Still named authorized agent for the city and county; Prof. P. Houston Murray's lectures; Rev. J. P. Campbell's residence notice; the Bethel male members' meeting on colored men as soldiers (Sept 6); the Bethel contraband relief meeting and committee of seven (Sept 27); the Sabbath School Convention of the Philadelphia District called by Bishop Nazrey; Wesley (Hurst St.) pastor's lecture series and appointments; Rev. W. D. W. Schureman's illness; the death of Henry Downing, Bethel Sunday School librarian. Ads that ran all quarter (Book Depository, Duterte, Allmond, Peer, Still's coal, Palmer, Charnock, Jane Johnson, Martha Collins): do NOT re-enter. From Oct-Dec 1862 (Run #82): Mrs. S. Shorter Hawkins's fall and winter goods ad (615 Lombard); Wm. H. Longfellow, surgeon dentist (1126 Rodman) ad and puff; 'Wanted' lodgers (424 South 7th) ad; the Bethel contraband committee roster; the Union A.M.E. freedmen's committee of 21; the SCSA election of Nov 3, Port Royal list, Contraband Fund and clothing lists; Father Richard Roberson's (Robinson's) injury, death and funeral; Garrison James's obituary; the Philadelphia Library Co. 29th anniversary; Rev. Wm. Alston's installation at St. Thomas'; the St. Thomas' Sinking Fund fair; the Friends' evening schools; ICY lecture course (Collins, Bassett); Book Concern executive committee and hymn-book appeal; A. Burris's concerts; Henry Christian seeking his children. From Jan-Mar 1863 (Run #83): the Church Directory of Philadelphia (First Presbyterian, J. C. Gibbs; Central Presbyterian, J. B. Reeve, 907 Lombard; Union A.M.E., Henry Davis; Jacob C. White, superintendent); Mrs. Jane Johnson and Mrs. Ann Wear/Weaver, shrouding (618 S. Eighth); Mrs. Margaret Hazzard's dressmaking 'Wanted' ad (Shippen between 8th and 9th); Edwin A. Hughes, undertaker and sexton (250 S. Tenth); Lewis Fayette, general furnishing undertaker (770 S. Second); George W. Lott, general furnishing undertaker (509 S. Thirteenth); Mrs. S. Shorter Hawkins's spring goods (815 Lombard); Julia Brown's boarders (912 Rodman); Woodlin Society officers; both Grand Lodge rosters; the Banneker Institute election; the SCSA Contraband Fund list; the Union Freedmen's Relief Association of West Philadelphia; the Hutchinson Family benefit concerts; the Annual Conference call (Bethel, May 9) and the elders' examination notice; Weaver's serial life of Richard Robinson. From Jul-Sep 1863 (Run #84): James W. Brown's steam-dyeing works (S. Sixth above Walnut; Shippen St.); Mrs. M. Bennett, herb doctress (S. Seventh below Pine); Mrs. Julia A. Brown, lodging; Mr. and Mrs. H. M. Cropper, boarding (Lombard between 4th and 5th); Dr. P. Gardiner, botanic physician (Princeton); P. Guinn & Son, grocery (South St. above Eleventh); the Soldiers' Relief Association standing notice (Jane L. Johnson, Esther Armstrong, committee of nine); the Wilberforce trustees; the Union, Friendship and Love notice; the 6th USCT flag subscribers; Campbell's hearing and resignation from Bethel (Sept); the Love and Charity expulsions (Longfellow, Eddy). From Oct-Dec 1863 (Run #85): John Oliver's employment office (Clarkson Hall, 615 Cherry); Dr. Wm. Armstrong (240 N. Ninth); Olive Branch Boarding House, Mrs. H. M. Cropper (403 Lombard); William Still's stove store; Georgiana Gleaves, oysters (633 Pine); Bethel under Stephen Smith and W. D. W. Schureman; the 6th USCT departure and the Nov 17 flag presentation; the Love and Charity schism. From Apr-Jun 1863 (Run #86): the 1863 Philadelphia Conference appointments; Wm. S. Walker, barber, 22 Main St., Frankford; the Love and Charity Grand Tabernacle roster (June 1863). Many standing ads (Duterte, Allmond, Peer, Book Depository, Hughes, Fayette, Lott, Hawkins, Jane Johnson shrouding, Hazzard, Julia Brown) will appear as repeats: note them, do not re-enter. From Jan-Jun 1864 (Runs #87-#88): Joseph Brister, dentist, 844 Lombard; John Oliver's intelligence office, 1113 Pine; Joseph C. and Sarah H. Bustill, wig makers, 403 S. Sixth; Georgiana Gleaves, oysters and notion store, 633 Pine; Mrs. S. Shorter Hawkins's 1864 dry goods; Charles W. Brister's Continental Restaurant (717 Lombard; = Winch Brister, Charles); Olive Branch boarding house (Mrs. H. M. Cropper, 403 Lombard); Mrs. M. Bennett, herb doctress; Wm. Still, coal; the 1864 Philadelphia Conference appointments; the Douglass Lyceum, Good Samaritans and Love and Charity 1864 rosters. If any ad or notice simply REPEATS, do not re-enter them (note the repeat). A changed notice (new officers, new dates) is new. Out of scope (white patrons): F. Champion (Brooklyn), Gustine, Reimer, Gregg, D. W. Clark, G. G. Evans, Leary
Getz, Dean, Metz, Elkinton, Rothermel (coal), insurance, railroads, patent medicines. NEW Black-owned ads or changed notices
SHOULD be entered. Quarterly-meeting schedules: one short article per notice, link only named preachers/officers.

## Already captured in Run #92 (April - June 1865) -- do NOT re-enter unless changed
T. J. Bowers, Coal and Kindling Wood Depot (634 Lombard); R. H. Gleaves, Private Boarding (633 Pine); Georgina Gleaves, trimmings
(633 Pine); Mrs. H. T. O'Donnell, boarding house (Lombard); Mrs. S. Shorter Hawkins, spring and summer goods (615 Lombard);
J. J. Lyons, ice cream saloon (1023 Lombard); W. R. DeCordover's Periodical Depot (419 S. Seventh); James C. Clark, M. D. (618
Pine); Mrs. Ann E. Foster, boarding (1733 Addison); James J. Spelman, military instruction (1031 South); Mrs. M. C. Gibbons's
Intelligence Office (1113 Pine); Mrs. Mary Stroder, boarding (1132 Lombard); the April 14 procession and flag presentation to
the 24th U.S.C.T.; the 1865 Philadelphia Conference appointments; the Good Samaritans District Grand Lodge roster; Unity Lodge
No. 711's anniversary. Standing ads entered in 1864-65 and still running: Hannibal Hotel (620 Pine), Olive Branch boarding house (814 Lombard), Mrs. C. E. Harding (713 Lombard), N. L. Durham, cupping and leeching (911 1/2 Christian), Charles W. Brister's Continental Restaurant (717 Lombard), Mrs. Maria Highgates, shrouding (1026 Barley), Joseph C. and Sarah H. Bustill, wig makers (403 S. Sixth), Mrs. H. S. Duterte, undertaker, Mrs. M. Bennett, herb doctress (S. Seventh below Pine), Wm. H. Longfellow, surgeon dentist (Rodman St.), the Lebanon Cemetery notice. Everything through the June 24, 1865 issue is in the database. A repeated ad is noted once; an ad whose
address, proprietor or wording has CHANGED is new.

## Already captured in Run #93 (July - September 1865) -- do NOT re-enter unless changed
Thos. J. Bowers, Coal Yard (634 Lombard, the larger ad); William Still, Stove Store (107 North Fifth); Mrs. Amelia W. Adams,
Select School (Juniper St.); Abraham Fields, grocery (South Seventh above Lombard); the Banneker House, Cape Island (Mrs.
Teagle); the Colored People's National Lincoln Monument ad; C. C. Blue's saloon (610 Pine, editorial notice); the Harrisburg
annual meeting of the Pennsylvania State Equal Rights League (Aug 9); the call of the National Equal Rights League for
Cleveland; the Odd Fellows' excursion to the Baltimore celebration of Oct 6 (announcement only: a REPORT of it is new); the
Masonic Grand Lodges' call for Oct 10 (announcement only); the death and funeral of Rev. Jeremiah Asher; the death of Dr.
James H. Wilson; 'Shameful' (Spruce and Pine Street car, Sept 23); the Institute for Colored Youth appointments of Fanny
Jackson and Mary Patterson. Everything through the September 30, 1865 issue is in the database.

## Watch for in this quarter (October - December 1865)
- PARADES AND PROCESSIONS (owner tracks this as a topic): the Odd Fellows at Baltimore (Oct 6), the Masonic assembly (Oct 10),
  receptions of returning regiments, Thanksgiving (Dec 7, 1865), the Thirteenth Amendment rejoicings (December), Sabbath-school and society processions, excursions and picnics, receptions of returning
  regiments, lodge turnouts. For each: date, route or place, the marshals, the societies, lodges, schools and bands that
  marched, speakers, and any interference by police or mobs.
- STREETCAR exclusion (topic): every ejection, petition, meeting, letter, editorial, court case, car company vote.
- SOCIETY MEETINGS (owner's instruction): every meeting, anniversary, election, installation or notice of a beneficial,
  literary, temperance, relief or burial society, lodge, association or church society, each as its own EVENT with the full
  name as printed, date, place with address, and every officer, committee member and speaker.
- The Pennsylvania State EQUAL RIGHTS LEAGUE (after its Harrisburg meeting of August 1865), the National League at Cleveland (October 1865) and the Philadelphia
  auxiliaries; the National Equal Rights League; the suffrage question; delegates elected, with names.
- RETURNING colored regiments and their receptions; Camp William Penn; deaths of soldiers and chaplains; bounty and pension
  notices naming Philadelphians.
- Camp meetings, quarterly meetings, church dedications and corner stones in and near Philadelphia; the A.M.E. mission to the
  South and missionaries leaving Philadelphia; the Book Concern.
- Institute for Colored Youth, the public colored schools (teachers named), Banneker Institute, the Lincoln monument funds,
  freedpeople relief, fairs and festivals.
- NEW or changed Black-owned ads; marriages and deaths of Philadelphians, with officiating ministers.

## Known identities (record names as printed; mention the identification in `notes`)
- "Robertson" / "Father Robertson" (Bristol, Frankford circuits): the owner has ruled that the
  CR's "Rev. Richard Robertson" IS Rev. Richard Robinson of Frankford. Record a full printed name as printed;
  a bare surname ("Father Robertson") goes in the text only.
- J. C. White in Banneker/ICY contexts of the 1860s is Jacob C. White Jr.: record as "Jacob C. White Jr." with role
  noting the printed form. J. P. Campbell = Bishop Jabez Pitt Campbell (record "J. P. Campbell").
- Do NOT link bare surnames ("Nazrey", "Brother Gaines"): use the full name only when printed or certain from the
  same item (bishops: Willis Nazrey, Daniel A. Payne, William Paul Quinn).
- Subscriber lists from New Jersey / Bucks / Chester County circuits: list them in the event description; link only
  names that are clearly read AND not extremely common (skip linking e.g. "Mary Jones", "John Smith").
- S. Morgan Smith is NOT Rev. Stephen Smith (owner 2026-11-11; record as printed, separately). "Mrs. Laws" / "Ann Lawe" = the Publication Society president.
- LAWS FAMILY (owner's rulings, Nov 2026): Mrs. Anna Laws (wife of John Laws; mother of Rev. William J. Laws) is NOT
  Stephen Laws's daughter Anna. The early Stephen Laws (1820 city directory) is a separate man from the later Stephen Laws.
  Record every Laws exactly as printed and put any identification in `notes` only.
  "Mrs. Bunday"/"Mrs. Bundy" = Hope Grand Union. "James F. Needham" is the SON (James Fields Needham); plain "James
  Needham" of the 1830s-40s is the father. O. V. Catto, S. M. Douglass, A. C. Crippen, Prof. Bassett: record as printed.
- Miss Mary Still (Allentown / Clarksborough near Mount Holly N.J.; the Recorder's Philadelphia canvasser from June 1862) is William Still's sister (owner's ruling, Nov 2026); record her as printed.
- Rev. Jonathan C. Gibbs (born 1821; Presbyterian, First African Presbyterian) is the SON. His father, Jonathan C. Gibbs Sr.,
  died in 1831: any 1860s Gibbs is the son.
- 1863 Q3 rulings (owner): the 'Jacob C. White' of the 6th USCT flag list is the elder; 'J. C. White, Jr.' is the son. A. L. Stanford =
  Anthony L. Stanford; U. B. Vidal = Ulysses B. Vidal; T./Theo. Gould = Theodore Gould (record as printed). Rev. Peter Gardiner /
  Gardener and Dr. P. Gardiner are under review: record exactly as printed, no identification.
- Rulings of 2026-11-13 (owner): 'J. P. Campbell' and 'Jabez P. Campbell' are one record (Bishop Campbell); 'J. Asher' and 'Rev. Mr. Asher' = Rev. Jeremiah Asher; 'F. E. W. Harper' = Frances Ellen Watkins Harper; 'J. C. White, Sr.' = Jacob C. White Sr. and 'J. C. White, Jr.' = Jacob C. White Jr. Record all of them as printed. The Continental Restaurant proprietor is Charles W. Brister.
- 1864-65 rulings (owner, 2026-11-11): 'William Sill', post sutler = William Still. 'Jacob C. White' / 'J. C. White' printed without Jr. on
  the SCSA committee and as Lebanon Cemetery secretary = the father (Jacob C. White Sr.).
- 1864 rulings (owner): mob or police violence against Black passengers on or around the street cars belongs in the streetcar topic
  (the James W. Brown assault, Mar 1864). Surname-only women ('Mrs. Jones', 'Mrs. Mills') are NOT linked. 'Joseph C. Bustill' = Joseph
  Cassey Bustill (owner's 2026-07 merge). 'Miss Greenfield, the Black Swan' stays text only.
- 1863 Q2 rulings (owner): 'Libyan Cemetery' (Logan funeral) is Lebanon Cemetery: give 'Lebanon Cemetery (printed ...)' when misprinted.
  Lieutenant Daniel Colley (1863) is NOT Winch's Daniel Colley (b. 1794); record as printed.
- 1863 Q4 rulings (owner): ALL Joshua / Josiah / Joseph / J. P. B. Eddy variations are ONE person (Rev. Joshua P. B. Eddy): record as
  printed, identification in notes. Do NOT merge Wm. / William Cooper, Wm. H. / William H. Longfellow, T. H. / Thomas H. Cooper, or A. M. Green
  with anyone: record as printed. 'Rev. Mr. Shreeves' Lombard St. Church' = J. B. Reeve's Central Presbyterian. William A. Potter and
  Theodore Smith (advertisers) are not known to be Black: enter such ads as notices. 1863 William Still = the William Still (Underground Railroad).
- 1863 Q1 rulings (owner): the Church Directory superintendent 'Jacob C. White' (no Jr./Sr.) is the elder Jacob C. White; the
  undertaker at 509 S. Thirteenth is George W. Lott; Margaret Hassard / Hazzard is one dressmaker, spelled Hazzard. Hawkins's
  Lombard St. number (615 or 815) is not certain: record as printed.
- 1862 rulings (owner): Rev. Richard Roberson / Robertson = Rev. Richard Robinson of Frankford (died Nov. 18, 1862); Mrs. S. Shorter
  Hawkins = Sarah S. Hawkins = Sarah S. Shorter; Wm. Alston / W. A. Alston = Rev. William J. Alston of St. Thomas'; 'E. H. Bassett' =
  E. D. Bassett; Garrison James served both Bethel (chorister) and Union (trustee). Record as printed; identifications in notes.
- Lambsong the confectioner (Culvert above Apple) is Rebecca Lambsong's husband; Robert J. Douglass / Robert Douglass Jr. is the
  painter (owner's rulings, Nov 2026). The 1838 Register of Trades is now in the database: a tradesperson with an address may already
  have a record; record as printed.
- Rev. Walter Proctor died Dec. 10, 1861; Elisha Weaver resumed as editor in Dec. 1861 after A. L. Stanford resigned.
- Isaiah C. Were = Isaiah C. Wears. W. D. W. Schureman (also printed Wm. D. W., Scheroman). Joshua Pernal (also printed
  Purnell). A. L. Stanford (Anthony L. Stanford) was acting editor in the autumn of 1861 while Weaver travelled.
- Bishops of this period: Willis Nazrey ("W. Nazrey", often OCR'd Nazary/Nasrey), Daniel A. Payne,
  William Paul Quinn, Jabez P. Campbell. Elisha Weaver is the General Book Steward/editor.
  John M. Brown (J. M. Brown) edits the Repository of Religion and Literature.

- Henrietta Duterte (undertaker, 634 Lombard; printed 'Mrs. H. S. Duterte') and Francis A. Duterte (her husband, a carpenter
  and builder) are already single merged records: record as printed; do not treat a new printing as a new person. Her husband
  is reported dead before 1862, so a living 1862 'Francis Duterte' needs a flag in `notes`.
- Thomas Butler (the 1838 Butler) is record 'Butler, Thomas'; record any Butler exactly as printed, identification in `notes` only.
- The minister is Woodson (Lewis/Louis Woodson), NOT Woodward. Record as printed and flag if the paper itself prints Woodward.

## Verification (non-negotiable)
- EVERY name, address and number you record must be read on the image crop, not taken from OCR.
- If you cannot read it confidently, either leave it out or record your best reading followed by
  " [VERIFY]" in the name/role/description and add a `flags` entry saying what is uncertain.
- The public site shows no VERIFY flags, so before you finish, RE-READ every [VERIFY] name at DPI=1600 (env DPI=1600 for
  crop.py) and on every other printing of the same item. If it is now certain, remove the flag. If not, keep the flag:
  those names will be kept out of the linked people (the text keeps your best reading). Fewer, certain links beat more.
- Never invent a given name or fill a gap from outside knowledge. You may note a likely
  identification in `notes` (e.g. "probably the Rev. J. P. Campbell of Union Church").

## What to return (your final message)
A short report: issues covered, counts of articles/events/linked names, the 5-10 most notable
finds, and every flag. Keep it under 400 words; the JSON file is the deliverable.
