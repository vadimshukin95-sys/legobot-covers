# -*- coding: utf-8 -*-
"""Учебная программа WeDo 2.0, часть 3: КТП + текст презентаций, шаблон H.
python3 parse_h.py <course_dir>  (ktp.json, txt/NN.json, names.tsv)"""
import re, json, sys, os, glob

STOP = ('соберем', 'соберём', 'подключите', 'алгоритм', 'дополнительное задание', 'а что будет', 'поздравляю', 'что мы узнаем', 'построим')
MECH = re.compile(r'передач|датчик|рычаг|шестер|шкив|\bремен|зубчат|\bблок|\bмотор|смарт')

def norm(s):
    s = s.replace('\x0b', ' ').replace('\u000b', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()

def sents(s, n=1, maxlen=260):
    s = re.sub(r'\s*\n+\s*', ' ', s)
    s = re.sub(r'(^|\s)\d+\.\s+', r'\1', s).strip()
    s = re.sub(r'\b([А-ЯЁA-Z])\.\s', r'\1§ ', s)                 # инициалы «Г. Н.»
    s = re.sub(r'\b(т|др|пр|гг|г|см|им|ул)\.\s', r'\1§ ', s)
    parts = [p.strip().replace('§', '.') for p in re.findall(r'.+?[.!?…](?:»)?(?=\s|$)', s)] or [s.replace('§', '.')]
    parts = [p for p in parts if not re.search(r'\s(и|а|но|или|с|в|на)\.$', p)] or parts
    out = parts[0]
    for p in parts[1:n]:
        if len(out) + len(p) < maxlen: out += ' ' + p
    if not re.search(r'[.!?…»]$', out): out += '.'
    return out

FIX = [('делателей', 'деталей'), ('Набор состоит из: ящика с деталями, смарт хаб, мотор, датчик движения и датчик наклона.', 'В наборе: ящик с деталями, смартхаб, мотор, датчик движения и датчик наклона.'), ('вилы крокодилов', 'виды крокодилов'), ('факту о', 'факты о'), ('космический роботов', 'космических роботов'),
       ('звездного война', 'звёздного воина'), ('автоматический ворот', 'автоматических ворот'), ('подъемный кранов', 'подъёмных кранов'),
       ('История создании', 'История создания'), ('что бы', 'чтобы'), ('находиться на космодроме', 'находится на космодроме'),
       ('коронарн', 'коронн'), ('о автомобили', 'об автомобилях'), ('День рождение', 'День рождения'), ('автоматический рук', 'автоматических рук'),
       ('Историю гоночных', 'История гоночных'), ('и что где она', 'и где она'), ('на сколько', 'насколько')]

def fix(s):
    s = re.sub(r'"([^"]+)"', r'«\1»', s)
    s = re.sub(r'(?<!\.)\.\.(?!\.)', '.', s)
    s = re.sub(r'(?<=[а-яё])—(?=[а-яё])', ' — ', s); s = re.sub(r'(?<=\s)—(?=[а-яё])', '— ', s)
    s = s.replace('АРТРОПЛЕРВА', 'Артроплевра').replace('ртроплерва', 'ртроплевра').replace('  ', ' ')
    s = re.sub(r'(^|\s)оберем', r'\1Соберём', s)
    for a, b in FIX[1:] if FIX[0][0] == 'оберем' else FIX:
        s = s.replace(a, b)
    s = s.replace('Соберем', 'Соберём').replace('соберем', 'соберём').replace('Проведем', 'Проведём')
    return s

TFIX = {'Значение Опыление пчёлами': 'Значение опыления пчёлами', 'Первая Карусель в россии': 'Первая карусель в России',
        'Современные танк россии Т-14 "Армата"': 'Современный танк России Т-14 «Армата»', 'Интересные факты об автомобилях тесла': 'Интересные факты об автомобилях Tesla',
        'От куда мы узнали о мегалодоне': 'Откуда мы узнали о мегалодоне', 'Автомобили с поворотом колес на 90 гр': 'Автомобили с поворотом колёс на 90°',
        'Что такое Сила тяги': 'Что такое сила тяги', 'История становления профессии повар': 'История профессии повара', 'Машина тягач': 'Машина-тягач',
        'Набор Lego wedo 2.0': 'Набор LEGO WeDo 2.0', 'Виды спутников:': 'Виды спутников', 'Интересные факты о улитках': 'Интересные факты об улитках',
        'Самые красивые улитки Хрустальная улитка': 'Хрустальная улитка', 'кто такой шпион': 'Кто такой шпион', 'основные элементы ременной передачи': 'Основные элементы ременной передачи',
        'Какая передача подойдет для БТР': 'Какая передача подойдёт для БТР'}

def ktp_list(c):
    parts = re.split(r'\n(?=\s*\d+\.)', c.strip())
    items = [re.sub(r'^\d+\.\s*', '', re.sub(r'\s*\n\s*', ' ', x)).strip(' .') for x in parts if x.strip()]
    items = [fix(x[:1].upper() + x[1:]) for x in items if len(x) > 3]
    return items

def summ(body):
    raw = [l.strip() for l in body.split('\n') if l.strip()]
    lines = []
    for l in raw:
        if lines and re.match(r'[a-zа-яё(]', l) and not lines[-1].endswith(':'): lines[-1] += ' ' + l
        else: lines.append(l)
    short = [l for l in lines if len(l) < 60 and not re.search(r'[.!?]$', l)]
    head0 = 1 if lines and lines[0].endswith(':') else 0
    if len(lines) >= 3 and len(short) >= len(lines) - head0 and all(len(l) < 60 for l in lines[head0:]):
        head = lines[0] if lines[0].endswith(':') else ''
        items = [re.sub(r'^[-–—•\d.\s]+', '', l).rstrip(' ,;') for l in (lines[1:] if head else lines)]
        items = [i[:1].lower() + i[1:] if not re.match(r'[А-ЯA-Z]{2}', i) else i for i in items if i]
        txt_ = ', '.join(items[:6])
        return (head + ' ' + txt_ + '.') if head else (txt_[:1].upper() + txt_[1:] + '.')
    segs, i = [], 0
    while i < len(lines):
        l = re.sub(r'^[-–—•]\s*', '', lines[i])
        if l.endswith(':'):
            j = i + 1; items = []
            while j < len(lines) and len(lines[j]) < 70:
                it = re.sub(r'^[-–—•\d.\s]+', '', lines[j]).rstrip(' .,;')
                if it: items.append(it[:1].lower() + it[1:] if not re.match(r'[А-ЯA-Z]{2}', it) else it)
                j += 1
            if items:
                segs.append(l + ' ' + ', '.join(items[:6]) + '.'); i = j; continue
        if len(l) < 30 and not re.search(r'[.!?:;,]$', l) and i + 1 < len(lines) and len(lines[i + 1]) > len(l):
            i += 1; continue                     # подзаголовок внутри текста
        segs.append(l if re.search(r'([.!?:;,]|[.!?]»)$', l) else l + '.')
        i += 1
    joined = ' '.join(segs)
    joined = joined[:1].upper() + joined[1:]
    return sents(joined, 2, 300)

def slide_parts(x):
    t = [norm(s) for s in x['text'] if norm(s)]
    if not t: return None, ''
    if len(t) == 1:
        return (t[0], '') if len(t[0]) < 80 else (None, t[0])
    title = next((s for s in t if len(s) < 70 and '\n' not in s and not s.endswith('.') and (s.endswith('?') or not re.search(r'[.!]\s', s))), None)
    body = '\n'.join(s for s in t if s is not title and len(s) > 25)
    return title, body

def parse(n, S, K):
    talk, mech, blocks = [], [], []
    for x in S[2:]:
        title, body = slide_parts(x)
        lt = (title or '').lower()
        if any(lt.startswith(s) for s in STOP) or 'алгоритм' in lt or not body: continue
        if re.search(r'на рисунке|на картинке|Вопросы для проверки|вести огонь|огонь из', body): continue
        if 'мы узнаем' in lt: continue
        b = fix(summ(body))
        t = fix(title.rstrip('?').strip()) if title else ''
        if t and t.upper() == t and len(t) > 12: t = t.lower()
        t = re.sub(r'\bроссии\b', 'России', t).replace('Артроплерва', 'Артроплевра').replace('"Армата"', '«Армата»').replace('Современные танк', 'Современный танк')
        t = TFIX.get(t, t[:1].upper() + t[1:])
        if lt.startswith('блок') or 'новые блоки' in lt or 'запрограммировать' in lt:
            blocks.append((t, b))
        elif MECH.search(lt if lt else body[:30].lower()):
            mech.append((t, b))
        else:
            talk.append((t, b))
    # убрать повторяющиеся заголовки («Интересные факты…» ×2)
    def dedup(lst, k):
        seen, out = set(), []
        for t, b in lst:
            if t and t in seen: continue
            seen.add(t); out.append((t, b))
        return out[:k]
    return dict(plan=ktp_list(K['content']), talk=dedup(talk, 4), mech_items=dedup(mech, 3), blocks=dedup(blocks, 2))

MECHN = {'угловая коронарная': 'угловая коронная зубчатая передача', 'повышающая': 'повышающая зубчатая передача', 'понижающая': 'понижающая зубчатая передача',
         'промежуточная (холостая)': 'промежуточная (холостая) зубчатая передача', 'многоступенчатая зубчатая': 'многоступенчатая зубчатая передача',
         'двойная ременная': 'двойная ременная передача', 'повышающая ременная': 'повышающая ременная передача', 'механизм рычаг': 'рычаг',
         'датчик движения/угловая коронная зубчатая передача': 'датчик движения и угловая коронная зубчатая передача', 'датчик движения/рычаг': 'датчик движения и рычаг',
         'датчик наклона самостоятельное программирование': 'датчик наклона, самостоятельное программирование',
         'датчик движения самостоят программирование': 'датчик движения, самостоятельное программирование',
         'зубчатая и червячная': 'зубчатая и червячная передачи', 'угловая зубчатая и многоступенчатая зубчатая': 'угловая и многоступенчатая зубчатые передачи',
         'угловая, многоступенчатая': 'угловая и многоступенчатая зубчатые передачи', 'ременная и угловая зубчатая': 'ременная и угловая зубчатая передачи',
         'ременная и червячная': 'ременная и червячная передачи', 'зубчатая, рычаг': 'зубчатая передача и рычаг', 'червячная, реечная': 'червячная и реечная передачи',
         'двойная угловая': 'двойная угловая зубчатая передача', 'ременная, зубчатая, реечная': 'ременная, зубчатая и реечная передачи',
         'угловая зубчатая, ременная и зубчатая': 'угловая зубчатая, ременная и зубчатая передачи', 'червячная, зубчатая и угловая зубчатая': 'червячная, зубчатая и угловая зубчатая передачи',
         'ременная и зубчатая': 'ременная и зубчатая передачи', 'зубчатая и рычаг': 'зубчатая передача и рычаг', 'новый блок голос': 'новый блок «Голос»',
         'блок сообщение': 'блоки «Отправить сообщение» и «Получить сообщение»', 'датчик наклона, рычаг': 'датчик наклона и рычаг',
         'угловая зубчатая передача\nблок сообщение\nдатчик движения': 'угловая зубчатая передача, блок «Сообщение», датчик движения',
         'блок ожидания, датчик движения': 'блок ожидания и датчик движения', 'два мотора и два смарт хаба': 'два мотора и два смартхаба',
         'датчик движения, клавиша': 'датчик движения и блок «Клавиша»', 'смартхаб': 'смартхаб', '': ''}

if __name__ == '__main__':
    d = sys.argv[1]
    K = {x['n']: x for x in json.load(open(os.path.join(d, 'ktp.json')))}
    names = [l.rstrip('\n').split('\t') for l in open(os.path.join(d, 'names.tsv')) if l.strip()]
    res = []
    for n, slug, name in names:
        n = int(n); S = json.load(open(os.path.join(d, 'txt', f'{n:02d}.json')))
        k = K[n]
        r = parse(n, S, k)
        m = k['mech'].strip()
        r.update(n=n, slug=slug, name=name, section=k['section'][:1].upper() + k['section'][1:], mech=MECHN.get(m, m), control=k['control'],
                 age='8–12 лет', minutes=45, slides=len(S))
        res.append(r)
    json.dump(res, open(os.path.join(d, 'lessons.json'), 'w'), ensure_ascii=False, indent=1)
    for r in res:
        print(r['n'], r['name'], '|', r['section'], '|', r['mech'], '|plan', len(r['plan']), '|talk', [t for t, _ in r['talk']], '|mech', [t for t, _ in r['mech_items']], '|bl', [t for t, _ in r['blocks']])
