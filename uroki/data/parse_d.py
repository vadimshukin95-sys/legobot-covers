# -*- coding: utf-8 -*-
"""Парсер методичек курса «Как это работает» (LEGO 9686), шаблон D.
python3 parse_d.py <course_dir>"""
import re, json, sys, glob, os
sys.path.insert(0, os.path.dirname(__file__))
from parse_bc import clean, bullets, table, paras, split_bold

def first_sentence(s):
    m = re.match(r'(.+?[.!?»])(\s|$)', s)
    return m.group(1) if m else s

def parse(md):
    secs = split_bold(md)
    names = [t for t, _ in secs]
    def get(name, start=0):
        for t, b in secs[start:]:
            if t.startswith(name): return b
        return ''
    lines = [l for l in md.splitlines() if l.strip()]
    subtitle = clean(lines[2]) if len(lines) > 2 else ''
    head = md.split('**1. ')[0]
    mm = re.search(r'(Возраст.+?)(?:\n\n|$)', head, re.S)
    meta = re.sub(r'\s+', ' ', mm.group(1)) if mm else ''
    age = (re.search(r'Возраст ([0-9–-]+ лет)', meta) or [None, '9–13 лет'])[1]
    double = 'ДВОЙНОЕ' in meta
    s = re.search(r'модель (\d+) шаг', meta); steps = int(s.group(1)) if s else None
    motor = ('нужен мотор' in meta) or ('с мотором' in meta)
    body2 = get('2. Цели и задачи')
    tema = re.search(r'\*\*Тема:\*\*\s*(.+?)(?:\n\n|$)', md, re.S)
    cel = re.search(r'\*\*Цель:\*\*\s*(.+?)(?:\n\n|$)', md, re.S)
    tasks = bullets(get('Образовательные задачи'))
    equip = bullets(get('Оборудование'))
    box = {}
    m = re.search(r'ЧТО ЗАКЛАДЫВАЕТСЯ.*?</td>', md, re.S)
    if m:
        for k, pat in (('Понятие', r'Поняти[ея]'), ('Правило', r'Правил[оа]'), ('Навык', r'Навык[и]?')):
            mm = re.search(pat + r':\s*(.+?)</p>', m.group(0), re.S)
            if mm: box[k] = clean(mm.group(1))
    plan = []
    for t, b in secs:
        if 'Технологическая карта' in t:
            part = re.search(r'Часть (\d)', t)
            for r in table(b):
                if len(r) >= 3: plan.append(((('Часть ' + part.group(1) + '. ') if part and double else '') + r[0], r[1], r[2]))
    trials = []
    for i, (t, b) in enumerate(secs):
        if re.match(r'Испытание \d+\.', t):
            mm = re.search(r'\*\*Что проверяем:\*\*\s*(.+?)(?:\n\n|$)', b, re.S)
            what = clean(mm.group(1)) if mm else ''
            trials.append((t, what))
    gl = []
    for t, b in secs:
        if t.startswith('7. Словарь'):
            gl = [r for r in table(b) if len(r) >= 2]
    trouble = []
    for t, b in secs:
        if t.startswith('Возможные затруднения') or t.startswith('5. Если что-то пошло не так'):
            trouble = [r for r in table(b) if len(r) >= 2] or [(x, '') for x in bullets(b)]
    stages = []
    if any(t.startswith('4. Как провести каждый этап') for t in names):
        i0 = names.index(next(t for t in names if t.startswith('4. Как провести')))
        for t, b in secs[i0 + 1:]:
            if re.match(r'^\d+\.', t): break
            ps = paras(b)
            if ps and len(t) < 40: stages.append((t, first_sentence(ps[0])))
    return dict(subtitle=subtitle, age=age, double=double, steps=steps, motor=motor,
                tema=clean(tema.group(1)) if tema else '', goal=clean(cel.group(1)) if cel else '',
                tasks=tasks, equip=equip, box=box, plan=plan, trials=trials, glossary=gl, trouble=trouble,
                stages=stages, minutes=45)

if __name__ == '__main__':
    d = sys.argv[1]
    lst = [l.rstrip('\n').split('\t') for l in open(os.path.join(d, 'list.tsv')) if l.strip()]
    res = []
    for n, slug, name, *_ in lst:
        f = glob.glob(os.path.join(d, 'md', f'{n}-*.md'))[0]
        r = parse(open(f).read()); r.update(n=int(n), slug=slug, name=name); res.append(r)
    json.dump(res, open(os.path.join(d, 'lessons.json'), 'w'), ensure_ascii=False, indent=1)
    for r in res:
        print(r['n'], r['name'], '|', r['subtitle'][:40], '|', r['age'], 'double' if r['double'] else '', '|steps', r['steps'], 'motor' if r['motor'] else 'nomotor',
              '|box', list(r['box']), '|tasks', len(r['tasks']), '|eq', len(r['equip']), '|plan', len(r['plan']), '|trials', [t for t, _ in r['trials']],
              '|gl', len(r['glossary']), '|tr', len(r['trouble']), '|st', [t for t, _ in r['stages']], '|goal', r['goal'][:50])
