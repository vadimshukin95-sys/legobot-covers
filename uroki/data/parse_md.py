import re, json, sys, glob, os
def clean(s):
    s=re.sub(r'\*\*|\\(?=[.\-])','',s).strip()
    return s
def sections(md):
    parts=re.split(r'\n\*\*(.+?)\*\*\n', '\n'+md)
    out={'_title':None}; 
    # parts: [pre, h1, body1, h2, body2...]
    for i in range(1,len(parts),2):
        out.setdefault(parts[i].strip(), parts[i+1])
    return out
def table(body):
    rows=[l for l in body.splitlines() if l.strip().startswith('|')]
    rows=[r for r in rows if not re.match(r'^\|[\s\-:|]+\|$', r.strip())]
    data=[[clean(c) for c in r.strip().strip('|').split('|')] for r in rows]
    return data[1:] if data else []
def bullets(body):
    return [clean(l[1:]) for l in body.splitlines() if l.strip().startswith('- ')]
res=[]
for f in sorted(glob.glob(sys.argv[1]+'/*.md'), key=lambda p:int(os.path.basename(p).split('-')[0])):
    md=open(f).read()
    S=sections(md)
    keys=list(S.keys())
    title=[k for k in keys if k.startswith('Занятие')][0]
    n,name=re.match(r'Занятие (\d+)\. (.+)',title).groups()
    meta=re.search(r'Возраст ([^·]+)· (\d+) минут · набор (.+)', md)
    learn=bullets(S.get('Чему научатся дети',''))
    need=table(S.get('Что понадобится',''))
    plan=table([v for k,v in S.items() if k.startswith('План занятия')][0])
    theory=table([v for k,v in S.items() if k.startswith('2. Теория')][0])
    mech=[v for k,v in S.items() if k.startswith('3. ')][0]
    m=re.search(r'найти в наборе ([^.]+?) и подержать', mech)
    elec=m.group(1) if m else ''
    qa=table([v for k,v in S.items() if k.startswith('Ответы на вопросы')][0])
    trouble=table(S.get('Частые трудности',''))
    extra=bullets(S.get('Если осталось время',''))
    steps=re.search(r'(\d+) шаг', ' '.join(learn))
    res.append(dict(n=int(n),name=name,age=meta.group(1).strip() if meta else '',minutes=int(meta.group(2)) if meta else 45,kit=meta.group(3).strip() if meta else '',
      learn=learn,need=need,plan=plan,theory=theory,elec=elec,qa=qa,trouble=trouble,extra=extra,steps=int(steps.group(1)) if steps else None))
json.dump(res,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
for r in res:
    print(r['n'],r['name'],'|',r['age'],r['minutes'],'|steps',r['steps'],'|elec:',r['elec'],'|learn0:',r['learn'][0],'|theory:',[t[0] for t in r['theory']],'|qa',len(r['qa']),'tr',len(r['trouble']),'ex',len(r['extra']))
