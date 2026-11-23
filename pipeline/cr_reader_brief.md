# Extraction brief: Christian Recorder, January - March 1867

You are extracting names, articles and events from issues of *The Christian Recorder*
(Philadelphia, organ of the A.M.E. Church; Rev. Elisha Weaver, General Book Steward/Publisher;
office at No. 631 Pine Street from Nov 10, 1866; the Book Depository ad still prints 619 Pine) for the **1838 Black Metropolis names
database**, a public-history project recovering the free Black community of antebellum
Philadelphia (c. 1780-1865). The owner is a historian who values source-critical rigor: a wrong
name is worse than a missing one, and every uncertainty must be flagged, not smoothed over.

NOTE for this quarter: in Oct-Dec 1866 every page-1 masthead printed "Rev. Elisha Weaver, Publisher," and every page-2
editorial box "Rev. James Lynch, Editor," but Lynch went South on Oct 23, 1866 and Weaver edited in his absence. Check each
issue: if the editor or publisher line CHANGES this quarter, or Lynch's return or departure is reported, say so in your notes.
Record editors/publishers exactly as printed. Vol. VII begins with Jan 5, 1867 (No. 1, Whole No. 313); pagination restarts at 1.

## Inputs (scratch dir S = /home/claude/run99_scratch)
- OCR text: `S/txt/CR_<date>_p<N>.txt` -- one file per page, 7 columns per page separated by
  `[column N]` markers, top to bottom within each column. Microfilm OCR: names are often garbled.
- Page images: `S/jpg/CR_<date>_p<N>.jpg` (2000px wide, whole page). For READING names you need
  higher resolution: render a crop from the source PDF instead. Frame numbers: ALWAYS look the frame up in S/jobs.txt
  ('frame:slug:page'). Pages not in jobs.txt DO NOT EXIST in our copy. Cite by DATE and the issue page (1-4).
  January-March 1867 (Vol. VII, Nos. 1-13): 13 issues, pagination 1-52. In our copy:
  **March 2 (No. 9) and March 30 (No. 13) are pages 3-4 only** (the film carries a card "first sheet missing" for each,
  frames 34 and 49). **January 5 (No. 1) pages 1 and 2 are badly torn**: about half of each page is lost (page 1's left
  half, page 2's right half); read what survives and say which columns are gone. All other issues are complete.
  **Frame 1 is a target card, not a page; frames 34 and 49 are "first sheet missing" cards.** January 5 was filmed out of
  order: frame 4 is page 4 and frame 5 is page 3. Frame map (frame:date:page), confirmed from mastheads and page numbers:
  - Jan 5 (No.1): f2=p1 (torn), f3=p2 (torn), f5=p3, f4=p4
  - Jan 12 (No.2): f6=p1, f7=p2, f8=p3, f9=p4
  - Jan 19 (No.3): f10=p1, f11=p2, f12=p3, f13=p4
  - Jan 26 (No.4): f14=p1, f15=p2, f16=p3, f17=p4
  - Feb 2 (No.5): f18=p1, f19=p2, f20=p3, f21=p4
  - Feb 9 (No.6): f22=p1, f23=p2, f24=p3, f25=p4
  - Feb 16 (No.7): f26=p1, f27=p2, f28=p3, f29=p4
  - Feb 23 (No.8): f30=p1, f31=p2, f32=p3, f33=p4
  - Mar 2 (No.9): f35=p3, f36=p4  (p1 and p2 MISSING)
  - Mar 9 (No.10): f37=p1, f38=p2, f39=p3, f40=p4
  - Mar 16 (No.11): f41=p1, f42=p2, f43=p3, f44=p4
  - Mar 23 (No.12): f45=p1, f46=p2, f47=p3, f48=p4
  - Mar 30 (No.13): f50=p3, f51=p4  (p1 and p2 MISSING)
  Crops: render from the PDF with
  ```
  python3 S/crop.py <frame> <x0frac> <y0frac> <x1frac> <y1frac> <out.png>
  ```
  then Read the png. Fractions are of the paper area (film border trimmed). Write your crops into a folder of your own,
  `S/crops_<your-label>/`. A single column is ~1/7 of the width; crops of ~1/7 width x ~1/5 height read comfortably.
  This file is a small (~470x620 pt) page with a 600 ppi high-resolution layer: crop.py renders at DPI=1000 by default
  (one column ~885px wide). For a VERIFY recheck use `DPI=1600 python3 S/crop.py ...`; going higher than ~1600 does NOT
  help, because the scan itself is 600 ppi (there is no more detail to recover). crop.py caches each page's render, so the
  FIRST crop of a page takes a few seconds to ~30s and later crops of the same page are instant. Run ONE crop at a time:
  two other readers share this small (2-core) machine. Use the 2000px JPEG (also cropped, e.g. with PIL) to locate
  things first.
- OCR and image of a page should be used together: OCR to find what is there, the image to read
  names, addresses and numbers exactly.
- READ PAGES 1 AND 4 OF EVERY ISSUE IN FULL FROM IMAGE CROPS, column by column (7 columns, about five slices each, ONE
  column per crop, not two-column or wider strips; about FIVE vertical slices per column, never fewer: tall
  crops are downscaled and small type is lost), on your FIRST pass. Do NOT triage these pages from the OCR text or from
  headings. In past runs readers triaged them and had to be sent back; a report that says pages 1 and 4 were not read in
  full will be sent back again. Page 1 carries letters and church news, page 4 the ads and notices. Read the local, notice,
  marriage, death and advertisement columns of pages 2 and 3 from crops as well, INCLUDING EVERY AD COLUMN OF PAGE 3 (one
  column per crop, five slices; do not check them on the overview image), and the foot of page 3. (For the short issues, read
  in full whatever pages are present: March 2 and March 30 are pages 3-4 only, so read BOTH of their pages in full.)
  This is slow work: expect well over an hour, and take the time.
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
Format example (taken from an earlier quarter; the structure is what matters):
```json
{
  "articles": [
    {"issue": "CR_1866-04-07", "page": 2, "headline": "Our City Carriers (notice)",
     "author": "", "type": "notice",
     "summary": "Opening sentences only, lightly cleaned transcription, enough to identify the piece.",
     "people": [["James Wiggins", "city carrier"], ["W. T. Jones", "city carrier"]]}
  ],
  "events": [
    {"issue": "CR_1866-04-07", "page": 2, "name": "Publication Society of Philadelphia -- meeting called",
     "date": "1866-04-21", "location": "No. 619 Pine street, Philadelphia",
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

## Topics to WATCH FOR this quarter (January - March 1867)
Tag these in your notes and make sure each is captured as an article/event with full rosters:
- STREETCAR exclusion (topic, the big one this quarter): the Pennsylvania legislature took up the bill again in the 1867
  session. Capture every ejection, petition, meeting, letter, editorial, court case, legislative vote and its aftermath (the
  Equal Rights League's Railroads committee: D. B. Bowser, W. D. Forten, O. V. Catto; William Still's earlier campaign).
- PARADES AND PROCESSIONS (owner tracks this as a topic): New Year's and Emancipation Day (January 1) observances,
  Washington's birthday, Sabbath-school and society processions, lodge turnouts, funeral processions. For each: date, route
  or place, marshals, societies, lodges, schools, military companies and bands, speakers, any interference by police or mobs.
- MIGRATIONS (owner tracks this as a topic): people and missionaries leaving or arriving: A.M.E. missions to the South
  (South Carolina, Georgia, Florida; T. G. Steward, Henry M. Turner, R. H. Cain, J. M. Brown, James Lynch), teachers going South,
  emigration to Liberia or Haiti, Major Martin R. Delany. Capture date, origin, destination, names and the organizing committee.
- INFORMATION WANTED notices: capture those with a Philadelphia or nearby link as notices with the named people; others in
  the issue notes only.
- CONVENTIONS AND SUFFRAGE: the National Convention of Colored Soldiers and Sailors and the National Equal Rights League
  meeting in Washington (January 1867); the Pennsylvania State Equal Rights League; Philadelphia delegates and officers (linked);
  suffrage petitions and meetings.
- LIBERTY HALL (the former ICY building on Lombard St., dedicated Nov 1866): every meeting, concert, lecture or fair held
  there, and stockholder business.
- THE BOOK CONCERN (Great Union) FAIR aftermath: reports of proceeds, thanks to committees, prizes awarded.
- THE PHILADELPHIA ANNUAL CONFERENCE: notices of the spring 1867 session, its place and date, committees; and any South
  Carolina, Baltimore or New York conference reports naming Philadelphia clergy.
- SOCIETY MEETINGS (owner's instruction): every meeting, anniversary, election, installation or notice of a beneficial,
  literary, temperance, relief or burial society, lodge (Masons, Odd Fellows, Good Samaritans), association, school or church
  society, each as its own EVENT with the full name as printed, date, place with address, and every officer and speaker.
  January is election and installation season: capture officer lists.
- RETURNING soldiers and sailors, bounty and pension claim notices naming Philadelphians; soldiers' reunions.
- BASE BALL AND CRICKET CLUBS: Pythian and Excelsior and any other club; record members as printed.
- THE WESLEY CHURCHES BY NAME: owner's rulings: Hurst Street Wesley is LITTLE WESLEY (A.M.E.); Lombard Street Wesley is BIG
  WESLEY (A.M.E. Zion), also printed "First Colored Wesley Church"; plain "Wesley Church" notices default to the Little Wesley
  lane but FLAG them. Record each exactly as printed.
- Bethel affairs (pastor James Hollen), quarterly meetings, church dedications, fairs and festivals, watch-night services,
  the Home for Aged and Infirm Colored Persons, the Institute for Colored Youth, the public colored schools (teachers named),
  the Banneker Institute, the Library Company, the Social, Civil and Statistical Association, the Pennsylvania Freedmen's Relief,
  the Zion Mission (Seventh below Dickerson).
- NEW or changed Black-owned ads; marriages and deaths of Philadelphians, with officiating ministers.

## Already captured (through December 29, 1866) -- do NOT re-enter unless the ad/notice has CHANGED
Everything in the Christian Recorder THROUGH THE DECEMBER 29, 1866 ISSUE is already in the database (Runs #74-#98). A repeated
ad or standing notice is entered once; an ad whose address, proprietor or wording has CHANGED is new. Many of the ads below
will still be running in Jan-Mar 1867: note the repeat, do not re-enter.

### Run #98 (October - December 1866) -- note repeats, do NOT re-enter
Ads: Mrs. Sarah Irons, shrouding and laying out the dead, moved to Union Street (number 320 or 820 not settled: if a Jan-Mar
printing shows the number clearly, report it in notes and flags); A. Upham's confectionery (white-owned; skip); J. H. Moore's
china (printed 716 Lombard Oct-Dec; 706 in Sep: report which number Jan-Mar printings show); Lodgings (Gaskill St., 410/416:
report the number shown). Captured: Liberty Hall dedication (Nov 12); the Book Concern (Great Union) Fair (calls, opening
Nov 15, officers, Mrs. Maria Hallowell president, closing Nov 29, prizes); the Philadelphia soldiers' and sailors' permanent
organization (Sgt. J. R. V. Morgan president); the Soldiers' and Sailors' National Convention call (Nov 3, Dec 22); the NERL
Washington call (Nov 24, Dec 15); the Dec 19 Liberty Hall mass meeting electing delegates to Washington (I. C. Wears
president); the Odd Fellows' gold medal to D. B. Bowser; St. Thomas' fair committee; Bishop Campbell Bible Class officers;
the ICY examination and 1866 graduates; the Zion Mission; Union A.M.E. quarterly meeting; Elisha Weaver's marriage (Nov 14).

### Run #97 (July - September 1866) -- note repeats, do NOT re-enter
Standing ads entered once in Jul-Sep 1866: Mrs. J. Culquhoon's ice cream saloon (No. 913 Lombard; owner's reading of the
surname); William Still's coal yard (Nos. 1216-1220 Washington Ave.); Georgina Gleaves (removed to 1028 Lombard); A. T. Jones's
auction dry goods and trimmings (No. 718 Lombard; also printed A. P., A. I., A. J. Jones: owner rules it is ONE man, A. T. Jones);
James W. Brown's new store (No. 14 South Sixth); M. A. Williams's employment office (1019 Rodman); J. H. Moore's china, glass
and queensware (No. 706 Lombard, under Liberty Hall); Houston & Boling, flour/starch/soaps (South St., 625 or 825); Organs for
Sale, Joseph H. Carter (South St.); Lodgings (410 Gaskill); Macamoose Tonic (Rev. I. R. Gates; 1230 Wood St. and 1618 N. 11th);
lessons in French, English and Spanish (804 Lombard); Wanted apprentices (401 S. Seventh); Miss E. E. Hunter at Mrs. S. S.
Hawkins's Cape May store; Banneker House (Cape Island); Mrs. Emeline Williams (Cape May). Also captured: the Pa. State Equal
Rights League at Pittsburgh (Aug) and the National League's Nashville call, protest and revocation; the new Hall on Lombard St.
(former ICY building) and its stockholders; the Home for Aged and Infirm Colored Persons officers; the Book Concern Fair committees
(announced Sep 29); the Centenary of Methodism committee (Sep 15 and Sep 29 rosters); the Olive Cemetery election; the suffrage
meeting at Wesley Church, Lombard St. (Sep 10).

### Run #96 (April - June 1866) -- note repeats, do NOT re-enter
Standing ads entered once in Apr-Jun 1866: the Great Union Intelligence Office (proprietor also printed "E. Demund & Co.");
Mrs. Sarah Irons, 619 Pine, shrouding and laying out the dead; Robert Jones, room to rent for societies, No. 6 North 8th
St.; the Security Life Insurance Co. (Jos. C. Bustill, solicitor; N. L. Durham also solicitor, 911 1/2 Christian St.); the
African Civilization Society ad (with its branch office).
Articles and events captured Apr-Jun 1866: the A.M.E. Semi-Centenary printings (Bethel and others, left separate for the
owner); the SCSA universal-suffrage fund donor roster; the Philadelphia Annual Conference spring session at Princeton
(printed Apr 21, May 5 and Jun 2, with the appointment roster); the Excelsior Base Ball Club; the Freedmen's Fair opening the
new Lombard Street hall; Rev. William Moore's Bethel service; new Bethel pastor James Hollen; F. E. W. Harper's "What
High-Toned Men Think" (streetcars); the June 2 meeting for teachers and preachers for the Freedmen; the South Carolina
Conference southern-mission reports; Major Martin R. Delany at Hilton Head.

### Run #95 (January - March 1866) standing ads/notices -- note repeats, do NOT re-enter
Standing ads entered once in Jan-Mar 1866: Mayhew (257 Raspberry St.); G. A. Brown (Newtown); Dr. Jonathan Davis; Maria Butler;
Capt. George Brook; Leizeare Brown; J. B. Rodgers; the Freedmen's Employment Office. The Equal Rights League special meeting of
Feb. 20 1866 is captured. (Run #95 left the Semi-Centenary spread, the SCSA meetings and the two Old Folks' concerts as separate
entries for owner review -- do not assume those are closed.)

### Runs #74-#94 (1861 - Dec 1865) recurring ads/standing notices -- note repeats, do NOT re-enter
Book Depository of the AME Church (619 Pine; E. Weaver); city carriers James Wiggins & W. T. Jones; Ellis J. Peer's Fine Cake
Bakery; Mrs. H. S. Duterte, undertaker (634 Lombard); Thomas W. Allmond, furnishing undertaker (1027 Rodman); Thomas Charnock,
furnishing undertaker (427 S. 6th); Edwin A. Hughes, undertaker (250 S. Tenth); Lewis Fayette, undertaker (770 S. Second);
George W. Lott, undertaker (509 S. Thirteenth); Maria Highgates, shrouding (1026 Barley); Jane Johnson & Ann Wear, shrouding
(618 S. Eighth); Mrs. S. Shorter Hawkins, dry goods (615 Lombard St.); William Still, coal/stoves (107 N. Fifth); T. J. Bowers,
Coal and Kindling Depot (634 Lombard); R. H. Gleaves, boarding and Georgiana/Georgina Gleaves, trimmings/oysters (633 Pine);
Joseph C. & Sarah H. Bustill, wig makers (403 S. Sixth); Charles W. Brister's Continental Restaurant (717 Lombard); Olive
Branch Boarding House (Mrs. H. M. Cropper); Mrs. M. Bennett, herb doctress (S. Seventh below Pine); Wm. H. Longfellow, surgeon
dentist (Rodman St.); Joseph Brister, dentist (844 Lombard); John Oliver's intelligence/employment office (1113 Pine); the
Hannibal Hotel (620 Pine); Mrs. C. E. Harding (713 Lombard); N. L. Durham, cupping and leeching; W. R. DeCordover's Periodical
Depot (419 S. Seventh); James C. Clark/Clarke, M.D. (618 Pine); Mrs. Ann E. Foster, boarding (1733 Addison); Mrs. M. C.
Gibbons's Intelligence Office (1113 Pine); Mrs. Mary Stroder, boarding (1132 Lombard); Amelia W. Adams, Select School (Juniper
St.); Abraham Fields, grocery; the Lebanon Cemetery notice; New Fall/Winter Dry Goods (S. Shorter Hawkins, 615 Lombard); Joseph
H. Cole's Continental Restaurant; James W. Brown, Steam-Dyeing; the Colored Soldiers' and Seamen's U.S. Government Claim Office
(John J. Keefe, Jr.); the U.S. Agency for Colored Soldiers and Seamen (Thomas S. Malcom); Dr. David Rosell (907 Lombard); Wm.
H. Davis's "Amateur's Companion"; the Ladies' Union Sewing Circle appeal; "Information Wanted (Richard Parker)". Church/
conference items captured through 1865-66: the Philadelphia Conference appointments 1861-65; the Book Concern trustees/exec
committee; the Church Directory of Philadelphia; the ICY appointments (Fanny Jackson, Mary Patterson, Bassett); the Pa. State
Equal Rights League Harrisburg meetings; the Odd Fellows' Baltimore excursion; the deaths of Rev. Jeremiah Asher and Dr. James
H. Wilson; "Shameful" (Spruce and Pine St. car, Sept 23 1865).
White-run standing ads that the SKIP rule already covers (note once, do not enter): Ayer's Sarsaparilla and Cathartic Pills;
the Pennsylvania Central Railroad; the "Vermifuge" ad; McLane's pills.

## Known identities (record names as printed; mention the identification in `notes`)
- Editors this period: Rev. Elisha Weaver (General Book Steward/Publisher) and Rev. James Lynch, Editor (from May 5, 1866).
  Record each as printed on each issue.
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
- Rulings of 2026-11-13 (owner): 'J. P. Campbell' and 'Jabez P. Campbell' are one record (Bishop Campbell); 'J. Asher' and 'Rev. Mr. Asher' = Rev. Jeremiah Asher; 'F. E. W. Harper' = Frances Ellen Watkins Harper; 'J. C. White, Sr.' = Jacob C. White Sr. and 'J. C. White, Jr.' = Jacob C. White Jr. Record all of them as printed. The Continental Restaurant proprietor is Charles W. Brister.
- 1864-65 rulings (owner, 2026-11-11): 'William Sill', post sutler = William Still. 'Jacob C. White' / 'J. C. White' printed without Jr. on
  the SCSA committee and as Lebanon Cemetery secretary = the father (Jacob C. White Sr.).
- Run #94 rulings (owner, 2026-11-14): 'Jacob O. White' (Oct 21 Lincoln-monument call) = Jacob C. White, Jr.; 'John C. Bonors'
  (Dec 30) = John C. Bowers; Union Bethel's 'J. P. Gibbs' is NOT R. P. Gibbs; Mrs. Hawkins's address stays 615 Lombard (a '515'
  printing is a misprint). H. G. Rhodes (Book Concern trustee) and H. J. Rhodes (a Zion pastor) are NOT known to be one man:
  record each exactly as printed, no merge, identification question noted only.
- 1864 rulings (owner): mob or police violence against Black passengers on or around the street cars belongs in the streetcar topic.
  Surname-only women ('Mrs. Jones', 'Mrs. Mills') are NOT linked. 'Joseph C. Bustill' = Joseph Cassey Bustill. 'Miss Greenfield,
  the Black Swan' stays text only.
- ALL Joshua / Josiah / Joseph / J. P. B. Eddy variations are ONE person (Rev. Joshua P. B. Eddy): record as printed, identification
  in notes. Do NOT merge Wm. / William Cooper, Wm. H. / William H. Longfellow, T. H. / Thomas H. Cooper, or A. M. Green with anyone.
  'Libyan Cemetery' is Lebanon Cemetery. 1863-66 'William Still' = the William Still (Underground Railroad).
- 1862 rulings (owner): Rev. Richard Roberson / Robertson = Rev. Richard Robinson of Frankford; Mrs. S. Shorter Hawkins = Sarah S.
  Hawkins = Sarah S. Shorter; Wm. Alston / W. A. Alston = Rev. William J. Alston of St. Thomas'; 'E. H. Bassett' = E. D. Bassett;
  Garrison James served both Bethel (chorister) and Union (trustee). Record as printed; identifications in notes.
- Lambsong the confectioner is Rebecca Lambsong's husband; Robert J. Douglass / Robert Douglass Jr. is the painter. The 1838
  Register of Trades is in the database: a tradesperson with an address may already have a record; record as printed.
- Isaiah C. Were = Isaiah C. Wears. W. D. W. Schureman (also printed Wm. D. W., Scheroman). Joshua Pernal (also printed Purnell).
  A. L. Stanford (Anthony L. Stanford). The minister is Woodson (Lewis/Louis Woodson), NOT Woodward: record as printed and flag
  if the paper itself prints Woodward.
- Bishops of this period: Willis Nazrey ("W. Nazrey", often OCR'd Nazary/Nasrey), Daniel A. Payne, William Paul Quinn, Jabez P.
  Campbell. Elisha Weaver is the General Book Steward/Publisher. John M. Brown (J. M. Brown) edits the Repository of Religion and Literature.
- Henrietta Duterte (undertaker, 634 Lombard; printed 'Mrs. H. S. Duterte') and Francis A. Duterte (her late husband) are a single
  merged record: record as printed. Thomas Butler (the 1838 Butler) is record 'Butler, Thomas'; record any Butler as printed,
  identification in `notes` only.
- Run #97 rulings (owner, 2026-11-20): Joseph Carter, organ builder on South Street, is a Black organ builder (CR Jan 6, 1866;
  Bolivar) and "Joseph H. Carter" of the 1866 organ ad is the same man: record as printed. A. T. Jones of 718 Lombard (printed
  A. P./A. I./A. J.) is one man. Rev. William Moore of Trenton (1866) is recorded as printed and is NOT linked to Bethel's earlier
  William Moore. Common names on out-of-town committees (N.J., Chester Co., Md.) stay in the text only.
- Run #98 and Liberty Hall rulings (owner, 2026-11-21): Robert Adger of Liberty Hall IS Robert M. Adger (only one). Robert
  Allen and Henry Jones, Liberty Hall stockholders, are kept on their own records (not linked to older same-named men). "J. W.
  Parnell" of the Liberty Hall dedication = James W. Purnell. William Warrick and William Warrick, Jr. of Liberty Hall are one
  man (Jr.). The ice cream saloon at 913 Lombard is Mrs. J. Culquhoon's (owner's reading). Record all as printed.
- OPEN identity questions (record as printed, flag, do NOT link across): Rev. William Moore of Bethel (1864-66) vs
  the earlier A.M.E. cleric William Moore of 1835 -- kept apart. H. G. Rhodes vs H. J. Rhodes -- kept as printed. R. P. Gibbs vs
  J. P. Gibbs -- kept as printed. "Malcolm's" branch address read as 609 Walnut is uncertain [VERIFY]. Octavius V. Catto appears on
  both the Excelsior and Pythian club lanes (Bolivar does not name him an Excelsior) -- record the club as printed on the item.
  Robert Jones of the Run #96 room-to-rent ad (No. 6 North 8th St.) is NOT established as Bolivar's Robert Jones: record any
  Robert Jones as printed, identification question in notes only.

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
