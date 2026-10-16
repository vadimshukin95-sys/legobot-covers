# -*- coding: utf-8 -*-
"""Конспекты уроков для Потока «Уроки робототехники» (legobot.ru/uroki).
python3 build_uroki.py <lessons.json> <course.json> <imgmap.json> <out.csv>"""
import json, csv, io, html, re, sys

L = json.load(open(sys.argv[1]))
C = json.load(open(sys.argv[2]))
IM = json.load(open(sys.argv[3])) if sys.argv[3] != '-' else {}
e = html.escape

def txt(x): return f'<div class="t-redactor__text">{x}</div>'
def h2(x): return f'<h2 class="t-redactor__h2">{e(x)}</h2>'
def ul(items): return txt('<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>')
def ol(items): return txt('<ol>' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>')
def pl(n, f):
    a, b = n % 10, n % 100
    return f[0] if a == 1 and b != 11 else f[1] if 2 <= a <= 4 and not 12 <= b <= 14 else f[2]

def alias(l): return f"urok-{l['slug']}-{C['alias_suffix']}"
def url(l): return f"/uroki/{alias(l)}"

rows = []
total = len(L)
for l in L:
    name = l['name']; n = l['n']
    theme = re.sub(r'^\s*(Узнаем|Узнают|Поймут|Поймём)\s*,\s*', '', l['learn'][0]).rstrip('.')
    h1 = f"Урок «{name}» по {C['platform']}"
    seo_title = f"Урок «{name}» {C['platform_short']} — конспект на {l['minutes']} минут | LEGObot"
    seo_descr = (f"Конспект занятия «{name}» для {C['platform']}, {l['age']}: чему научатся дети, "
                 f"план урока на {l['minutes']} минут, вопросы с ответами и частые трудности.")
    short = f"Занятие {n} из {total}: {theme}. Модель — {l['steps']} {pl(l['steps'], ['шаг','шага','шагов'])} сборки."
    facts = '<br>'.join([
        f"<strong>Курс:</strong> {e(C['course_short'])}, занятие {n} из {total}",
        f"<strong>Возраст:</strong> {e(l['age'])}",
        f"<strong>Длительность:</strong> {l['minutes']} минут",
        f"<strong>Набор:</strong> {e(C['kit'])}",
        f"<strong>Модель:</strong> {e(name)}, {l['steps']} {pl(l['steps'], ['шаг','шага','шагов'])} сборки",
        f"<strong>Электроника:</strong> {e(l['elec'])}"])
    note = (f"Это сокращённый конспект. Полная методичка с поминутным ходом урока, вопросами к каждому слайду "
            f"и разбором программы, презентация и инструкция по сборке — в курсе «<a href=\"{C['url']}\">{e(C['course_short'])}</a>» "
            f"({total} занятий). ")
    if C.get('free_url') and n == 1:
        note += (f"А это занятие можно скачать целиком бесплатно: <a href=\"{C['free_url']}\">методичка, презентация и инструкция</a>.")
    elif C.get('free_url'):
        note += (f"Первое занятие курса можно скачать бесплатно: <a href=\"{C['free_url']}\">методичка, презентация и инструкция</a>.")
    body = [txt(facts), txt(note)]
    body += [h2('Чему научатся дети'), ul([e(re.sub(r'^Узнаем', 'Узнают', x).rstrip('.')) for x in l['learn']])]
    need = []
    for r in l['need']:
        what, qty = r[0], r[1]
        if what.startswith('Файл'):
            need.append('Презентация занятия на проекторе (входит в курс)')
        else:
            need.append(e(what) + (f' — {e(qty)}' if qty and qty != '—' else ''))
    body += [h2('Что понадобится'), ul(need)]
    plan = []
    for r in l['plan']:
        stage = re.sub(r'^\d+\.\s*', '', r[0])
        plan.append(f"{e(stage)} — {e(r[1])}")
    body += [h2(f"План занятия на {l['minutes']} минут"), ol(plan)]
    th = [f"<strong>{e(re.sub(r'^[0-9]+[.] *', '', r[0]))}.</strong> {e(r[1])}" for r in l['theory']]
    body += [h2('О чём поговорить на теории'), ul(th)]
    qa = [l['qa'][i] for i in (0, 1, 3) if i < len(l['qa'])]
    body += [h2('Вопросы на повторение')]
    body += [txt(f"<strong>{e(q)}</strong><br>{e(a)}") for q, a in qa]
    tr = l['trouble'][2:5] if len(l['trouble']) >= 5 else l['trouble'][:3]
    body += [h2('Частые трудности'), ul([f"<strong>{e(r[0])}.</strong> {e(r[1])} — {e(r[2][0].lower() + r[2][1:])}." for r in tr])]
    body += [h2('Если осталось время'), ul([e(x.rstrip('.')) for x in l['extra']])]
    kit = [f"Методичка для педагога (DOCX): поминутный ход урока, вопросы к слайдам с ответами, разбор блоков программы, частые трудности, словарик",
           f"Презентация занятия (PPTX и PDF)",
           f"Инструкция по сборке модели «{e(name)}» (PDF), {l['steps']} {pl(l['steps'], ['шаг','шага','шагов'])}",
           f"Обложка модели (PNG)"]
    others = ', '.join(f"<a href=\"{url(o)}\">{e(o['name'])}</a>" for o in L if o['n'] != n)
    body += [h2('Что в полном комплекте'), ul(kit),
             txt(f"Другие занятия курса: {others}. Все {total} занятий — в курсе «<a href=\"{C['url']}\">{e(C['course_short'])}</a>».")]
    cover = IM.get(f"{l['slug']}.jpg", '')
    rows.append({'Alias': alias(l), 'Title': h1, 'Category': C['category'], 'Media Type': 'image', 'Media': cover,
                 'Description': short, 'Text': ''.join(body),
                 'Date': f"2026-10-16 07:{59 - n:02d}:00+03:00", 'Visibility': 'draft', 'Thumb Image': cover,
                 'SEO Title': seo_title, 'SEO Description': seo_descr,
                 'Social Title': seo_title, 'Social Description': seo_descr, 'Social Image': cover})
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=list(rows[0]), delimiter=';', quoting=csv.QUOTE_ALL, lineterminator='\n')
w.writeheader(); w.writerows(rows)
open(sys.argv[4], 'w', encoding='utf-8').write(buf.getvalue())
for r in rows:
    print(len(r['SEO Title']), len(r['SEO Description']), len(r['Text']), r['Alias'], '|', r['Description'])
