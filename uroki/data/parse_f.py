# -*- coding: utf-8 -*-
"""Парсер методичек «Путешествие по регионам» (WeDo 2.0): поля шаблона E, разметка заголовками #/##/###.
python3 parse_f.py <course_dir>"""
import re, json, sys, glob, os
sys.path.insert(0, os.path.dirname(__file__))
from parse_bc import clean, bullets, table

GENERIC = ('Титульный', 'Маршрут', 'Сборка', 'Рефлексия', 'Следующ', 'Программа', 'Эксперимент', 'Итог', 'Вопрос-задача')

def split_h(md, level):
    pat = r'\n' + '#' * level + r' ([^\n]+)\n'
    parts = re.split(pat, '\n' + md)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]

def normalize(md):
    """Уроки 1–3 размечены жирным, 4–6 — заголовками: приводим к заголовкам."""
    L = md.split('\n'); out = []; started = False
    for l in L:
        m = re.match(r'^\*\*([^*].*?)\*\*\s*$', l)
        if m and re.match(r'\d+\\?\.\s', m.group(1)): started = True
        if started and m:
            t = m.group(1)
            if re.match(r'\d+\\?\.\s', t): l = '# ' + t
            elif re.match(r'Слайд \d+', t) or re.match(r'(Образовательные|Развивающие|Воспитательные):', t): l = '### ' + t
            elif not re.match(r'(Что сказать|Цель|Тема урока|Тип урока|Продолжительность)', t): l = '## ' + t
        out.append(l)
    return '\n'.join(out)

def parse(md):
    md = normalize(md)
    head = md.split('\n# ')[0]
    hl = [clean(l.strip('*')) for l in head.splitlines() if l.strip().startswith('**')]
    les = next((x for x in hl if x.startswith('Урок')), '')
    i = hl.index(les) if les else 0
    topic = nodot(re.sub(r'^Урок \d+\.\s*', '', les))
    tagline = hl[i + 1] if i + 1 < len(hl) else ''
    m = re.search(r'дети (\d+[–-]\d+ лет)', head); age = m.group(1) if m else '8–12 лет'
    S = split_h(md, 1)
    def sec(prefix):
        return next((b for t, b in S if re.sub(r'^\d+\\?\.\s*', '', t).startswith(prefix)), '')
    les_b = next((b for t, b in S if re.match(r'\d+\\?\.\s*Урок', t)), '')
    sub = dict(split_h(les_b, 2))
    cel = re.search(r'\*\*Цель урока:\*\*\s*(.+?)(?:\n\n|$)', les_b, re.S)
    obr = re.search(r'### Образовательные:\s*\n(.+?)(?:\n###|\n##|$)', les_b, re.S)
    tasks = bullets(obr.group(1)) if obr else []
    equip = bullets(sub.get('Оборудование и материалы', ''))
    plan = [r for r in table(sub.get('Технологическая карта урока', '')) if len(r) >= 3]
    talk = []
    for t, b in split_h(sec('Подробное содержание'), 3):
        mm = re.match(r'Слайд (\d+)\.\s*(.+)', t)
        if not mm or any(g in mm.group(2) for g in GENERIC): continue
        say = re.search(r'\*\*Что сказать:\*\*\s*(.+?)(?:\n\n|$)', b, re.S)
        if say: talk.append((clean(mm.group(2)), decaps(clean(say.group(1)))))
    progs = []
    for t, b in split_h(sec('Программирование'), 2):
        mm = re.match(r'Программа № ?(\d+)\.\s*(.+)', t)
        if mm:
            g = re.search(r'(?:\*\*)?Цель(?: программы)?:(?:\*\*)?\s*(.+?)(?:\n\n|$)', b, re.S)
            idea = re.search(r'\*Идея:\s*(.+?)\*', b, re.S)
            named = re.search(r'Программа № ?\d+ для опытных:\s*«([^»]+)»\.\s*(.+?[.!?])(?:\s|$)', clean(b))
            if g: txt_ = clean(g.group(1))
            elif named: txt_ = f"Идея: «{named.group(1)[:1].upper() + named.group(1)[1:]}» — {named.group(2)[:1].lower() + named.group(2)[1:]}"
            elif idea: txt_ = 'Идея: ' + first_sent(clean(idea.group(1)))
            else: txt_ = ''
            progs.append((f"Программа {mm.group(1)}. {clean(mm.group(2))}", decaps(txt_.replace("\\>", ">").replace("\\<", "<"))))
    gl = [r for r in table(sec('Глоссарий')) if len(r) >= 2]
    extra = dict(split_h(sec('Дополнительные материалы'), 2))
    trb = next((b for t, b in extra.items() if t.startswith('Возможные затруднения')), '')
    trouble = [r for r in table(trb) if len(r) >= 2]
    t = (sec('Программирование') + ' '.join(r[2] for r in plan) + ' '.join(equip)).lower()
    elec = ['смартхаб'] + (['мотор'] if 'мотор' in t else [])
    for k in ('датчик расстояния', 'датчик движения', 'датчик наклона'):
        if k in t or k.replace('датчик ', 'датчика ') in t: elec.append(k)
    return dict(topic=topic, tagline=nodot(tagline), age=age, minutes=45, goal=clean(cel.group(1)) if cel else '',
                tasks=tasks, equip=equip, plan=plan, talk=talk[:4], progs=progs, glossary=gl, trouble=trouble, elec_list=elec)

def nodot(s): return s.rstrip(' .')

def first_sent(s):
    m = re.match(r'(.+?[.!?])(\s|$)', s)
    return m.group(1) if m else s

def decaps(s):
    """ЗЕРНО → зерно (капслок в тексте для педагога)."""
    return re.sub(r'\b[А-ЯЁ]{3,}\b', lambda m: m.group(0).lower(), s)

MODELS = {1: 'Трактор', 2: 'Плантатор (сеялка точного высева)', 3: 'Зерноуборочный комбайн', 4: 'Свеклоуборочный комбайн',
          5: 'Мельница (машина для измельчения зерна)', 6: 'Грузовой автомобиль'}

def fix_plan(plan, n):
    """В технологических картах уроков 2–6 этапы 1 и 5 скопированы из урока 1."""
    out = []
    for r in plan:
        st, tm, act = r[0], r[1], r[2]
        if n > 1 and st.startswith('1.'):
            st = '1. Организационный момент'
            act = 'Приветствует группу. Демонстрирует маршрут путешествия.' if 'маршрут' in act else 'Приветствует группу.'
        if n > 1: act = act.replace('запустить трактор', 'запустить модель')
        out.append((st, tm, act) + tuple(r[3:]))
    return out

if __name__ == '__main__':
    d = sys.argv[1]
    lst = [l.rstrip('\n').split('\t') for l in open(os.path.join(d, 'list.tsv')) if l.strip()]
    res = []
    for n, slug, name, *_ in lst:
        f = glob.glob(os.path.join(d, 'md', f'{n}-*.md'))[0]
        r = parse(open(f).read()); r.update(n=int(n), slug=slug, name=name, model=MODELS[int(n)])
        r['plan'] = fix_plan(r['plan'], int(n))
        e = r.pop('elec_list'); r['elec'] = '' if len(e) == 1 else ', '.join(e[:-1]) + ' и ' + e[-1]
        res.append(r)
    json.dump(res, open(os.path.join(d, 'lessons.json'), 'w'), ensure_ascii=False, indent=1)
    for r in res:
        print(r['n'], r['name'], '|', r['topic'], '|', r['tagline'], '|', r['age'], '|elec', r['elec'], '|goal', len(r['goal']), '|tasks', len(r['tasks']),
              '|eq', len(r['equip']), '|plan', len(r['plan']), '|talk', [t for t, _ in r['talk']], '|progs', [t[:30] for t, _ in r['progs']], '|gl', len(r['glossary']), '|tr', len(r['trouble']))
