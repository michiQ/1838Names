#!/usr/bin/env node
/*
 * Browserless replacement for precompute_fullmap.js (added 2026-08-14).
 *
 * The original bake needs Playwright/Chromium, which the cloud sandbox can't
 * install (ARM + no root + proxy-blocked apt). But the viewer's layout code is
 * pure JS with no real DOM dependency beyond what smoke_test.js already stubs,
 * so this script reuses that stub, executes the viewer's script blocks, then
 * drives the same code path the browser would: null the cache, enter full view,
 * buildFullGraph(), drain the settle ticks, and dump _fullLayoutCache to
 * pipeline/fullmap_layout.json (same format the viewer's BAKED_FULLMAP expects).
 *
 * Usage: node pipeline/bake_fullmap_node.js [indexHtmlPath] [outJsonPath]
 * After it writes the JSON, re-run build_viewer.py to inject it.
 */
const fs = require('fs');
const path = require('path');

const HERE = __dirname;
const INDEX = process.argv[2] || path.join(HERE, '..', 'index.html');
const OUT   = process.argv[3] || path.join(HERE, 'fullmap_layout.json');

// ---- DOM stub (same shape as smoke_test.js) ----------------------------------
const els = new Map();
function mkEl(id){ return {
  id, style:{}, classList:{add(){},remove(){},toggle(){}}, dataset:{},
  textContent:'', innerHTML:'', value:'', children:[],
  appendChild(c){this.children.push(c); return c;},
  addEventListener(){}, querySelector(){return null;}, querySelectorAll(){return {forEach(){}}},
  getContext(){ return new Proxy({}, {get:(t,k)=> (k==='measureText'?()=>({width:0}):()=>{}) }); },
  clientWidth:1400, clientHeight:950, scrollTop:0, width:1400, height:950,
};}
global.document = {
  getElementById(id){ if(!els.has(id)) els.set(id, mkEl(id)); return els.get(id); },
  createElement(tag){ return mkEl(tag); },
  querySelector(){ return {textContent:'build'}; },
  querySelectorAll(){ return {forEach(){}}; },
  body: mkEl('body'),
};
global.window = new Proxy({ addEventListener(){}, innerWidth:1400 }, {
  get(t,k){ return k in t ? t[k] : undefined; },
  set(t,k,v){ t[k]=v; return true; }
});
global.devicePixelRatio = 1;
global.requestAnimationFrame = ()=>{};
global.localStorage = { getItem:()=>null, setItem(){} };
global.fetch = async ()=>({text:async()=>''});
global.location = {pathname:'/', reload(){}};
global.setTimeout = ()=>{}; global.setInterval = ()=>{};

// ---- run the viewer scripts, then drive the settle inside the same scope -----
const html = fs.readFileSync(INDEX, 'utf8');
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);

let dumped = null;
global.__BAKE_DUMP__ = s => { dumped = s; };

const driver = `
;(function(){
  if (typeof buildFullGraph !== 'function') return;   // not the graph block
  window._fullLayoutCache = null;                     // force a genuine fresh settle
  window._fullView = true;
  buildFullGraph();
  let guard = 0;
  while ((window._bigSettle||0) > 0 && guard++ < 5000) { tick(); window._bigSettle--; }
  // cache exactly as draw() does on first-settle completion
  const c = new Map();
  for (const n of nodes) c.set(n.type+'|'+n.id, {x:n.x, y:n.y, z:n.z, c:n.comm});
  __BAKE_DUMP__(JSON.stringify([...c.entries()]));
})();
`;

for (const [i, code] of blocks.entries()) {
  try { new Function(code + driver)(); }
  catch(e){ console.error(`script block ${i} failed: ${e.message}`); process.exit(1); }
}
if (!dumped || dumped === 'null') { console.error('no layout produced'); process.exit(1); }
const entries = JSON.parse(dumped);
fs.writeFileSync(OUT, JSON.stringify(entries));
console.log(`baked ${entries.length} node positions -> ${OUT} (${fs.statSync(OUT).size} bytes)`);
