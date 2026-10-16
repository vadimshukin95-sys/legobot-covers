# -*- coding: utf-8 -*-
"""Конспекты уроков для Потока «Уроки робототехники» (legobot.ru/uroki), шаблоны A/B/C.
python3 build2.py <course_dir> [imgmap.json]  -> <course_dir>/uroki.csv"""
import json, csv, io, html, re, sys, os

D = sys.argv[1]
L = json.load(open(os.path.join(D, 'lessons.json')))
C = json.load(open(os.path.join(D, 'course.json')))
IM = json.load(open(sys.argv[2])) if len(sys.argv) > 2 and os.path.exists(sys.argv[2]) else {}
T = C['template']
e = html.escape

def txt(x): return f'<div class="t-redactor__text">{x}</div>'
def h2(x): return f'<h2 class="t-redactor__h2">{e(x)}</h2>'
def ul(items): return txt('<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>')
def ol(items): return txt('<ol>' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>')
def pl(n, f):
    a, b = n % 10, n % 100
    return f[0] if a == 1 and b != 11 else f[1] if 2 <= a <= 4 and not 12 <= b <= 14 else f[2]
def shagov(n): return f"{n} {pl(n, ['шаг', 'шага', 'шагов'])}"
def lcfirst(s): return s[:1].lower() + s[1:] if s else s
def nodot(s): return s.rstrip(' .')
def dot(s): s = nodot(s); return s if s[-1:] in '!?…' else s + '.'
def alias(l): return f"urok-{l['slug']}-{C['alias_suffix']}"
def url(l): return f"/uroki/{alias(l)}"

total = len(L)
CL = f"<a href=\"{C['url']}\">{e(C['course_short'])}</a>"
zan = f"{total} {pl(total, ['занятие', 'занятия', 'занятий'])}"

def note(l):
    s = (f"Это сокращённый конспект. {C['full_what']} — в курсе «{CL}» ({zan}). ")
    if C.get('free_url') and l['n'] == 1:
        s += f"А это занятие можно скачать целиком бесплатно: <a href=\"{C['free_url']}\">{C['free_what']}</a>."
    elif C.get('free_url'):
        s += f"Первое занятие курса можно скачать бесплатно: <a href=\"{C['free_url']}\">{C['free_what']}</a>."
    elif C.get('free_other_url'):
        s += f"Попробовать формат бесплатно можно на <a href=\"{C['free_other_url']}\">{C['free_other_text']}</a>."
    return s

def facts(l):
    rows = [f"<strong>Курс:</strong> {e(C['course_short'])}, занятие {l['n']} из {total}",
            f"<strong>Возраст:</strong> {e(l['age'])}",
            f"<strong>Длительность:</strong> " + ('два занятия по 45 минут' if l.get('double') else f"{l['minutes']} минут"),
            f"<strong>Набор:</strong> {e(C['kit'])}"]
    if C.get('env'): rows.append(f"<strong>Среда программирования:</strong> {C['env']}")
    if l.get('steps') or T != 'D':
        rows.append(f"<strong>Модель:</strong> {e(l.get('model', l['name']))}" + (f", {shagov(l['steps'])} сборки" if l.get('steps') else ''))
    if l.get('author'): rows.append(f"<strong>Автор модели:</strong> {e(l['author'])}")
    if l.get('elec'): rows.append(f"<strong>Электроника:</strong> {e(l['elec'])}")
    if 'motor' in l and l.get('steps'): rows.append("<strong>Мотор:</strong> " + ('нужен, с батарейками' if l['motor'] else 'не нужен'))
    return txt('<br>'.join(rows))

def kit_block(l):
    sw = f"{l['slides']} {pl(l['slides'], ['слайд', 'слайда', 'слайдов'])}" if l.get('slides') else ''
    items = [x.replace('{model}', '{{model}}').format(name=e(l['name']), steps=shagov(l['steps']) if l.get('steps') else '', slides=sw)
             for x in C['kit_list'] if not (('{steps}' in x or '{model}' in x) and not l.get('steps'))]
    items = [x.replace('{model}', '') for x in items]
    items = [re.sub(r',\s*$', '', x) for x in items]
    others = ', '.join(f"<a href=\"{url(o)}\">{e(o['name'])}</a>" for o in L if o['n'] != l['n'])
    return [h2('Что в полном комплекте'), ul(items),
            txt(f"Другие занятия курса: {others}. Все {zan} — в курсе «{CL}».")]

def body_A(l):
    b = []
    b += [h2('Чему научатся дети'), ul([e(nodot(re.sub(r'^Узнаем', 'Узнают', x))) for x in l['learn']])]
    need = []
    for r in l['need']:
        what, qty = r[0], r[1]
        if what.startswith('Файл'): need.append('Презентация занятия на проекторе (входит в курс)')
        else: need.append(e(what) + (f' — {e(qty)}' if qty and qty != '—' else ''))
    b += [h2('Что понадобится'), ul(need)]
    b += [h2(f"План занятия на {l['minutes']} минут"), ol([f"{e(re.sub(r'^\d+\.\s*', '', r[0]))} — {e(r[1])}" for r in l['plan']])]
    b += [h2('О чём поговорить на теории'), ul([f"<strong>{e(re.sub(r'^[0-9]+[.] *', '', r[0]))}.</strong> {e(r[1])}" for r in l['theory']])]
    b += [h2('Вопросы на повторение')] + [txt(f"<strong>{e(q)}</strong><br>{e(a)}") for q, a in [l['qa'][i] for i in (0, 1, 3) if i < len(l['qa'])]]
    tr = l['trouble'][2:5] if len(l['trouble']) >= 5 else l['trouble'][:3]
    b += [h2('Частые трудности'), ul([f"<strong>{e(r[0])}.</strong> {e(r[1])} — {e(lcfirst(r[2]))}." for r in tr])]
    b += [h2('Если осталось время'), ul([e(nodot(x)) for x in l['extra']])]
    return b

def body_B(l):
    b = [h2('Цель занятия'), txt(e(l['goal']))]
    b += [h2('Что понадобится'), ul([e(nodot(x)) for x in l['need']])]
    plan = []
    for r in l['plan']:
        m = re.match(r'(\d+)\s*[–-]\s*(\d+)', r[0]); mn = int(m.group(2)) - int(m.group(1)) if m else None
        plan.append(f"<strong>{e(r[1])}{', ' + str(mn) + ' мин' if mn else ''}.</strong> {e(nodot(r[2]))}")
    b += [h2(f"План занятия на {l['minutes']} минут"), ol(plan)]
    b += [h2('О чём поговорить на теории'), ul([f"<strong>{e(t)}.</strong> {e(' '.join(dot(x) for x in bl[:2]))}" for t, bl in l['theory']])]
    if l.get('exp') and l['exp'][1]:
        t, bl = l['exp']
        items = []
        for x in bl:
            m = re.match(r'^([А-ЯЁ][а-яё]+):\s*(.*)', x)
            items.append(f"<strong>{e(m.group(1))}:</strong> {e(lcfirst(nodot(m.group(2))))}" if m else e(nodot(x)))
        b += [h2(t), ul(items)]
    if l.get('scripts'):
        n = len(l['scripts'])
        b += [h2('Программа'), txt(f"В программе {n} {pl(n, ['скрипт', 'скрипта', 'скриптов'])}, каждый запускается от своего события: "
                                     + ', '.join(e(s) for s in l['scripts']) + ". Блоки со значениями и готовый проект для приложения "
                                     "LEGO Education SPIKE — в полной методичке.")]
    b += [h2('Вопросы на повторение')] + [txt(f"<strong>{e(q)}</strong><br>{e(a)}") for q, a in [l['qa'][i] for i in (0, 1, 3) if i < len(l['qa'])]]
    b += [h2('Частые трудности'), ul([e(nodot(x)) for x in l['trouble'][:3]])]
    if l.get('tasks'):
        b += [h2('Задания на доработку'), ul([f"<strong>{e(t)}.</strong> {e(nodot(s))}" for t, s in l['tasks']])]
    return b

def body_C(l):
    b = [h2('Идея занятия')] + [txt(e(p)) for p in l['idea'][:2]]
    b += [h2('Чему научатся дети'), ul([e(nodot(x)) for x in l['learn']])]
    plan = []
    for r in l['plan']:
        m = re.match(r'(\d+)\s*[–-]\s*(\d+)', r[0]); mn = int(m.group(2)) - int(m.group(1)) if m else None
        plan.append(f"<strong>{e(r[1])}{', ' + str(mn) + ' мин' if mn else ''}.</strong> {e(nodot(r[2]))}")
    b += [h2(f"Ход занятия на {l['minutes']} минут"), ol(plan)]
    if l.get('tasks'):
        b += [h2('Программы'), ul([e(nodot(re.sub(r'^Задание (\d+)\.\s*', r'Задание \1: ', t))) for t in l['tasks']]),
              txt("Программы собираются из блоков в <a href=\"/app\">онлайн-среде WeDo</a> прямо в браузере — "
                  "без установки приложения.")]
    if l.get('game'):
        b += [h2('Игра в конце урока'), txt(e(l['game'][0]))]
    b += [h2('Вопросы детям')] + [txt(f"<strong>{e(q)}</strong><br>{e(a)}") for q, a in l['qa'][:3]]
    tr = l['trouble'][1:4] if len(l['trouble']) >= 4 else l['trouble'][:3]
    b += [h2('Что может пойти не так'), ul([f"<strong>{e(r[0])}.</strong> {e(r[1])} — {e(lcfirst(nodot(r[2])))}." for r in tr])]
    return b


def clean_equip(x):
    x = re.sub(r'\s*[«"]?[\w\-]+\.(pdf|pptx|docx)[»"]?', '', x)
    x = re.sub(r'Презентация «[^»]*»', 'Презентация занятия', x)
    return nodot(re.sub(r'\s+', ' ', x).replace(' ,', ','))

def body_D(l):
    b = []
    if l.get('box'):
        names = {'Понятие': 'Понятия', 'Правило': 'Правило', 'Навык': 'Навык'}
        b += [h2('Главное на занятии'), ul([f"<strong>{names[k]}:</strong> {e(nodot(v))}" for k, v in l['box'].items()])]
    if l.get('goal'):
        b += [h2('Цель занятия'), txt(e(l['goal'][:1].upper() + l['goal'][1:]))]
    if l.get('tasks'):
        b += [h2('Задачи занятия'), ul([e(nodot(x[:1].upper() + x[1:])) for x in l['tasks'][:6]])]
    if l.get('equip'):
        b += [h2('Что понадобится'), ul([e(clean_equip(x)) for x in l['equip']])]
    if l.get('plan'):
        def stage(x): return re.sub(r'^(Часть \d\. )?\d+\.\s*', lambda m: m.group(1) or '', x)
        plan = [f"<strong>{e(stage(r[0]))}, {e(r[1])}.</strong> {e(nodot(r[2]))}" for r in l['plan']]
        b += [h2('План занятия' + (' (два урока по 45 минут)' if l.get('double') else ' на 45 минут')), ol(plan)]
    if l.get('trials'):
        b += [h2('Испытания'), ul([f"<strong>{e(t)}.</strong> " + (f"Что проверяем: {e(lcfirst(nodot(w)))}." if w else '') for t, w in l['trials']])]
    if l.get('stages'):
        b += [h2('Как проходит финал'), ul([f"<strong>{e(t)}.</strong> {e(nodot(w))}." for t, w in l['stages']])]
    if l.get('glossary'):
        b += [h2('Словарь занятия'), ul([f"<strong>{e(r[0])}</strong> — {e(lcfirst(nodot(r[1])))}" for r in l['glossary']])]
    if l.get('trouble'):
        b += [h2('Частые трудности'), ul([f"<strong>{e(nodot(r[0]))}.</strong> {e(nodot(r[1]))}." if r[1] else e(nodot(r[0])) for r in l['trouble'][:3]])]
    return b

def clean_files(x):
    x = re.sub(r'\s*[«"][^»"]*?(_|\.(pdf|pptx|docx))[^»"]*[»"]', '', x)
    return nodot(re.sub(r'\s+', ' ', x).replace(' ,', ',').replace(' —', ' —').rstrip(' ;'))

def body_E(l):
    b = [h2('Тема урока'), txt(f"<strong>{e(l['topic'])}.</strong> {e(dot(l['tagline']))}")]
    if l.get('goal'): b += [h2('Цель урока'), txt(e(l['goal'][:1].upper() + l['goal'][1:]))]
    if l.get('tasks'): b += [h2('Задачи урока'), ul([e(nodot(x[:1].upper() + x[1:]).rstrip(';')) for x in l['tasks']])]
    if l.get('equip'): b += [h2('Что понадобится'), ul([e(clean_files(x)) for x in l['equip']])]
    if l.get('plan'):
        def stage(x): return re.sub(r'^\d+\.\s*', '', x)
        b += [h2('План урока на 45 минут'), ol([f"<strong>{e(stage(r[0]))}, {e(r[1])}.</strong> {e(nodot(first_sent(r[2], 1 if len(first_sent(r[2])) > 40 else 2)))}" for r in l['plan']])]
    if l.get('talk'):
        b += [h2('О чём рассказать детям'), ul([f"<strong>{e(dot(t))}</strong> {e(first_sent(sv.replace('«', '').replace('»', ''), 2))}" for t, sv in l['talk']])]
    if l.get('progs'):
        b += [h2('Программы'), ul([f"<strong>{e(nodot(t))}.</strong> " + ((e(dot(g)) if g.startswith('Идея:') else f"Цель: {e(lcfirst(nodot(g)))}.") if g else '') for t, g in l['progs']])]
    if l.get('glossary'): b += [h2('Словарь урока'), ul([f"<strong>{e(r[0])}</strong> — {e(lcfirst(nodot(r[1])))}" for r in l['glossary']])]
    if l.get('trouble'): b += [h2('Частые трудности'), ul([f"<strong>{e(nodot(r[0]))}.</strong> {e(nodot(r[1]))}." for r in l['trouble'][:3]])]
    return b

def first_sent(s, n=1):
    parts = [p.strip() for p in re.findall(r'.+?[.!?…](?:»)?(?=\s|$)', s)]
    return ' '.join(parts[:n]) if parts else s

def short_desc(l):
    if T == 'A':
        th = nodot(re.sub(r'^\s*(Узнаем|Узнают|Поймут|Поймём)\s*,\s*', '', l['learn'][0]))
        s = f"Занятие {l['n']} из {total}: {th}."
    elif T == 'B':
        g = re.split(r',? и (научить|познакомить)', l['goal'])[0]
        g = re.sub(r'^Показать', 'покажем', g); g = re.sub(r'^Рассказать', 'расскажем', g); g = re.sub(r'^Познакомить', 'познакомим', g)
        s = f"Занятие {l['n']} из {total}: {nodot(g)}."
    elif T == 'E':
        s = f"Занятие {l['n']} из {total}. {l['topic']}: {dot(lcfirst(l['tagline']))}"
    elif T == 'D':
        s = f"Занятие {l['n']} из {total}. {dot(l['subtitle'])}"
    else:
        s = f"Занятие {l['n']} из {total}: {dot(l['tagline'])}"
    if l.get('steps'): s += f" Модель — {shagov(l['steps'])} сборки."
    return s

rows = []
for l in L:
    name = l['name']
    h1 = C.get('h1_tpl', 'Урок «{name}» по {platform}').format(name=name, platform=C['platform'], topic=lcfirst(l.get('topic', '')))
    seo_title = C.get('seo_title_tpl', 'Урок «{name}» {platform_short} — конспект на {minutes} минут | LEGObot').format(name=name, platform_short=C['platform_short'], minutes=l['minutes'])
    seo_descr = C['seo_descr'].format(name=name, platform=C['platform'], age=l['age'], minutes=l['minutes'])
    body = [facts(l), txt(note(l))] + {'A': body_A, 'B': body_B, 'C': body_C, 'D': body_D, 'E': body_E}[T](l) + kit_block(l)
    cover = IM.get(f"{l['slug']}.jpg", '')
    rows.append({'Alias': alias(l), 'Title': h1, 'Category': C['category'], 'Media Type': 'image', 'Media': cover,
                 'Description': short_desc(l), 'Text': ''.join(body),
                 'Date': f"2026-10-16 {C['date_hour']:02d}:{59 - l['n']:02d}:00+03:00", 'Visibility': 'draft', 'Thumb Image': cover,
                 'SEO Title': seo_title, 'SEO Description': seo_descr,
                 'Social Title': seo_title, 'Social Description': seo_descr, 'Social Image': cover})
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=list(rows[0]), delimiter=';', quoting=csv.QUOTE_ALL, lineterminator='\n')
w.writeheader(); w.writerows(rows)
open(os.path.join(D, 'uroki.csv'), 'w', encoding='utf-8').write(buf.getvalue())
json.dump(rows, open(os.path.join(D, 'rows.json'), 'w'), ensure_ascii=False, indent=1)
for r in rows:
    print(len(r['SEO Title']), len(r['SEO Description']), len(r['Text']), r['Alias'], '|', r['Description'])
