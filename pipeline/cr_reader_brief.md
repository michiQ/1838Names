# Extraction brief: Christian Recorder, July - September 1866

You are extracting names, articles and events from issues of *The Christian Recorder*
(Philadelphia, organ of the A.M.E. Church; Rev. Elisha Weaver, General Book Steward/Publisher;
office and AME Book Depository at No. 619 Pine Street) for the **1838 Black Metropolis names
database**, a public-history project recovering the free Black community of antebellum
Philadelphia (c. 1780-1865). The owner is a historian who values source-critical rigor: a wrong
name is worse than a missing one, and every uncertainty must be flagged, not smoothed over.

NOTE for this quarter: the editorship change of spring 1866 is now settled. Every page-1 masthead
this quarter prints "Rev. Elisha Weaver, Publisher," and every page-2 editorial box prints
"The Christian Recorder. Rev. James Lynch, Editor." Record editors/publishers exactly as printed on
the issue you are reading.

## Inputs (scratch dir S = /home/claude/run97_scratch)
- OCR text: `S/txt/CR_<date>_p<N>.txt` -- one file per page, 7 columns per page separated by
  `[column N]` markers, top to bottom within each column. Microfilm OCR: names are often garbled.
- Page images: `S/jpg/CR_<date>_p<N>.jpg` (2000px wide, whole page). For READING names you need
  higher resolution: render a crop from the source PDF instead. Frame numbers: ALWAYS look the frame up in S/jobs.txt
  ('frame:slug:page'). Pages not in jobs.txt DO NOT EXIST in our copy. Cite by DATE and the issue page (1-4).
  July-September 1866 (Vol. VI, Nos. 27-39): 13 issues, continuous pagination 105-156. ONE issue is missing a leaf
  in our copy: **August 11 (No. 32)** is present as pages 3-4 only (pages 1 and 2 missing): frame 22 is page 3
  (numbered 127) and frame 23 is page 4 (numbered 128). **Frame 21 is a dark target card, not a page: ignore it.** All other issues are complete (four pages). Frame map (frame:date:page):
  - Jul 7 (No.27): f1=p1, f2=p2, f3=p3, f4=p4
  - Jul 14 (No.28): f5=p1, f6=p2, f7=p3, f8=p4
  - Jul 21 (No.29): f9=p1, f10=p2, f11=p3, f12=p4
  - Jul 28 (No.30): f13=p1, f14=p2, f15=p3, f16=p4
  - Aug 4 (No.31): f17=p1, f18=p2, f19=p3, f20=p4
  - Aug 11 (No.32): f22=p3, f23=p4  (p1 and p2 MISSING; f21 is a target card)
  - Aug 18 (No.33): f24=p1, f25=p2, f26=p3, f27=p4
  - Aug 25 (No.34): f28=p1, f29=p2, f30=p3, f31=p4
  - Sep 1 (No.35): f32=p1, f33=p2, f34=p3, f35=p4
  - Sep 8 (No.36): f36=p1, f37=p2, f38=p3, f39=p4
  - Sep 15 (No.37): f40=p1, f41=p2, f42=p3, f43=p4
  - Sep 22 (No.38): f44=p1, f45=p2, f46=p3, f47=p4
  - Sep 29 (No.39): f48=p1, f49=p2, f50=p3, f51=p4
  Crops: render from the PDF with
  ```
  python3 S/crop.py <frame> <x0frac> <y0frac> <x1frac> <y1frac> <out.png>
  ```
  then Read the png. Fractions are of the paper area (film border trimmed). Write your crops into a folder of your own,
  `S/crops_<your-label>/`. A single column is ~1/7 of the width; crops of ~1/7 width x ~1/5 height read comfortably.
  This file is a small (~471x620 pt) page with a 600 ppi high-resolution layer: crop.py renders at DPI=1000 by default
  (one column ~885px wide). For a VERIFY recheck use `DPI=1600 python3 S/crop.py ...`; going higher than ~1600 does NOT
  help, because the scan itself is 600 ppi (there is no more detail to recover). crop.py caches each page's render, so the
  FIRST crop of a page takes a few seconds to ~30s and later crops of the same page are instant. Run ONE crop at a time:
  two other readers share this small (2-core) machine. Use the 2000px JPEG (also cropped, e.g. with PIL) to locate
  things first.
- OCR and image of a page should be used together: OCR to find what is there, the image to read
  names, addresses and numbers exactly.
- READ PAGES 1 AND 4 OF EVERY ISSUE IN FULL FROM IMAGE CROPS, column by column (7 columns, about five slices each, ONE
  column per crop, not two-column or wider strips), on your FIRST pass. Do NOT triage these pages from the OCR text or from
  headings. In past runs readers triaged them and had to be sent back; a report that says pages 1 and 4 were not read in
  full will be sent back again. Page 1 carries letters and church news, page 4 the ads and notices. Read the local, notice,
  marriage, death and advertisement columns of pages 2 and 3 from crops as well, and the foot of page 3. (For the short
  issue, read in full whatever pages are present: August 11 is pages 3-4 only, so read BOTH of its pages in full.)
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

## Topics to WATCH FOR this quarter (July - September 1866)
Tag these in your notes and make sure each is captured as an article/event with full rosters:
- PARADES AND PROCESSIONS (owner tracks this as a topic): receptions, Sabbath-school and society processions, excursions,
  picnics, lodge turnouts, funeral processions, and any Fourth of July or August 1 (West India Emancipation) observance.
  Summer is excursion season: watch for railroad excursions and the companies that ran them (the OCR of Jul 28 p3
  suggests a notice naming the "Delany Guards" [VERIFY]: read it from the image). For each: date, route or place, the marshals, the societies, lodges, schools, military
  companies and bands that marched, speakers, and any interference by police or mobs.
- STREETCAR exclusion (topic): every ejection, petition, meeting, letter, editorial, court case, car company vote.
- MIGRATIONS (owner tracks this as a topic): people and missionaries leaving or arriving: emigration to Haiti, Liberia,
  West Africa, Canada, the Pacific coast; A.M.E. missions to the South and missionaries leaving Philadelphia (the South
  Carolina correspondence continues this quarter); the African Civilization Society and its emigration work; Major Martin
  R. Delany; Rev. T. M. D. Ward in/to California; manumitted or relocating families. Capture date, origin, destination,
  names and the organizing committee.
- INFORMATION WANTED notices (people searching for family separated by slavery and war; several run on page 3 this
  quarter): capture those with a Philadelphia or nearby link as notices with the named people; for the others, record the
  names in the issue notes only (same rule as other non-Philadelphia names).
- THE A.M.E. CHURCH SEMI-CENTENARY (50th anniversary of the A.M.E. Church, 1816-1866): any further celebrations, reports,
  subscriptions or processions. Record each printing separately and note it (the owner's merge question is still open).
- THE CENTENARY OF METHODISM (1866, the centenary of American Methodism; an item headed "The Centenary of Methodism" runs
  on Sep 15 p2). This is a DIFFERENT observance from the A.M.E. Semi-Centenary: never merge or conflate them. Capture any
  Philadelphia A.M.E. participation, committees and collections.
- SOCIETY MEETINGS (owner's instruction): every meeting, anniversary, election, installation or notice of a beneficial,
  literary, temperance, relief or burial society, lodge, association or church society, each as its own EVENT with the full
  name as printed, date, place with address, and every officer, committee member and speaker.
- THE EQUAL RIGHTS LEAGUE: the Pennsylvania State Equal Rights League, the National Equal Rights League (an item headed
  "Annual Meeting of the National Equal Rights League" runs on Aug 18 p1, and more on Aug 18 p2), the Philadelphia
  auxiliaries, the suffrage question, delegates elected (with names).
- RETURNING colored regiments and their receptions; Camp William Penn; deaths of soldiers and chaplains; bounty, back-pay and
  pension notices naming Philadelphians.
- BASE BALL AND CRICKET CLUBS (owner now tracks sports clubs): the Pythian and Excelsior clubs of Philadelphia and any match,
  meeting, officer or founding notice; record members as printed (O. V. Catto, etc.).
- THE WESLEY CHURCHES BY NAME: owner's rulings: Hurst Street Wesley is LITTLE WESLEY (A.M.E.); Lombard Street Wesley is
  BIG WESLEY (A.M.E. Zion), also printed "First Colored Wesley Church"; plain "Wesley Church" notices default to the Little
  Wesley lane but FLAG them. Record each exactly as printed.
- PHILADELPHIA ANNUAL CONFERENCE follow-up (the spring 1866 session was captured last quarter): appointments taking effect,
  Bishop J. P. Campbell; Rev. William Moore and Bethel; Bethel's new pastor James Hollen; the Book Concern. Minutes of OTHER
  conferences (New England, Indiana, etc.) are non-Philadelphia: summary text only, except bishops and Philadelphia
  Conference clergy.
- Camp meetings (summer season), quarterly meetings, church dedications and corner stones in and near Philadelphia;
  freedpeople relief, fairs and festivals; Institute for Colored Youth, the public colored schools (teachers named), the
  Banneker Institute.
- THE "MRS. J." ICE CREAM SALOON (an OPEN owner question): this ad was left off the ads page in Run #96 because the surname
  was illegible. It runs on page 3 through this quarter (seen at least Jul 7, Jul 21, Aug 11, Sep 22), on Lombard Street.
  The OCR suggests a surname like "Culyahouse" [VERIFY]: that is a guess, not a reading. Read EVERY printing in your issues
  at DPI=1600, compare them, and record the proprietor's name and street number only as far as you can actually read them.
  If one printing is clear, enter the ad once at that printing; if no printing is clear, keep the [VERIFY] and say which
  letters are certain.
- HOUSTON & BOLING, dealers in flour, starch, soaps, &c., on South Street (page 3 from Jul 7): not in the captured lists.
  Capture it once as an advertisement with the proprietors and address as printed, and FLAG it "ownership not established"
  so the owner can decide whether it belongs.
- NEW or changed Black-owned ads; marriages and deaths of Philadelphians, with officiating ministers.

## Already captured (through June 30, 1866) -- do NOT re-enter unless the ad/notice has CHANGED
Everything in the Christian Recorder THROUGH THE JUNE 30, 1866 ISSUE is already in the database (Runs #74-#96). A repeated
ad or standing notice is entered once; an ad whose address, proprietor or wording has CHANGED is new. Many of the 1865-66 ads
and notices below will still be running in Jul-Sep 1866: note the repeat, do not re-enter.

### Run #96 (April - June 1866) -- note repeats, do NOT re-enter
Standing ads entered once in Apr-Jun 1866: the Great Union Intelligence Office (proprietor also printed "E. Demund & Co.");
Mrs. Sarah Irons, 619 Pine, shrouding and laying out the dead; Robert Jones, room to rent for societies, No. 6 North 8th
St.; the Security Life Insurance Co. (Jos. C. Bustill, solicitor; N. L. Durham also solicitor, 911 1/2 Christian St.); the
African Civilization Society ad (with its branch office). NOT captured: the "Mrs. J." ice cream saloon (see the watch list).
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
White-run standing ads seen this quarter that the SKIP rule already covers (note once, do not enter): Ayer's Sarsaparilla and
Cathartic Pills; the Pennsylvania Central Railroad; the "Vermifuge" ad.

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
