# Extraction brief: Christian Recorder, April - June 1865

You are extracting names, articles and events from issues of *The Christian Recorder*
(Philadelphia, organ of the A.M.E. Church; Rev. Elisha Weaver, General Book Steward/editor;
office and AME Book Depository at No. 619 Pine Street) for the **1838 Black Metropolis names
database**, a public-history project recovering the free Black community of antebellum
Philadelphia (c. 1780-1865). The owner is a historian who values source-critical rigor: a wrong
name is worse than a missing one, and every uncertainty must be flagged, not smoothed over.

## Inputs (scratch dir S = /tmp/claude-0/-home-claude/19f25cf0-1195-5d2b-a392-127587d9c568/scratchpad/cr92)
- OCR text: `S/txt/CR_<date>_p<N>.txt` -- one file per page, 7 columns per page separated by
  `[column N]` markers, top to bottom within each column. Microfilm OCR: names are often garbled.
- Page images: `S/jpg/CR_<date>_p<N>.jpg` (2000px wide, whole page). For READING names you need
  higher resolution: render a crop from the source PDF instead. Frame numbers: ALWAYS look the frame up in S/jobs.txt
  ('frame:slug:page'). Pages not in jobs.txt DO NOT EXIST in our copy. Cite by DATE and the issue page (1-4).
  April-June 1865 (Vol. V, Nos. 13-25): Apr 1 (frames 1-4), Apr 8 (5-8), Apr 15 (9-12), Apr 22 (13-16; printed with heavy black
  mourning rules for Lincoln), Apr 29 (17-20), May 6 (21-24), May 13 MISSING (card at frame 25: 'No. 19 missing'), May 20 (26-29),
  May 27 (30-33), Jun 3 (34-37), Jun 10 (38-41), Jun 17 (43-44 = pp3-4 only; card at frame 42: 'No. 24 first sheet missing'),
  Jun 24 (45-48). Crops: render from the PDF with
  ```
  python3 S/crop.py <frame> <x0frac> <y0frac> <x1frac> <y1frac> <out.png>
  ```
  then Read the png. Write your crops into a folder of your own, `S/crops_<your-label>/`. A single column is ~1/7 of the width;
  crops of ~1/7 width x ~1/5 height read comfortably. This file's scans are 200ppi native with very large pages: crop.py renders
  at DPI=400 by default; use `DPI=600 python3 S/crop.py ...` for rechecks. NEVER go above DPI=600 on this file (it exhausts the
  machine's memory) and run ONE crop at a time. Use the 2000px JPEG (also cropped, e.g. with PIL) to locate things first.
- OCR and image of a page should be used together: OCR to find what is there, the image to read
  names, addresses and numbers exactly.
- READ PAGES 1 AND 4 OF EVERY ISSUE IN FULL, column by column, from image crops (earlier runs missed items there: page 1 carries
  letters and church news, page 4 the ads and notices). Pages 2 and 3 carry the editorials, local news, marriages and deaths.
- SAVE YOUR JSON AFTER EACH ISSUE (rewrite the whole file each time), so nothing is lost if you are interrupted.

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

## Already captured in Runs #89-#91 (July 1864 - March 1865) -- do NOT re-enter unless changed
Hannibal Hotel (620 Pine); John Oliver's Intelligence Office (1113 Pine); Mrs. S. Shorter Hawkins's fall goods; Olive Branch (814
Lombard); Mrs. C. E. Harding (713 Lombard); Thos. J. Bowers's coal yard (631 / 634 Lombard); N. L. Durham, cupping and leeching
(911 1/2 Christian); Charles W. Brister's Continental Restaurant (717 Lombard); Mrs. Highgates, shrouding (1026 Barley); the
Sansom Street Hall and Masonic Hall mass meetings on the cars; the Syracuse delegates; the Pennsylvania State Equal Rights League
constitution, officers and the Harrisburg convention (Feb 8-10, 1865); the SCSA lecture course; the 1865 Grand Lodge rosters;
the Union League Association officers; the Charleston relief meeting; the Lebanon Cemetery notices. Everything through the
March 25, 1865 issue is in the database.

## Watch for in this quarter (April - June 1865)
- The FALL OF RICHMOND (Apr 3) and LEE'S SURRENDER (Apr 9): Philadelphia celebrations, illuminations, sermons, the U.S. Colored
  Troops entering Richmond, letters from Philadelphians in the regiments and from chaplains.
- LINCOLN'S ASSASSINATION (Apr 14-15), the mourning issue of Apr 22, and the FUNERAL IN PHILADELPHIA (the body lay in state at
  Independence Hall, Apr 22-24): who among the colored people marched or was refused a place, which churches, lodges and
  societies took part, resolutions of meetings (name every officer and committee member), memorial sermons at Bethel, Union,
  Wesley, St. Thomas', the Presbyterian and Baptist churches. Capture each meeting as its own event with its roster.
- STREETCAR exclusion: every ejection, petition, meeting, letter, editorial, court case, the car companies' votes and any
  legislative action (owner tracks a 'Streetcar discrimination' topic; mob or police violence on or around the cars counts too).
- The PHILADELPHIA ANNUAL CONFERENCE of May 1865 and its APPOINTMENTS (enter the appointments whole, as printed), ordinations,
  resolutions; the A.M.E. mission to the South (Charleston, Savannah, Wilmington, Norfolk), missionaries leaving Philadelphia.
- The Pennsylvania State EQUAL RIGHTS LEAGUE and its Philadelphia auxiliaries, the suffrage question, celebrations and
  processions; regiments returning or still at Camp William Penn; deaths of soldiers and chaplains.
- Freedpeople relief, fairs, Sabbath-school and church anniversaries, ICY examination and commencement (class lists whole),
  Banneker Institute, lodge and society elections (officer lists whole), the Book Concern.
- SOCIETY MEETINGS (owner, 2026-11-13: 'look out for society meetings'): every meeting, called meeting, anniversary, election,
  installation or standing notice of a beneficial, benevolent, literary, temperance, relief or burial society, lodge, tabernacle,
  union, association or church society (Daughters of Cornish, Woodlin, Nazrey, Dorcas, Love and Charity, Good Samaritans, Odd
  Fellows, Masons, Banneker Institute, Library Company, Ladies' Union Association, Soldiers' Relief, Publication Society, Sabbath
  school societies, and any you have not seen before). Enter each as its own EVENT with the society's full name as printed, the
  date, the meeting place with its address, and every officer, committee member and speaker with the role as printed. A
  standing notice that only repeats is noted once; a notice with a new date, place or officer is new. Small notices on page 4
  and at the foot of page 3 are easy to miss: check them in every issue.
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
