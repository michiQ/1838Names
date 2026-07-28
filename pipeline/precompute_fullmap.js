#!/usr/bin/env node
/*
 * Precompute the "All connections" map layout so the viewer's first open is instant
 * (no in-browser physics settle). Loads the built index.html in headless Chromium,
 * opens the full map, lets it settle, and dumps the settled node positions/communities
 * to pipeline/fullmap_layout.json. build_viewer.py injects that file (if present) into
 * BAKED_FULLMAP; the viewer restores it and skips the settle. If the node set later
 * changes, the viewer falls back to a live layout automatically, so a stale file is safe.
 *
 * This is an OPTIONAL, manual refresh step (needs Playwright/Chromium) -- it is NOT part
 * of the core rebuild. Re-run it after a data change if you want the first open to stay
 * instant:  node pipeline/precompute_fullmap.js
 *
 * Usage: node pipeline/precompute_fullmap.js [indexHtmlPath] [outJsonPath]
 */
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const HERE = __dirname;
const INDEX = process.argv[2] || path.join(HERE, '..', 'index.html');
const OUT   = process.argv[3] || path.join(HERE, 'fullmap_layout.json');
const SETTLE_TIMEOUT_MS = 120000;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 950 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('file://' + INDEX, { waitUntil: 'load' });
  await page.waitForTimeout(500);
  // open the full map (runs buildFullGraph -> non-blocking settle)
  await page.evaluate(() => document.getElementById('allbtn').click());
  const t0 = Date.now();
  let bs = await page.evaluate(() => window._bigSettle || 0);
  while (bs > 0 && Date.now() - t0 < SETTLE_TIMEOUT_MS) {
    await page.waitForTimeout(120);
    bs = await page.evaluate(() => window._bigSettle || 0);
  }
  const dump = await page.evaluate(() =>
    window._fullLayoutCache ? JSON.stringify([...window._fullLayoutCache.entries()]) : 'null');
  await browser.close();
  if (errors.length) { console.error('PAGE ERRORS:', errors); process.exit(1); }
  const parsed = dump === 'null' ? null : JSON.parse(dump);
  if (!parsed || !parsed.length) { console.error('No layout captured (settle incomplete?)'); process.exit(1); }
  // round coordinates to 1 decimal to keep the file small; positions need no more precision
  for (const [, v] of parsed) { v.x = Math.round(v.x*10)/10; v.y = Math.round(v.y*10)/10; v.z = Math.round(v.z*10)/10; }
  fs.writeFileSync(OUT, JSON.stringify(parsed));
  console.log(`wrote ${OUT}: ${parsed.length} nodes, settle wall ${((Date.now()-t0)/1000).toFixed(1)}s, ${(fs.statSync(OUT).size/1024).toFixed(0)} KB`);
})();
