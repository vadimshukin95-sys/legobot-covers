# -*- coding: utf-8 -*-
"""Парсер методичек «Мастерская изобретателя» (WeDo 2.0), шаблон E.
python3 parse_e.py <course_dir>"""
import re, json, sys, glob, os
sys.path.insert(0, os.path.dirname(__file__))
from parse_bc import clean, bullets, table, paras, split_bold

GENERIC = ('Титульный', 'Маршрут', 'Сборка', 'Рефлексия', 'Следующее', 'Программа', 'Эксперимент', 'в презентации', 'Итог', 'Награжд', 'Битва', 'Турнир')

def first_sentences(s, n=2):
    parts = re.findall(r'.+?[.!?»](?=\s|$)', s)
    return ' '.join(parts[:n]) if parts else s

def parse(md):
    lines = [l for l in md.splitlines() if l.strip()]
    title = next((clean(l) for l in lines[:10] if l.startswith('**') and '.' in l and 'КУРС' not in l and 'УРОК' not in l), '')
    topic = title.rsplit('.', 1)[0].strip() if '.' in title else title
    tagline = next((clean(l.strip('*')) for l in lines[:12] if l.startswith('*') and not l.startswith('**')), '')
    m = re.search(r'дети (\d+[–-]\d+ лет)', md[:3000]); age = m.group(1) if m else '8–12 лет'
    # секции «N\. Заголовок»
    secs = re.split(r'\n(\d+)\\\. ([^\n]+)\n', '\n' + md)
    S = [(secs[i + 1].strip(), secs[i + 2]) for i in range(1, len(secs), 3)]
    def sec(prefix):
        return next((b for t, b in S if t.startswith(prefix)), '')
    goals = sec('Цели и задачи') or next((b for t, b in S if 'Урок' in t and 'Тема' in b), '')
    cel = re.search(r'Цель урока:\s*(.+?)(?:\n\n|$)', goals, re.S)
    obr = re.search(r'Образовательные:\s*\n(.+?)(?:\n\S[^\n]*:\s*\n|\*\*|$)', goals, re.S)
    tasks = bullets(obr.group(1)) if obr else []
    eq = re.search(r'\*\*Оборудование и материалы\*\*(.+?)(?:\*\*|\n\d+\\\.|$)', md, re.S)
    equip = bullets(eq.group(1)) if eq else []
    tk = next((b for t, b in S if t.startswith('Технологическая карта')), '')
    if not tk:
        tk = re.search(r'\*\*Технологическая карта урока\*\*(.+?)(?:\n\d+\\\.|$)', md, re.S); tk = tk.group(1) if tk else ''
    plan = [r for r in table(tk) if len(r) >= 3]
    # слайды с содержанием
    slides = []
    for t, b in split_bold(sec('Подробное содержание')):
        mm = re.match(r'Слайд (\d+)\.\s*(.+)', t)
        if not mm or any(g in mm.group(2) for g in GENERIC): continue
        say = re.search(r'\*\*Что сказать:\*\*\s*(.+?)(?:\n\n|$)', b, re.S)
        if say: slides.append((clean(mm.group(2)), clean(say.group(1))))
    progs = []
    for t, b in split_bold(sec('Программирование')):
        mm = re.match(r'Программа № ?(\d+)\.\s*(.+)', t)
        if mm:
            g = re.search(r'Цель:\s*(.+?)(?:\n\n|$)', b, re.S)
            progs.append((f"Программа {mm.group(1)}. {mm.group(2)}", clean(g.group(1)) if g else ''))
    gl = [r for r in table(sec('Глоссарий')) if len(r) >= 2]
    tr = re.search(r'\*\*Возможные затруднения и пути их решения\*\*(.+?)(?:<table>|\n\*\*[^|*]|$)', md, re.S)
    trouble = [r for r in table(tr.group(1)) if len(r) >= 2] if tr else []
    warm = re.search(r'\*\*Разминка перед уроком[^*]*\*\*\s*(.+?)(?:\n\n\*\*|$)', md, re.S)
    t = (sec('Программирование') + sec('Запуск модели') + ' '.join(r[2] for r in plan) + ' '.join(equip)).lower()
    elec = ['смартхаб'] + (['мотор'] if 'мотор' in t else [])
    if 'датчик расстояния' in t or 'датчика расстояния' in t: elec.append('датчик расстояния')
    if 'датчик движения' in t or 'датчика движения' in t: elec.append('датчик движения')
    if 'датчик наклона' in t or 'датчика наклона' in t: elec.append('датчик наклона')
    return dict(topic=topic, tagline=tagline, age=age, minutes=45, goal=clean(cel.group(1)) if cel else '',
                tasks=tasks, equip=equip, plan=plan, talk=slides[:4], progs=progs, glossary=gl, trouble=trouble,
                warmup=clean(warm.group(1)) if warm else '', elec_list=elec)

if __name__ == '__main__':
    d = sys.argv[1]
    lst = [l.rstrip('\n').split('\t') for l in open(os.path.join(d, 'list.tsv')) if l.strip()]
    res = []
    for n, slug, name, *_ in lst:
        f = glob.glob(os.path.join(d, 'md', f'{n}-*.md'))[0]
        r = parse(open(f).read()); r.update(n=int(n), slug=slug, name=name)
        e = r.pop('elec_list'); r['elec'] = '' if len(e) == 1 else ', '.join(e[:-1]) + ' и ' + e[-1]
        res.append(r)
    json.dump(res, open(os.path.join(d, 'lessons.json'), 'w'), ensure_ascii=False, indent=1)
    for r in res:
        print(r['n'], r['name'], '|', r['topic'][:35], '|', r['tagline'][:35], '|', r['age'], '|elec', r['elec'], '|goal', len(r['goal']), '|tasks', len(r['tasks']),
              '|eq', len(r['equip']), '|plan', len(r['plan']), '|talk', [t for t, _ in r['talk']], '|progs', [t[:25] for t, _ in r['progs']], '|gl', len(r['glossary']), '|tr', len(r['trouble']), '|warm', len(r['warmup']))
