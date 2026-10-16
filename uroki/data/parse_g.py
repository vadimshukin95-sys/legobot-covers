# -*- coding: utf-8 -*-
"""Парсер презентаций курса «Minecraft» (WeDo 2.0), шаблон G: текст слайдов + заметки.
python3 parse_g.py <course_dir>   (нужен slides.json от extract)"""
import re, json, sys, os

def sents(s, n=1):
    parts = [p.strip() for p in re.findall(r'.+?[.!?…](?:»)?(?=\s|$)', s)]
    return ' '.join(parts[:n]) if parts else s

def is_label(t):
    return not re.search(r'[а-яё]', t) or t.strip().isdigit() or bool(re.fullmatch(r'\d+\s*мин', t.strip()))

def body(x):
    return [t.replace('\n', ' ').strip() for t in x['text'][3:]]

def _pairs(b, k):
    out = []
    i = 0
    while i < len(b) - 1 and len(out) < k:
        if len(b[i]) < 40 and not re.search(r'[.!?]$', b[i]) and len(b[i + 1]) > 20 and not is_label(b[i]):
            d = sents(b[i + 1], 1).rstrip('.')
            out.append(f"{b[i]} — {d[:1].lower() + d[1:]}."); i += 2
        else: i += 1
    return out

def lead(x):
    b = [t for t in body(x) if not t.strip().isdigit()]
    if not b: return ''
    if '·' in b[0] and is_label(b[0]) and len(b) >= 4:          # сравнение двух колонок
        out = []
        for lab, txt_ in ((b[0], b[1]), (b[2], b[3])):
            l = lab.split('·')[0].strip().lower(); d = sents(txt_, 1).rstrip('.')
            out.append(f"{l[:1].upper() + l[1:]} — {d[:1].lower() + d[1:]}.")
        return ' '.join(out)
    raw = body(x)
    if len(raw) > 3 and raw[2].strip().isdigit() and not raw[0].strip().isdigit() and not re.search(r'[.!?]$', raw[0]):
        i1 = sents(raw[1], 1)                                      # подзаголовок + вступление + нумерованный список
        head = f"{raw[0]}. {i1}" if ':' in i1 else f"{raw[0]}: {i1[:1].lower() + i1[1:]}"
        return ' '.join([head] + _pairs(b[2:], 2))
    if len(b[0]) > 30 and re.search(r'[.!?]', b[0]) and not is_label(b[0]):
        s1 = sents(b[0], 1)
        return sents(b[0], 2) if len(s1) < 45 else s1
    p = _pairs(b, 3)
    if p: return ' '.join(p)
    for t in b:
        if len(t) > 30 and not is_label(t): return sents(t, 1)
    return ''

def term(t):
    m = re.match(r'([А-ЯЁ][А-ЯЁ \-]+?)\s+—\s+(.+)', t)
    if not m: return None
    w = m.group(1).strip().lower()
    return (w[:1].upper() + w[1:], m.group(2).strip())

def decaps(s):
    return re.sub(r'\b[А-ЯЁ]{3,}\b', lambda m: m.group(0).lower(), s)

def plural(n, f): return f[0] if n % 10 == 1 and n % 100 != 11 else (f[1] if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else f[2])

def parse(sl):
    T = lambda x: x['text'][0].replace('\n', ' ').strip() if x['text'] else ''
    s1 = [t.replace('\n', ' ') for t in sl[0]['text']]
    name = s1[1].capitalize(); subtitle = s1[2]; tagline = s1[3]
    age = next((t for t in s1 if 'лет' in t), '7–9 лет')
    steps = int(re.search(r'(\d+) шаг', ' '.join(s1)).group(1))
    by = {T(x): x for x in sl}
    s2, s3 = sl[1], sl[2]
    b2, b3 = body(s2), body(s3)
    story = b2[1] if len(b2) > 1 else ''
    q = b2[b2.index('Вопрос классу') + 1] if 'Вопрос классу' in b2 else ''
    task = b3[b3.index('НАША ЗАДАЧА') + 1] if 'НАША ЗАДАЧА' in b3 else ''
    story2 = b3[1] if len(b3) > 1 else ''
    b4 = body(sl[3]); plan = []
    for i, t in enumerate(b4):
        if t.isdigit() and i + 3 < len(b4): plan.append((b4[i + 1], b4[i + 3], b4[i + 2]))
    rule = next((t for t in b4 if t.startswith('Правило урока')), '')
    theory = []
    for x in sl[4:11]:
        t = T(x)
        if t.startswith('Думаем') or t.startswith('Проверь'): continue
        ld = lead(x)
        if ld: theory.append((t, decaps(ld)))
    sec = next((x for x in sl if 'секрет' in T(x).lower()), None)
    mech_title = re.sub(r'^.*?[Сс]екрет[^:]*:\s*', '', T(sec)) if sec else ''
    mech_intro = sents(decaps(body(sec)[0]), 2) if sec else ''
    mech = [term(t) for t in body(sec)[1:]] if sec else []
    mech = [m for m in mech if m]
    ans = by.get('Проверь себя: ответы'); quiz = []
    if ans:
        b = [t for t in body(ans) if not t.startswith('Все три')]
        for i in range(0, len(b) - 2, 3):
            quiz.append((b[i], re.sub(r'^[А-В]\.\s*', '', b[i + 1]), b[i + 2]))
    progs = []
    for x in sl:
        t = T(x)
        m = re.match(r'Задание (\d)\. (.+)', t)
        if m and 'алгоритм' not in m.group(2).lower():
            progs.append((f"Задание {m.group(1)}. {m.group(2)}", decaps(sents(body(x)[0], 1)), x['notes']))
    scratch = next((decaps(sents(body(x)[0], 1)) for x in sl if T(x).startswith('Та же программа в Scratch')), '')
    inv = by.get('Задание для изобретателей'); ideas = []
    if inv:
        b = body(inv)[1:]
        b = [t for t in b if not t.startswith('Покажи')]
        ideas = [(b[i], b[i + 1]) for i in range(0, len(b) - 1, 2)]
    summ = by.get('Что мы сегодня узнали'); summary = []
    if summ:
        b = [t for t in body(summ) if not t.isdigit()]
        summary = [(b[i], b[i + 1]) for i in range(0, len(b) - 1, 2)]
    alltxt = ' '.join(' '.join(x['text']) for x in sl).lower()
    elec = ['смартхаб', 'мотор'] + (['датчик движения'] if 'датчик движения' in alltxt else []) + (['датчик наклона'] if 'датчик наклона' in alltxt else [])
    tips = [decaps(n) for _, _, n in progs if n][:3]
    return dict(name=name, subtitle=subtitle, tagline=tagline, age=age, minutes=45, steps=steps, story=story, story2=story2, question=q, task=task,
                plan=plan, rule=rule, theory=theory[:5], mech_title=mech_title, mech_intro=mech_intro, mech=mech, quiz=quiz,
                progs=[(a, b) for a, b, _ in progs], scratch=scratch, ideas=ideas, summary=summary, tips=tips,
                elec=', '.join(elec[:-1]) + ' и ' + elec[-1], author='legogbc.com', model=f'{name} — {subtitle}', slides=len(sl))

if __name__ == '__main__':
    d = sys.argv[1]
    S = json.load(open(os.path.join(d, 'slides.json')))
    lst = [l.rstrip('\n').split('\t') for l in open(os.path.join(d, 'list.tsv')) if l.strip()]
    res = []
    for n, slug, name, *_ in lst:
        f = next(k for k in S if k.split('/')[-1].split('-', 1)[1].startswith(slug))
        r = parse(S[f]); r.update(n=int(n), slug=slug); res.append(r)
    json.dump(res, open(os.path.join(d, 'lessons.json'), 'w'), ensure_ascii=False, indent=1)
    for r in res:
        print(r['n'], r['name'], '|', r['subtitle'], '|', r['steps'], '|plan', len(r['plan']), '|th', [t for t, _ in r['theory']], '|mech', r['mech_title'], len(r['mech']),
              '|quiz', len(r['quiz']), '|progs', [t for t, _ in r['progs']], '|ideas', len(r['ideas']), '|sum', len(r['summary']), '|tips', len(r['tips']), '|', r['elec'])
