from urllib.parse import urlparse
import sys,os,gzip,base64,itertools,html,collections
DOM=(sys.argv[1] if len(sys.argv)>1 else 'https://YOURDOMAIN.com').rstrip('/');OUT=sys.argv[2] if len(sys.argv)>2 else 'site'
NAME='WordTiles';PFX=urlparse(DOM).path.rstrip('/')
W=sorted({w.strip() for w in open('enable.txt') if w.strip().isalpha() and 2<=len(w.strip())<=15})
DF={}
for l in gzip.decompress(base64.b64decode(open('defs.b64').read())).decode().split('\n'):
    w,p,g=l.split('\t');DF[w]=(p,g)
def mk(s):
    o={}
    for g in s.split():
        l,v=g.split(':')
        for c in l:o[c]=int(v)
    return o
SC=mk('aeilnorstu:1 dg:2 bcmp:3 fhvwy:4 k:5 jx:8 qz:10');WF=mk('aeiorst:1 dln:2 ghy:3 bcfmpw:4 kv:5 x:8 jqz:10 u:2')
pts=lambda w,t:sum(t[c] for c in w)
sig=lambda w:''.join(sorted(w))
BY=collections.defaultdict(list)
for w in W:BY[sig(w)].append(w)
PAGE=set(w for w in W if w in DF and 4<=len(w)<=10)
CSS='body{font:16px/1.6 ui-rounded,system-ui,sans-serif;margin:0;background:#E9EFF1;color:#12202B}main{max-width:760px;margin:auto;padding:16px}a{color:#0E7C86}.t{display:inline-block;background:#F2B544;color:#2A1D00;font-weight:800;border-radius:6px;padding:4px 9px;margin:2px;box-shadow:0 2px 0 #0004}.c{display:inline-block;background:#fff;border:1px solid #CFDAE0;border-radius:8px;padding:2px 9px;margin:3px;text-decoration:none;text-transform:uppercase;font-weight:700}.go{display:inline-block;background:#0E7C86;color:#fff;border-radius:10px;padding:10px 18px;font-weight:800;text-decoration:none}@media(prefers-color-scheme:dark){body{background:#0E1519;color:#E8EEF1}.c{background:#17222A;border-color:#27363F}a{color:#43C0CB}}'
urls=[]
def page(path,title,desc,body):
    d=os.path.join(OUT,path.strip('/'));os.makedirs(d,exist_ok=True);u=DOM+path
    urls.append(u)
    H=(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{u}"><style>{CSS}</style></head><body><main><nav><a href="/">{NAME}</a> · <a href="/browse/">Browse word lists</a></nav>{body}<p style="margin-top:2em;font-size:.85em">Word list: ENABLE. Points use standard Scrabble and Words With Friends tile values; always check disputed words in your game\'s own dictionary.</p></main></body></html>').replace('href="/','href="'+PFX+'/');open(os.path.join(d,'index.html'),'w').write(H)
def lk(w):return f'<a class="c" href="/unscramble/{w}/">{w}</a>' if w in PAGE else f'<span class="c">{w}</span>'
def tiles(w):return ''.join(f'<span class="t">{c.upper()}</span>' for c in w)
n=0
for w in sorted(PAGE):
    s=sig(w);an=[x for x in BY[s] if x!=w]
    subs={}
    for k in range(2,len(w)):
        for cmb in set(itertools.combinations(s,k)):
            for x in BY.get(''.join(cmb),[]):subs[x]=1
    subs=sorted(subs,key=lambda x:(-len(x),x not in DF,x))
    if len(subs)<2 and not an:continue
    by=collections.defaultdict(list)
    for x in subs:
        if len(by[len(x)])<30:by[len(x)].append(x)
    p,g=DF[w];U=w.upper()
    body=f'<h1>Unscramble {U}</h1><p>{tiles(w)}</p><p><b>{U}</b> is a valid word: {html.escape(g)} ({p}). It is worth <b>{pts(w,SC)}</b> points in Scrabble and <b>{pts(w,WF)}</b> in Words With Friends, and uses {len(w)} letters.</p>'
    if an:body+=f'<h2>Anagrams of {U}</h2><p>The same letters also spell: '+' '.join(lk(x) for x in an[:20])+'</p>'
    else:body+=f'<p>No other valid word can be made using all the letters of {U}.</p>'
    body+=f'<h2>Words you can make from the letters in {U}</h2>'
    for k in sorted(by,reverse=True):body+=f'<h3>{k}-letter words</h3><p>'+' '.join(lk(x) for x in by[k])+'</p>'
    body+=f'<p><a class="go" href="/#{w}">Unscramble your own letters</a></p>'
    page(f'/unscramble/{w}/',f'Unscramble {U}: anagrams, points and words you can make',f'Unscramble {U}: its {pts(w,SC)}-point Scrabble score, anagrams, definition and {len(subs)} shorter words you can make from the same letters.',body);n+=1
nav=[]
for k in range(2,11):
    L=[w for w in W if len(w)==k];C=[w for w in L if w in DF]
    show=L if k<=5 else C
    body=f'<h1>{k}-letter words</h1><p>{len(L):,} valid {k}-letter words in the ENABLE list. '+('All are shown below.' if k<=5 else f'The {len(C):,} most common are shown below.')+'</p><p>'+' '.join(lk(w) for w in show)+'</p>'
    page(f'/{k}-letter-words/',f'{k}-Letter Words: Complete List for Scrabble and Word Games',f'Every {k}-letter word for Scrabble, Words With Friends and Wordle-style games. {len(L):,} words in the list.',body);nav.append((f'/{k}-letter-words/',f'{k}-letter words'))
for c in 'abcdefghijklmnopqrstuvwxyz':
    for kind,f in (('starting-with',lambda w:w.startswith(c)),('ending-with',lambda w:w.endswith(c))):
        L=[w for w in W if f(w)];C=[w for w in L if w in DF]
        body=f'<h1>Words {kind.replace("-"," ")} {c.upper()}</h1><p>{len(L):,} words {kind.replace("-"," ")} {c.upper()}. Showing the {min(len(C),600)} most common, longest first.</p><p>'+' '.join(lk(w) for w in sorted(C,key=lambda w:(-len(w),w))[:600])+'</p>'
        page(f'/words-{kind}-{c}/',f'Words {kind.replace("-"," ").title()} {c.upper()}: Scrabble Word List',f'Words {kind.replace("-"," ")} {c.upper()} for Scrabble, Words With Friends and more. {len(L):,} valid words.',body);nav.append((f'/words-{kind}-{c}/',f'{kind.replace("-"," ")} {c.upper()}'))
page('/browse/','Browse Word Lists by Length and Letter',f'Browse every word list on {NAME}: words by length, and words starting or ending with each letter.','<h1>Browse word lists</h1><p>'+' '.join(f'<a class="c" href="{u}">{t}</a>' for u,t in nav)+'</p>')
open(os.path.join(OUT,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+DOM+'/</loc></url>'+''.join(f'<url><loc>{u}</loc></url>' for u in urls)+'</urlset>')
open(os.path.join(OUT,'robots.txt'),'w').write(f'User-agent: *\nAllow: /\nSitemap: {DOM}/sitemap.xml\n')
print(n,'word pages;',len(urls),'total urls')
import shutil
if os.path.exists('index.html'):shutil.copy('index.html',os.path.join(OUT,'index.html'))
