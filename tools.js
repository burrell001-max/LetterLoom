const $=s=>document.querySelector(s),esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const mk=s=>{const o={};s.split(' ').forEach(g=>{const[l,v]=g.split(':');for(const c of l)o[c]=+v});return o};
const SC=mk('aeilnorstu:1 dg:2 bcmp:3 fhvwy:4 k:5 jx:8 qz:10'),WF=mk('aeiorst:1 dln:2 ghy:3 bcfmpw:4 kv:5 x:8 jqz:10 u:2');
let _W,_S,_D;
async function words(){if(!_W){const r=await fetch('words.txt');if(!r.ok)throw 0;_W=(await r.text()).split('\n').filter(Boolean);_S=new Set(_W)}return _W}
const isWord=w=>_S.has(w);
async function defs(){if(!_D){_D={};try{const r=await fetch('defs.txt');(await r.text()).split('\n').forEach(l=>{const[w,p,g]=l.split('\t');if(w&&g&&!_D[w])_D[w]=[p,g]})}catch(e){}}return _D}
const pts=(w,t=SC)=>[...w].reduce((a,c)=>a+(t[c]||0),0);
const cnt=s=>{const a=new Uint8Array(26);for(const c of s){const i=c.charCodeAt(0)-97;if(i>=0&&i<26)a[i]++}return a};
function can(w,have,blanks){const t=have.slice();let x=blanks;for(let j=0;j<w.length;j++){const q=w.charCodeAt(j)-97;if(t[q]>0)t[q]--;else if(x>0)x--;else return false}return true}
const chip=(w,p)=>`<span class="wd">${w.toUpperCase()}${p!=null?`<sub>${p}</sub>`:''}</span>`;
const seed=s=>{let h=1779033703^s.length;for(let i=0;i<s.length;i++){h=Math.imul(h^s.charCodeAt(i),3432918353);h=h<<13|h>>>19}return()=>{h=Math.imul(h^h>>>16,2246822507);h=Math.imul(h^h>>>13,3266489909);return(h^=h>>>16)>>>0}};
function failed(sel){$(sel).innerHTML='<p>Could not load the word list. Please reload the page.</p>'}
