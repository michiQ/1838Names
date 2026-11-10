
## Topic labels (added 2026-11-10)

`pipeline/topics.json` tags articles and events with a topic label, for example "Streetcar discrimination".
- Articles are keyed by issue + headline (plus page when a headline repeats in one issue); events by issue + name.
  A key that matches nothing stops `build_viewer.py`, so a renamed headline cannot silently drop out of a topic.
- Each tagged entry shows a chip. The chip opens the topic page: the note, "Read more" links (blog posts), and every
  tagged event and article in date order with scan links. Articles with no linked author are only reachable this way.
- The Events tab lists topics first and its search matches topic labels (try "streetcar").
- Deep link: `index.html#t-<slug>`, e.g. `index.html#t-streetcar-discrimination`.
- To add an entry or a new topic, edit `topics.json` and rebuild the viewer. No database change is needed.
