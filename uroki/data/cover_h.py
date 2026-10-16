# -*- coding: utf-8 -*-
"""Обложки 1200×900 для «Учебная программа WeDo 2.0, часть 3»: цвет = раздел, крупный номер занятия."""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont
F = '/tmp/claude-0/-home-claude/2afa7230-c35c-5a49-9141-7328e6d042e2/scratchpad/fonts/Nunito-{}.ttf'
font = lambda w, s: ImageFont.truetype(F.format(w), s)
COL = {'Первые шаги': '#2e7d32', 'Проекты с пошаговыми инструкциями': '#00796b', 'Знакомство с передачами и механизмами': '#1565c0',
       'Виды зубчатой передачи': '#6a1b9a', 'Виды ременной передачи': '#ad1457', 'Датчики': '#c62828', 'Рычаг': '#d84315',
       'Двойные передачи': '#283593', 'Тройные передачи': '#4e342e', 'Командная сборка': '#00838f', 'Программирование': '#37474f'}
W, H = 1200, 900

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def make(l, out):
    c = COL.get(l['section'], '#37474f')
    base = Image.new('RGBA', (W, H), c)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    num = str(l['n']); fn = font(900, 620)
    bb = od.textbbox((0, 0), num, font=fn)
    od.text((W - (bb[2] - bb[0]) - 40 - bb[0], H - (bb[3] - bb[1]) - 60 - bb[1]), num, font=fn, fill=(255, 255, 255, 34))
    im = Image.alpha_composite(base, ov)
    ov2 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov2)
    x = 80
    d.text((x, 80), f"Занятие {l['n']} из 70", font=font(800, 44), fill=(255, 255, 255, 235))
    # название
    for size in (120, 104, 92, 80):
        fname = font(900, size); lines = wrap(d, l['name'], fname, W - 2 * x)
        if len(lines) <= 2: break
    y = 250
    for ln in lines:
        d.text((x, y), ln, font=fname, fill='white'); y += int(size * 1.08)
    # механизм
    if l.get('mech'):
        fm = font(700, 46); y += 18
        for ln in wrap(d, l['mech'][:1].upper() + l['mech'][1:], fm, W - 2 * x)[:2]:
            d.text((x, y), ln, font=fm, fill=(255, 255, 255, 220)); y += 58
    # раздел — плашка внизу
    fs = font(800, 36); t = l['section']
    tw = d.textlength(t, font=fs)
    d.rounded_rectangle((x, H - 140, x + tw + 56, H - 76), radius=32, fill='white')
    d.text((x + 28, H - 136), t, font=fs, fill=c)
    d.text((x, H - 60), 'LEGO WeDo 2.0 · учебная программа, часть 3', font=font(700, 26), fill=(255, 255, 255, 170))
    im = Image.alpha_composite(im, ov2).convert('RGB')
    im.save(out, quality=90)

if __name__ == '__main__':
    d = sys.argv[1]
    for l in json.load(open(os.path.join(d, 'lessons.json'))):
        make(l, os.path.join(d, 'jpg', l['slug'] + '.jpg'))
