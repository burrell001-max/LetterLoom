# Usage: python build_pages.py [https://yourdomain.com/]   (re-run any time; also rewrites URLs in index.html)
import re,sys,os,base64,datetime
from collections import Counter
D=os.path.dirname(os.path.abspath(__file__));os.chdir(D)
B=sys.argv[1] if len(sys.argv)>1 else 'https://burrell001-max.github.io/LetterLoom/'
B=B if B.endswith('/') else B+'/'
idx=open('index.html',encoding='utf-8').read()
prev=open('base.txt').read().strip() if os.path.exists('base.txt') else 'https://burrell001-max.github.io/LetterLoom/'
idx=idx.replace(prev,B);open('index.html','w',encoding='utf-8').write(idx);open('base.txt','w').write(B)
W=open('words.txt').read().split('\n')+['qi','za','ki','zo','fe','gi','ok','ew','da','po','te','qis','zas','kis','zos','gis'];bm=base64.b64decode(open('common.b64').read().strip())
com={w for i,w in enumerate(W) if bm[i>>3]>>(i&7)&1}
def mk(s):
    o={}
    for g in s.split():
        l,v=g.split(':')
        for c in l:o[c]=int(v)
    return o
SC=mk('aeilnorstu:1 dg:2 bcmp:3 fhvwy:4 k:5 jx:8 qz:10');WF=mk('aeiorst:1 dln:2 ghy:3 bcfmpw:4 kv:5 x:8 jqz:10 u:2');WD=mk('aeilnorst:1 du:2 gm:3 bcfhpvwy:4 k:5 x:8 jqz:10')
pt=lambda w,P=SC:sum(P[c] for c in w)
css=''.join(re.findall(r'<style>.*?</style>',idx,re.S));theme=re.search(r'<script>try\{var t=localStorage.*?</script>',idx,re.S).group(0);foot=re.search(r'<footer.*?</footer>',idx,re.S).group(0)
out=[];L='abcdefghijklmnopqrstuvwxyz'
def page(f,title,desc,h1,body):
    open(f,'w',encoding='utf-8').write(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | LetterLoom</title><meta name="description" content="{desc}"><link rel="canonical" href="{B}{f}"><meta name="robots" content="index,follow">{theme}{css}</head><body class="min-h-screen"><header class="max-w-3xl mx-auto px-4 pt-4"><a href="index.html" class="flex items-center gap-2 font-extrabold text-lg"><span class="tile w-8 h-8 grid place-items-center">L</span>LetterLoom</a></header><main class="max-w-3xl mx-auto px-4 pb-20 pg"><h1 class="text-3xl font-extrabold mt-6 leading-tight">{h1}</h1>{body}{foot}</main></body></html>');out.append((f,title))
ch=lambda ws:''.join(f'<span class="chip m-1">{w}<sub>{pt(w)}</sub></span>' for w in ws)
def grp(ws):
    h=''
    for k in sorted({len(w) for w in ws},reverse=True):
        x=[w for w in ws if len(w)==k];h+=f'<h2>{k}-letter words ({len(x):,})</h2><div>{ch(x)}</div>'
    return h
best=lambda ws,P:max(ws,key=lambda w:(pt(w,P),w))
def stats(ws):
    return f'Highest scoring: <b>{best(ws,SC).upper()}</b> in Scrabble ({pt(best(ws,SC))} points), <b>{best(ws,WF).upper()}</b> in Words With Friends ({pt(best(ws,WF),WF)}) and <b>{best(ws,WD).upper()}</b> in Wordfeud ({pt(best(ws,WD),WD)}). Points are tile values only, with no board bonuses. The number on each word is its Scrabble value.'
tool='<p>Have a rack? <a href="index.html">Use the LetterLoom word unscrambler</a> to find every playable word from your letters, with blanks, filters and points for Scrabble, Words With Friends, Wordfeud, Wordscapes and Word Cookies. The list is ENABLE, an open word list, so check disputed words in your own game.</p>'
for n in range(2,6):
    ws=[w for w in W if len(w)==n];f=f'{n}-letter-words.html'
    nav=''.join(f'<a href="{n}-letter-words-starting-with-{c}.html">{c.upper()}</a> ' for c in L if n in(4,5) and sum(1 for w in ws if w[0]==c)>=8)
    page(f,f'{n}-Letter Words: Full List with Scrabble Points',f'All {len(ws):,} valid {n}-letter words with Scrabble points. Sorted A to Z.',f'{n}-Letter Words',f'<p>There are {len(ws):,} valid {n}-letter words in our list. {stats(ws)}</p><p>'+(f'Narrow it down: {nav}' if nav else '')+f'</p><div class="mt-4">{ch(ws)}</div>{tool}')
for n in(4,5,6):
    for kind,sl,ok in(('starting-with','starting with',lambda w,c:w[0]==c),('ending-in','ending in',lambda w,c:w[-1]==c)):
        for c in L:
            ws=[w for w in W if len(w)==n and ok(w,c)]
            if len(ws)<8:continue
            e=sum(w in com for w in ws)
            page(f'{n}-letter-words-{kind}-{c}.html',f'{n}-Letter Words {sl.title()} {c.upper()}',f'{len(ws):,} {n}-letter words {sl} {c.upper()} with Scrabble points, for Wordle, Scrabble and word puzzles.',f'{n}-Letter Words {sl.title()} {c.upper()}',f'<p>{len(ws):,} valid {n}-letter words {sl} {c.upper()}, of which about {e:,} are everyday words. {stats(ws)}</p><div class="mt-4">{ch(ws)}</div><p>Other lists: <a href="{n}-letter-words.html">all {n}-letter words</a>, <a href="word-lists.html">browse every list</a>.</p>{tool}')
for c in L:
    ws=sorted((w for w in com if w[0]==c and 2<=len(w)<=9),key=lambda w:(len(w),w))
    page(f'words-starting-with-{c}.html',f'Words That Start With {c.upper()}',f'{len(ws):,} everyday words that start with {c.upper()}, grouped by length with Scrabble points.',f'Words That Start With {c.upper()}',f'<p>Everyday English words that start with {c.upper()}, from 2 to 9 letters. {stats(ws)}</p>{grp(ws)}{tool}')
M=[(sum(1<<(ord(x)-97) for x in set(w)),len(w),w) for w in W]
pop=[w for w in open('popular.txt').read().split('\n') if w];seen=set();pw=[]
for w in pop:
    s=''.join(sorted(w))
    if s not in seen:seen.add(s);pw.append(w)
pw=pw[:300]
for i,w in enumerate(pw):
    m=sum(1<<(ord(x)-97) for x in set(w));h=Counter(w);n=len(w)
    s=sorted((x for mm,k,x in M if 2<=k<=n and not mm&~m and all(h[c]>=v for c,v in Counter(x).items())),key=lambda x:(-len(x),x))
    an=[x for x in s if len(x)==n];W_=w.upper()
    nb=''.join(f'<a href="unscramble-{pw[(i+j)%len(pw)]}.html" class="chip m-1">{pw[(i+j)%len(pw)]}</a>' for j in range(1,9))
    page(f'unscramble-{w}.html',f'Unscramble {W_}: Words You Can Make',f'Unscramble {W_}: {len(an)} anagram{"s" if len(an)!=1 else ""} and {len(s):,} words you can make from the letters {W_}, with Scrabble points.',f'Unscramble {W_}',f'<p>The letters {W_} can make {len(s):,} valid words. {"The anagram"+("s" if len(an)>1 else "")+" of "+W_+" that use every letter: <b>"+", ".join(a.upper() for a in an)+"</b>." if an else ""} {stats(s)}</p>{grp(s)}<h2>More unscrambles</h2><div>{nb}</div>{tool}')
cat={}
for f,t in out:cat.setdefault(('Unscramble' if f.startswith('unscr') else 'Words starting with' if f.startswith('words-') else 'Letter-length lists' if f[0].isdigit() else ''),[]).append((f,t))
hub=''.join(f'<h2>{k}</h2><div>'+''.join(f'<a class="chip m-1" href="{f}">{t.split(":")[0].replace("Words That Start With","Starts with")}</a>' for f,t in v)+'</div>' for k,v in cat.items())
page('word-lists.html','Word Lists: Words by Length, Start and End','Browse word lists by length, first letter and last letter, plus unscramble pages for popular words, with Scrabble points.','Word Lists',f'<p>Browse word lists with Scrabble points, or <a href="index.html">unscramble your own letters</a>.</p>{hub}')
ex={'404.html'};urls=[f for f in sorted(os.listdir('.')) if f.endswith('.html') and f not in ex and not f.startswith('google')]
d=datetime.date.today().isoformat()
open('sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{B}{"" if f=="index.html" else f}</loc><lastmod>{d}</lastmod></url>' for f in urls)+'</urlset>')
open('robots.txt','w').write(f'User-agent: *\nAllow: /\nSitemap: {B}sitemap.xml\n')
print(len(out),'pages;',len(urls),'in sitemap')
