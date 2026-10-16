# -*- coding: utf-8 -*-
"""Парсер методичек шаблонов B (SPIKE Essential ч.3–4) и C (WeDo «Робо-парк").
python3 parse_bc.py B|C <course_dir>   (берёт <dir>/md/*.md и <dir>/list.tsv, пишет <dir>/lessons.json)"""
import re, json, sys, glob, os

def clean(s):
    s = re.sub(r'\*\*|\\(?=[.\-*()\[\]])', '', s)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def bullets(body):
    out, cur = [], None
    for l in body.splitlines():
        m = re.match(r'^\s*(?:-|\d+\.)\s+(.*)', l)
        if m:
            if cur is not None: out.append(clean(cur))
            cur = m.group(1)
        elif cur is not None and l.startswith('  ') and l.strip():
            cur += ' ' + l.strip()
        elif cur is not None and not l.strip():
            continue
        elif cur is not None:
            out.append(clean(cur)); cur = None
    if cur is not None: out.append(clean(cur))
    return [b for b in out if b]

def table(body):
    rows = [l for l in body.splitlines() if l.strip().startswith('|')]
    rows = [r for r in rows if not re.match(r'^\|[\s\-:|]+\|$', r.strip())]
    data = [[clean(c) for c in r.strip().strip('|').split('|')] for r in rows]
    return data[1:] if data else []

def paras(body):
    ps = [clean(p) for p in re.split(r'\n\s*\n', body)]
    return [p for p in ps if p and not p.startswith('|') and not p.startswith('<') and not p.startswith('-')]

def mins(rng):
    m = re.match(r'(\d+)\s*[–-]\s*(\d+)', rng)
    return int(m.group(2)) - int(m.group(1)) if m else None

def first_sentence(s):
    m = re.match(r'(.+?[.!?])(\s|$)', s)
    return m.group(1) if m else s

def detect_elec_ess(text):
    t = text.lower()
    e = ['хаб']
    two = bool(re.search(r'двумя моторами|два мотора|оба мотора|портам a|моторы\b|второй мотор', t))
    if 'мотор' in t: e.append('два мотора' if two else 'мотор')
    if 'датчик цвета' in t or 'датчика цвета' in t or 'датчиком цвета' in t: e.append('датчик цвета')
    if 'матриц' in t: e.append('световая матрица')
    return e

def detect_elec_wedo(text):
    t = text.lower()
    e = ['смартхаб']
    if 'мотор' in t: e.append('мотор')
    if 'датчик движения' in t or 'датчика движения' in t or 'датчиком движения' in t: e.append('датчик движения')
    if 'датчик наклона' in t or 'датчика наклона' in t or 'датчиком наклона' in t: e.append('датчик наклона')
    return e

def join_elec(e):
    return e[0] if len(e) == 1 else ', '.join(e[:-1]) + ' и ' + e[-1]

def split_bold(md):
    parts = re.split(r'\n\*\*(.+?)\*\*\n', '\n' + md)
    out = []
    for i in range(1, len(parts), 2):
        out.append((clean(parts[i]), parts[i + 1]))
    return out

def parse_B(md, meta):
    secs = split_bold(md)
    get = lambda name: next((b for t, b in secs if t.startswith(name)), '')
    head = md.split('──')[0]
    m = re.search(r'·\s*(\d+[–-]\d+ лет)\s*·\s*(\d+) минут', head)
    age, minutes = (m.group(1), int(m.group(2))) if m else ('6–9 лет', 45)
    goal = ' '.join(paras(get('Цель занятия')))
    need = [re.sub(r'\s*\(файл \d+\)', '', b) for b in bullets(get('Что понадобится'))]
    plan = table(get('План занятия'))
    steps = None
    for r in plan:
        s = re.search(r'(\d+) шаг', ' '.join(r))
        if s: steps = int(s.group(1)); break
    # теория: заголовки между «Теория: что рассказать» и «Мини-опыт»
    names = [t for t, _ in secs]
    i0 = names.index('Теория: что рассказать') if 'Теория: что рассказать' in names else -1
    i1 = names.index('Мини-опыт') if 'Мини-опыт' in names else len(names)
    theory = []
    for t, b in secs[i0 + 1:i1]:
        bl = bullets(b)
        if bl: theory.append((t, bl))
    # мини-опыт: следующий за «Мини-опыт» заголовок
    exp = None
    if 'Мини-опыт' in names:
        j = names.index('Мини-опыт')
        t, b = secs[j + 1] if j + 1 < len(secs) else ('', '')
        exp = (t, bullets(b))
    discuss = bullets(get('Вопросы для обсуждения'))
    model = bullets(get('Как устроена модель'))
    scripts = [re.sub(r'^Скрипт \d+\s*[—-]\s*', '', t) for t, _ in secs if t.startswith('Скрипт ')]
    prog_text = get('Программа') + ' '.join(b for t, b in secs if t.startswith('Скрипт '))
    # задания на доработку: заголовки «1. ...»
    k0 = names.index('Задания на доработку') if 'Задания на доработку' in names else -1
    tasks = []
    if k0 >= 0:
        for t, b in secs[k0 + 1:]:
            if not re.match(r'^\d+\.', t): break
            ps = paras(b)
            tasks.append((re.sub(r'^\d+\.\s*', '', t), first_sentence(ps[0]) if ps else ''))
    qa = table(get('Проверочные вопросы'))
    trouble = bullets(get('Типичные трудности'))
    elec = join_elec(detect_elec_ess(md))
    return dict(age=age, minutes=minutes, goal=goal, need=need, plan=plan, steps=steps, theory=theory,
                exp=exp, discuss=discuss, model=model, scripts=scripts, tasks=tasks, qa=qa, trouble=trouble,
                elec=elec, homework=' '.join(paras(get('Домашнее задание'))))

def parse_C(md, meta):
    lines = md.splitlines()
    tagline = ''
    nm = None
    for i, l in enumerate(lines[:12]):
        if l.startswith('**') and 'ЗАНЯТИЕ' not in l and nm is None:
            nm = clean(l)
            for l2 in lines[i + 1:i + 5]:
                if l2.strip():
                    tagline = clean(l2); break
    params = {r[0]: r[1] for r in table(md.split('1\\. Идея занятия')[0])}
    age = re.sub(r'\s*\(.*\)', '', params.get('Возраст', '6–8 лет'))
    minutes = int(re.search(r'\d+', params.get('Продолжительность', '45')).group(0))
    files = params.get('Файлы к занятию', '')
    s = re.search(r'(\d+) шаг', files); steps = int(s.group(1)) if s else None
    sl = re.search(r'(\d+) слайд', files); slides = int(sl.group(1)) if sl else None
    secs = re.split(r'\n(\d+)\\\. ([^\n]+)\n', '\n' + md)
    S = {}
    for i in range(1, len(secs), 3):
        S[int(secs[i])] = (secs[i + 1].strip(), secs[i + 2])
    body = lambda k: S.get(k, ('', ''))[1]
    idea = paras(body(1))
    res = body(2)
    subj = bullets(res.split('Метапредметные')[0].split('Предметные')[-1]) if 'Предметные' in res else bullets(res)
    meta_r = bullets(res.split('Метапредметные')[1].split('Личностные')[0]) if 'Метапредметные' in res else []
    plan = table(body(4))
    model = paras(body(5))
    prog = body(6)
    tasks = []
    for m in re.finditer(r'\n(Задание \d+\.[^\n]*)\n', '\n' + prog):
        tasks.append(clean(m.group(1)))
    game = paras(body(7))
    trouble = table(body(8))
    qa = table(body(9))
    diff = bullets(body(10).split('Тем, кому трудно')[0])
    hw = paras(body(11))
    elec = join_elec(detect_elec_wedo(' '.join(model) + ' ' + prog + ' ' + ' '.join(game) + ' ' + ' '.join(idea)))
    return dict(age=age, minutes=minutes, tagline=tagline, steps=steps, slides=slides, idea=idea, learn=subj,
                learn_meta=meta_r, plan=plan, model=model, tasks=tasks, game=game, trouble=trouble, qa=qa,
                diff=diff, homework=' '.join(hw), elec=elec)

if __name__ == '__main__':
    T, d = sys.argv[1], sys.argv[2]
    lst = [l.rstrip('\n').split('\t') for l in open(os.path.join(d, 'list.tsv')) if l.strip()]
    res = []
    for n, slug, name, *_ in lst:
        f = glob.glob(os.path.join(d, 'md', f'{n}-*.md'))[0]
        md = open(f).read()
        r = (parse_B if T == 'B' else parse_C)(md, {})
        r.update(n=int(n), slug=slug, name=name)
        res.append(r)
    json.dump(res, open(os.path.join(d, 'lessons.json'), 'w'), ensure_ascii=False, indent=1)
    for r in res:
        if T == 'B':
            print(r['n'], r['name'], '|', r['age'], r['minutes'], '|steps', r['steps'], '|elec:', r['elec'], '|plan', len(r['plan']),
                  '|theory', [t for t, _ in r['theory']], '|exp', (r['exp'] or ('',))[0], '|scripts', r['scripts'], '|tasks', [t for t, _ in r['tasks']],
                  '|qa', len(r['qa']), 'tr', len(r['trouble']), '|need', len(r['need']))
        else:
            print(r['n'], r['name'], '|', r['age'], r['minutes'], '|steps', r['steps'], 'slides', r['slides'], '|elec:', r['elec'], '|tag:', r['tagline'],
                  '|idea', len(r['idea']), '|learn', len(r['learn']), '|plan', len(r['plan']), '|model', len(r['model']), '|tasks', r['tasks'],
                  '|game', len(r['game']), '|tr', len(r['trouble']), '|qa', len(r['qa']), '|diff', len(r['diff']))
