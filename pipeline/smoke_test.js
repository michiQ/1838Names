// Minimal DOM stub: execute the viewer's main script top-to-bottom to catch runtime errors (TDZ, undefined refs).
const els = new Map();
function mkEl(id){ return {
  id, style:{}, classList:{add(){},remove(){},toggle(){}}, dataset:{},
  textContent:'', innerHTML:'', value:'', children:[],
  appendChild(c){this.children.push(c); return c;},
  addEventListener(){}, querySelector(){return null;}, querySelectorAll(){return {forEach(){}}},
  getContext(){ return new Proxy({}, {get:(t,k)=> (k==='measureText'?()=>({width:0}):()=>{}) }); },
  clientWidth:800, clientHeight:600, scrollTop:0,
};}
global.document = {
  getElementById(id){ if(!els.has(id)) els.set(id, mkEl(id)); return els.get(id); },
  createElement(tag){ return mkEl(tag); },
  querySelector(){ return {textContent:'build 2026-01-01 00:00'}; },
  querySelectorAll(){ return {forEach(){}}; },
  body: mkEl('body'),
};
global.window = new Proxy({ addEventListener(){}, innerWidth:1200 }, {
  get(t,k){ return k in t ? t[k] : undefined; },
  set(t,k,v){ t[k]=v; return true; }
});
global.devicePixelRatio = 1;
global.requestAnimationFrame = ()=>{};
global.localStorage = { getItem:()=>null, setItem(){}, };
global.fetch = async ()=>({text:async()=>''});
global.location = {pathname:'/', reload(){}};
global.setTimeout = ()=>{}; global.setInterval = ()=>{};

const fs = require('fs');
const file = process.argv[2];
const html = fs.readFileSync(file, 'utf8');
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
let failed = false;
blocks.forEach((code, i) => {
  try { new Function(code)(); console.log(`script block ${i}: OK`); }
  catch(e){ failed = true; console.log(`script block ${i}: RUNTIME ERROR -> ${e.message}`); }
});
process.exit(failed ? 1 : 0);
