"""LetterLoom page generator.

Usage:  python3 gen.py DOMAIN_URL [OUT_DIR] [--count N]

  --count N   number of word pages to build (default 300). Pages are ranked by
              how much unique content they have, so a larger N always contains
              the pages from a smaller N. Raise it gradually (300 -> 600 -> ...)
              as Search Console shows the earlier batches being indexed.

Every page must pass a minimum unique-text check; thin pages are skipped.
The sitemap lists the hand-built pages from sitemap-core.xml plus the pages built here.
"""
from urllib.parse import urlparse
import sys,os,re,gzip,base64,itertools,html,collections,json
args=[a for a in sys.argv[1:] if not a.startswith('--')]
COUNT=300
if '--count' in sys.argv:COUNT=int(sys.argv[sys.argv.index('--count')+1]);args=[a for a in args if a!=str(COUNT)]
DOM=(args[0] if args else 'https://YOURDOMAIN.com').rstrip('/');OUT=args[1] if len(args)>1 else 'site'
NAME='LetterLoom';PFX=urlparse(DOM).path.rstrip('/');MIN_WORDS=220
EX=["qi", "za", "ki", "zo", "fe", "gi", "ok", "ew", "da", "po", "te", "qis", "zas", "kis", "zos", "gis"]
W=sorted({w.strip() for w in open('enable.txt') if w.strip().isalpha() and 2<=len(w.strip())<=15}|set(EX));S=set(W)
DF={}
for l in gzip.decompress(base64.b64decode(open('defs.b64').read())).decode().split('\n'):
    if l:
        w,p,g=l.split('\t')
        DF.setdefault(w,(p,g))
def mk(s):
    o={}
    for g in s.split():
        l,v=g.split(':')
        for c in l:o[c]=int(v)
    return o
SC=mk('aeilnorstu:1 dg:2 bcmp:3 fhvwy:4 k:5 jx:8 qz:10');WF=mk('aeiorst:1 dln:2 ghy:3 bcfmpw:4 kv:5 x:8 jqz:10 u:2')
pts=lambda w,t:sum(t[c] for c in w)
sig=lambda w:''.join(sorted(w))
LET='abcdefghijklmnopqrstuvwxyz';VOW=set('aeiou')
BY=collections.defaultdict(list)
for w in W:BY[sig(w)].append(w)
CAND=sorted(w for w in W if w in DF and 5<=len(w)<=8 and w.isalpha())
def subwords(w):
    s=sig(w);subs={}
    for k in range(2,len(w)):
        for cmb in set(itertools.combinations(s,k)):
            for x in BY.get(''.join(cmb),[]):subs[x]=1
    return subs
# rank candidates by richness
rank=[]
for w in CAND:
    an=[x for x in BY[sig(w)] if x!=w];subs=subwords(w)
    nd=sum(1 for x in subs if x in DF)
    if len(subs)<6:continue
    rank.append((-(len(an)>0)*40-min(nd,60)-len(an)*5,w))
rank.sort();CHOSEN=[w for _,w in rank][:COUNT*2]  # pool; the text check trims further
CSS='body{font:16px/1.65 ui-rounded,system-ui,sans-serif;margin:0;background:#E9EFF1;color:#12202B}main{max-width:760px;margin:auto;padding:16px}a{color:#0E7C86}.t{display:inline-block;background:#F2B544;color:#2A1D00;font-weight:800;border-radius:6px;padding:4px 9px;margin:2px;box-shadow:0 2px 0 #0004}.c{display:inline-block;background:#fff;border:1px solid #CFDAE0;border-radius:8px;padding:2px 9px;margin:3px;text-decoration:none;text-transform:uppercase;font-weight:700}.c sub{font-weight:600;opacity:.7}.go{display:inline-block;background:#0E7C86;color:#fff!important;border-radius:10px;padding:10px 18px;font-weight:800;text-decoration:none}.cr{font-size:.85em;margin-top:1em}nav.top{display:flex;gap:1rem;flex-wrap:wrap;font-weight:700}details{background:#fff;border:1px solid #CFDAE0;border-radius:10px;padding:.6rem .9rem;margin-top:.5rem}summary{cursor:pointer;font-weight:700}footer{margin-top:3rem;padding-top:1.2rem;border-top:1px solid #CFDAE0;font-size:.875rem;opacity:.9}footer a{margin-right:1rem}@media(prefers-color-scheme:dark){body{background:#0E1519;color:#E8EEF1}.c,details{background:#17222A;border-color:#27363F}a{color:#43C0CB}footer{border-color:#27363F}}'
FOOT=f'<footer><nav aria-label="Footer"><a href="/guides.html">Tools &amp; Guides</a><a href="/browse/">Word Lists</a><a href="/about.html">About</a><a href="/contact.html">Contact</a><a href="/privacy.html">Privacy Policy</a><a href="/terms.html">Terms of Use</a></nav><p>&copy; 2026 {NAME}. Word list: ENABLE; points use standard Scrabble and Words With Friends tile values. Always check disputed words in your game\'s own dictionary. Not affiliated with Scrabble, Hasbro, Mattel, Words With Friends or Wordscapes.</p></footer>'
urls=[];GEN=set(CHOSEN)
def textwords(b):return len(re.sub(r'<[^>]+>',' ',b).split())
def page(path,title,desc,body,crumbs,extra=''):
    d=os.path.join(OUT,path.strip('/'));os.makedirs(d,exist_ok=True);u=DOM+path
    urls.append(u)
    ld={"@context":"https://schema.org","@graph":[{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":DOM+p} for i,(n,p) in enumerate(crumbs+[(title,path)])]}]+([extra] if extra else [])}
    H=(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | {NAME}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{u}"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{u}"><meta property="og:type" content="article"><script type="application/ld+json">{json.dumps(ld)}</script><style>{CSS}</style></head><body><main><nav class="top"><a href="/">{NAME}</a><a href="/guides.html">Tools &amp; Guides</a><a href="/browse/">Word Lists</a></nav>{body}{FOOT}</main></body></html>').replace('href="/','href="'+PFX+'/')
    open(os.path.join(d,'index.html'),'w',encoding='utf-8').write(H)
def lk(w):return f'<a class="c" href="/unscramble/{w}/">{w}</a>' if w in GEN_OK else f'<span class="c">{w}</span>'
def tiles(w):return ''.join(f'<span class="t">{c.upper()}</span>' for c in w)
def gl(w):
    p,g=DF[w];return f'{html.escape(g)} ({p})'
def ordn(n):return {1:'one',2:'two',3:'three',4:'four',5:'five',6:'six',7:'seven',8:'eight'}.get(n,str(n))
PREF=collections.defaultdict(list)
for w in CHOSEN:PREF[w[:3]].append(w)
GEN_OK=set()
built=[]
def build_word(w):
    s=sig(w);an=[x for x in BY[s] if x!=w];subs=subwords(w);U=w.upper();L=len(w)
    if len(subs)<6:return None
    sl=sorted(subs,key=lambda x:(-len(x),x not in DF,x))
    by=collections.defaultdict(list)
    for x in sl:by[len(x)].append(x)
    nv=sum(c in VOW for c in w);nc=L-nv;heavy=max(w,key=lambda c:(SC[c],c));hv=SC[heavy]
    sp,wp=pts(w,SC),pts(w,WF);dups=[c for c,k in collections.Counter(w).items() if k>1]
    b=f'<h1>Unscramble {U}</h1><p>{tiles(w)}</p>'
    b+=f'<p><b>{U}</b> is a valid word meaning: {gl(w)}. It has {L} letters ({nv} vowel{"s" if nv!=1 else ""} and {nc} consonant{"s" if nc!=1 else ""}) and scores <b>{sp}</b> points in Scrabble and <b>{wp}</b> in Words With Friends'+(f', a difference of {abs(sp-wp)} point{"s" if abs(sp-wp)!=1 else ""}' if sp!=wp else ', the same in both games')+f'. Its most valuable tile is {heavy.upper()}, worth {hv} point{"s" if hv!=1 else ""} in Scrabble.</p>'
    # bingo / length note
    if L==7:b+=f'<p>Because {U} uses all seven tiles of a rack, playing it earns the 50-point Scrabble bonus, for a total of <b>{sp+50}</b> points before premium squares.</p>'
    elif L<7:b+=f'<p>{U} uses {ordn(L)} tiles, so it is not a bingo on its own. To use a full seven-tile rack you would need {ordn(7-L)} more compatible tile{"s" if 7-L>1 else ""}; the section below shows which single letters extend it.</p>'
    else:b+=f'<p>{U} has {L} letters, one more than a rack holds, so it can only be played through a letter already on the board. A seven-tile rack plus one board tile makes an eight-letter play.</p>'
    # anagrams
    if an:
        b+=f'<h2>Anagrams of {U}</h2><p>{ordn(len(an)).capitalize()} other valid word{"s use" if len(an)>1 else " uses"} exactly the same letters: '+' '.join(lk(x) for x in an[:20])+'.</p>'
        dl=[x for x in an if x in DF][:5]
        if dl:b+='<ul>'+''.join(f'<li><b>{x.upper()}</b>: {gl(x)}</li>' for x in dl)+'</ul>'
    else:b+=f'<h2>Anagrams of {U}</h2><p>No other word in our list uses exactly the letters of {U}, so it has no anagrams.</p>'
    # extensions
    ext=[]
    for c in LET:
        r=[x for x in BY.get(sig(w+c),[])]
        if r:ext.append((c,r))
    if ext:
        b+=f'<h2>Add one letter to {U}</h2><p>Adding a single tile to {U} can make these longer words:</p><ul>'+''.join(f'<li><b>+{c.upper()}</b>: '+', '.join(x.upper() for x in r[:4])+'</li>' for c,r in ext[:14])+'</ul>'
    else:b+=f'<h2>Add one letter to {U}</h2><p>No single extra letter turns these tiles into a longer word in our list.</p>'
    bk=[c for c in LET if w+c in S];fr=[c for c in LET if c+w in S]
    b+=f'<h2>Hooks for {U}</h2><p>'+(f'Letters that can follow it: <b>{", ".join(c.upper() for c in bk)}</b> ({", ".join((w+c).upper() for c in bk[:6])}). ' if bk else f'No letter can be added to the end of {U} to make another word. ')+(f'Letters that can come before it: <b>{", ".join(c.upper() for c in fr)}</b> ({", ".join((c+w).upper() for c in fr[:6])}).' if fr else f'No letter can be added to the front of {U}.')+' Hooks let you play a word beside tiles already on the board and score both.</p>'
    # sub words
    top=sorted(subs,key=lambda x:(-pts(x,SC),-len(x),x))[0];topw=sorted(subs,key=lambda x:(-pts(x,WF),-len(x),x))[0]
    lens=', '.join(f'{len(by[k])} of {k} letters' for k in sorted(by,reverse=True)[:4])
    b+=f'<h2>Words you can make from the letters in {U}</h2><p>Using some of these {L} tiles, you can spell <b>{len(subs)}</b> shorter words in our list: {lens}. The highest-scoring is <b>{top.upper()}</b> at {pts(top,SC)} points in Scrabble'+(f'; in Words With Friends the best is <b>{topw.upper()}</b> at {pts(topw,WF)}' if topw!=top else '')+'.</p>'
    for k in sorted(by,reverse=True):
        b+=f'<h3>{k}-letter words ({len(by[k])})</h3><p>'+' '.join(lk(x) for x in by[k][:40])+('' if len(by[k])<=40 else f' and {len(by[k])-40} more')+'</p>'
    dsub=[x for x in sl if x in DF][:6]
    if dsub:b+='<h3>What some of them mean</h3><ul>'+''.join(f'<li><b>{x.upper()}</b>: {gl(x)}</li>' for x in dsub)+'</ul>'
    # tip
    if heavy in 'jqxz':tip=f'{U} contains the {heavy.upper()}, worth {hv} points. On a triple letter square it would count {hv*3} on its own, so look for a premium square where the {heavy.upper()} also forms a second word.'
    elif nv/L>=0.6:tip=f'{U} is vowel-heavy ({nv} of {L} tiles). If most of your rack looks like this, play off some vowels and keep consonants for balance.'
    elif nv/L<=0.25:tip=f'{U} is consonant-heavy ({nc} of {L} tiles). A rack like this needs vowels to work, so consider playing a short word and drawing fresh tiles.'
    else:tip=f'{U} has a balanced mix of {nv} vowels and {nc} consonants, which is the kind of rack leave strong players aim to keep.'
    if dups:tip+=f' It repeats {" and ".join(c.upper() for c in dups)}; duplicate letters on a rack limit your options, so check whether a shorter play that uses one of them scores nearly as well.'
    b+=f'<h2>Play tip</h2><p>{tip}</p>'
    # related
    rel=[x for x in PREF[w[:3]] if x!=w and x in GEN_OK_NEXT][:12]
    if rel:b+=f'<h2>Related words</h2><p>'+' '.join(f'<a class="c" href="/unscramble/{x}/">{x}</a>' for x in rel)+'</p>'
    faq=[(f'Is {U} a valid Scrabble word?',f'{U} is in the ENABLE word list used by this site, so it is valid here. Official Scrabble dictionaries differ slightly, so confirm it in your own game if it matters.'),
         (f'How many points is {U} worth?',f'{U} is worth {sp} points in Scrabble and {wp} in Words With Friends before bonus squares'+(' and the 50-point bingo bonus' if L==7 else '')+'.'),
         (f'What words can you make from {U}?',f'You can make {len(subs)} shorter words from the letters of {U}, and {len(an)} anagram{"s" if len(an)!=1 else ""} using every letter.')]
    b+='<h2>Questions</h2>'+''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in faq)
    b+=f'<p style="margin-top:1.5rem"><a class="go" href="/#{w}">Unscramble your own letters</a> <a href="/word-checker.html#{w}">Check {U} in the word checker</a></p>'
    fq={"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}
    return dict(body=b,title=f'Unscramble {U}: Anagrams, Points and Words You Can Make',desc=f'Unscramble {U}: {sp}-point Scrabble score, {len(an)} anagram{"s" if len(an)!=1 else ""}, definition, hooks and {len(subs)} shorter words you can make from the same letters.',fq=fq)
# two passes: first decide which pages pass the text check, then render with links
GEN_OK_NEXT=set(CHOSEN)
res={}
for w in CHOSEN:
    r=build_word(w)
    if r and textwords(r['body'])>=MIN_WORDS:res[w]=r
final=[w for w in CHOSEN if w in res][:COUNT]
GEN_OK=set(final);GEN_OK_NEXT=set(final)
for w in final:
    r=build_word(w)
    page(f'/unscramble/{w}/',r['title'],r['desc'],r['body'],[('Home','/'),('Word Lists','/browse/')],r['fq'])
n=len(final)
nav=[]
def stats_p(L,label,extra_intro=''):
    tops=sorted(L,key=lambda w:(-pts(w,SC),w))[:5];lc=collections.Counter(c for w in L for c in set(w)).most_common(5)
    vs=sum(c in VOW for w in L for c in w)/max(1,sum(len(w) for w in L))
    return (f'<p>{extra_intro}The highest-scoring {label} in our list is <b>{tops[0].upper()}</b> at {pts(tops[0],SC)} Scrabble points; the next best are {", ".join(f"<b>{w.upper()}</b> ({pts(w,SC)})" for w in tops[1:])}. '
            f'The letters that appear in the most of these words are {", ".join(c.upper() for c,_ in lc)}, and about {round(vs*100)}% of all their letters are vowels.</p>')
def sample_defs(C,k=6):
    pick=sorted(C,key=lambda w:(-len(w),w))[:200:max(1,min(200,len(C))//k)][:k]
    return '<h2>Some common examples</h2><ul>'+''.join(f'<li><b>{w.upper()}</b>: {gl(w)}</li>' for w in pick)+'</ul>' if pick else ''
for k in range(2,11):
    L=[w for w in W if len(w)==k];C=[w for w in L if w in DF]
    show=L if k<=5 else C
    cnts=collections.Counter(w[0] for w in L).most_common(3);ends=collections.Counter(w[-1] for w in L).most_common(3)
    body=f'<h1>{k}-letter words</h1><p>Our list contains {len(L):,} valid {k}-letter words. '+('All are shown below.' if k<=5 else f'The {len(C):,} most common are shown below.')+f' The most frequent starting letters are {", ".join(c.upper() for c,_ in cnts)}, and the most frequent final letters are {", ".join(c.upper() for c,_ in ends)}.</p>'+stats_p(L,f'{k}-letter word')
    if k==7:body+='<p>Seven-letter words matter in Scrabble because using all seven tiles earns a 50-point bingo bonus. See the <a href="/bingo-finder.html">bingo finder</a> to find them from your rack.</p>'
    if k==2:body+='<p>Two-letter words are the key to parallel plays. See our <a href="/two-letter-words.html">two-letter words guide</a> for tips.</p>'
    body+=sample_defs(C)+'<h2>Full list</h2><p>'+' '.join(lk(w) for w in show)+'</p>'
    if textwords(body)<MIN_WORDS:continue
    page(f'/{k}-letter-words/',f'{k}-Letter Words: Complete List for Scrabble and Word Games',f'Every {k}-letter word for Scrabble, Words With Friends and Wordle-style games. {len(L):,} words in the list, with top scorers and examples.',body,[('Home','/'),('Word Lists','/browse/')]);nav.append((f'/{k}-letter-words/',f'{k}-letter words'))
for c in LET:
    for kind,f in (('starting-with',lambda w:w.startswith(c)),('ending-with',lambda w:w.endswith(c))):
        L=[w for w in W if f(w)];C=[w for w in L if w in DF];lbl=kind.replace('-',' ')
        bl=collections.Counter(len(w) for w in L)
        pos=(lambda w:w[1] if len(w)>1 else '') if kind=='starting-with' else (lambda w:w[-2] if len(w)>1 else '')
        nxt=collections.Counter(pos(w) for w in L).most_common(4)
        body=f'<h1>Words {lbl} {c.upper()}</h1><p>Our list has {len(L):,} words {lbl} {c.upper()}, from {min(bl)} to {max(bl)} letters long. The most common length is {bl.most_common(1)[0][0]} letters ({bl.most_common(1)[0][1]:,} words). '+(f'The most frequent second letters are {", ".join(x.upper() for x,_ in nxt)}.' if kind=='starting-with' else f'The letter most often just before the final {c.upper()} is {nxt[0][0].upper()}.')+'</p>'+stats_p(L,f'word {lbl} {c.upper()}')
        if c in 'jqxz':body+=f'<p>{c.upper()} is a high-value tile worth {SC[c]} points in Scrabble, so words with it can score well even when short.</p>'
        body+=sample_defs(C)+f'<h2>Most common words {lbl} {c.upper()}</h2><p>'+' '.join(lk(w) for w in sorted(C,key=lambda w:(-len(w),w))[:300])+'</p>'
        if textwords(body)<MIN_WORDS:continue
        page(f'/words-{kind}-{c}/',f'Words {lbl.title()} {c.upper()}: Scrabble Word List',f'Words {lbl} {c.upper()} for Scrabble, Words With Friends and more. {len(L):,} valid words with top scorers and examples.',body,[('Home','/'),('Word Lists','/browse/')]);nav.append((f'/words-{kind}-{c}/',f'{lbl} {c.upper()}'))
wl=''.join(f'<a class="c" href="/unscramble/{w}/">{w}</a>' for w in sorted(final))
page('/browse/','Browse Word Lists by Length and Letter',f'Browse {NAME} word lists: words by length, words starting or ending with each letter, and unscrambled word pages.',f'<h1>Browse word lists</h1><p>Lists by length and by starting or ending letter, plus pages that unscramble individual words.</p><h2>Lists</h2><p>'+' '.join(f'<a class="c" href="{u}">{t}</a>' for u,t in nav)+f'</p><h2>Unscrambled words ({len(final)})</h2><p>{wl}</p>',[('Home','/')])
core=[]
if os.path.exists('sitemap-core.xml'):core=re.findall(r'<loc>(.*?)</loc>',open('sitemap-core.xml').read())
else:core=[DOM+'/']
core=[re.sub(r'^https?://[^/]+(?:/[^/]+)?/',DOM+'/',u) if False else u for u in core]
open(os.path.join(OUT,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{u}</loc></url>' for u in core+urls)+'</urlset>')
open(os.path.join(OUT,'robots.txt'),'w').write(f'User-agent: *\nAllow: /\nSitemap: {DOM}/sitemap.xml\n')
print(n,'word pages;',len(urls),'generated urls;',len(core),'core urls')
