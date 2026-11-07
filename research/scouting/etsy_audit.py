# Etsy listing audit (Nov 2026). Reads the rendered LISTING*.md files and mockups in content-factory/
# (etsy/, brands/, pod/) and checks them against etsy-seo-playbook.md. Usage: python3 etsy_audit.py [content-factory dir]
import re, os, glob, json, collections
from PIL import Image
import sys
ROOT=sys.argv[1] if len(sys.argv)>1 else "/mnt/project-files/content-factory"
files=sorted(glob.glob(f"{ROOT}/etsy/**/LISTING*.md",recursive=True)+glob.glob(f"{ROOT}/brands/**/LISTING*.md",recursive=True)+glob.glob(f"{ROOT}/pod/**/LISTING*.md",recursive=True))
STOP=set("and or for the a an to of with your in on by & + - de y para en con el la los las del e o a".split())
SUBJ=re.compile(r"\b(perfect|beautiful|cute|best|amazing|gift|gifts|stunning|unique)\b",re.I)
PRICE=re.compile(r"\b(sale|discount|% off|free shipping|cheap)\b",re.I)
rows=[]
def sec(md,name):
    m=re.search(r"^## "+re.escape(name)+r".*?\n(.*?)(?=^## |\Z)",md,re.S|re.M); return m.group(1).strip() if m else ""
for f in files:
    md=open(f).read(); d=os.path.dirname(f); rel=os.path.relpath(f,ROOT)
    t=sec(md,"Title") or sec(md,"Etsy title")
    if not t:
        m=re.search(r"\*\*Title\*\*.*\n(.+)",md); t=m.group(1) if m else ""
    title=t.splitlines()[0].strip() if t else ""
    tsec=sec(md,"Tags") or sec(md,"Etsy tags")
    m=re.search(r"\*\*Tags\*\*.*\n(.+)",md)
    if not tsec and m: tsec=m.group(1)
    tags=[re.sub(r"^\d+\.\s*","",l).strip() for l in tsec.splitlines() if re.match(r"^\d+\.",l.strip())]
    if not tags: tags=re.findall(r"`([^`]+)`",tsec)
    if not tags:
        t=sec(md,"Tags"); tags=[x.strip() for x in re.split(r",|\n",t) if x.strip() and not x.startswith("(")]
    attrs=dict(re.findall(r"^- \*\*(.+?):\*\* (.+)$",sec(md,"Attributes"),re.M))
    desc=(sec(md,"Description") or sec(md,"Etsy description")).strip("`\n ")
    cand=[os.path.join(d,x) for x in os.listdir(d) if re.match(r"(mockup|preview).*\.(png|jpe?g)$",x,re.I)]
    if os.path.isdir(os.path.join(d,"images")): cand+= [os.path.join(d,"images",x) for x in os.listdir(os.path.join(d,"images")) if x.endswith((".png",".jpg"))]
    imgs=sorted(cand)
    sizes=[Image.open(x).size for x in imgs]
    words=re.findall(r"[A-Za-z0-9$'áéíóúñ]+",title)
    low=[w.lower() for w in words if w.lower() not in STOP]
    reps=sorted({w for w in low if low.count(w)>1})
    issues=[]
    if len(words)>=15: issues.append(f"title {len(words)} words")
    if reps: issues.append("title repeats: "+", ".join(reps))
    if SUBJ.search(title): issues.append("subjective/gift word in title: "+SUBJ.search(title).group(0))
    if PRICE.search(title): issues.append("price/sale word in title")
    if len(tags)!=13: issues.append(f"{len(tags)} tags")
    long=[t for t in tags if len(t)>20]
    if long: issues.append("tags over 20 chars: "+"; ".join(long))
    one=[t for t in tags if len(t.split())==1]
    if one: issues.append("single-word tags: "+", ".join(one))
    av=" ".join(attrs.values()).lower()
    dup=[t for t in tags if t.lower() in av]
    if dup: issues.append("tags repeating attributes: "+", ".join(dup))
    if len(imgs)<5: issues.append(f"{len(imgs)} photos (Etsy allows 20)")
    if sizes and min(min(s) for s in sizes)<2000: issues.append(f"photos {sizes[0][0]}x{sizes[0][1]} (Etsy recommends 2000+ on both sides)")
    lead=" ".join(words[:2]).lower()
    first=desc.split("\n")[0].lower()
    if lead and lead not in first: issues.append(f"description's first line lacks '{lead}'")
    rows.append(dict(path=rel,title=title,words=len(words),tags=tags,attrs=attrs,photos=len(imgs),sizes=sizes[:1],issues=issues,first=first[:100]))
json.dump(rows,open("etsy_audit.json","w"),indent=1)
print(len(rows))
c=collections.Counter()
for r in rows:
    for i in r["issues"]: c[re.sub(r":.*|\d+","#",i)]+=1
for k,v in c.most_common(): print(v,k)
