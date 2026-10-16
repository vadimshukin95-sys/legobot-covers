import json, csv, html, io
def pl(n,f):
    a,b=n%10,n%100
    return f[0] if a==1 and b!=11 else f[1] if 2<=a<=4 and not 12<=b<=14 else f[2]
D=json.load(open('models.json')); IM=json.load(open('imgmap.json'))
S=D['set']; e=html.escape
def txt(x): return f'<div class="t-redactor__text">{x}</div>'
def h2(x): return f'<h2 class="t-redactor__h2">{e(x)}</h2>'
def img(src,alt): return f'<figure class="t-redactor__figure"><img src="{src}" alt="{e(alt)}"></figure>'
rows=[]
for m in D['models']:
    slug=m['slug']
    facts='<br>'.join([
        f"<strong>Конструктор:</strong> LEGO Education WeDo 2.0 (45300)",
        f"<strong>Шагов сборки:</strong> {m['steps']}",
        f"<strong>Сложность:</strong> {e(m['level'].lower())}",
        f"<strong>Время на сборку:</strong> {e(m['time'])}",
        f"<strong>Возраст:</strong> {e(m['age'])}",
        f"<strong>Электроника:</strong> {e(m['electronics'])}"])
    body=[txt(facts),
          txt(f"Полная пошаговая инструкция на {m['steps']} {pl(m['steps'],['шаг','шага','шагов'])} — в «<a href=\"{S['url']}\" target=\"_blank\">{e(S['title'])}</a>». Доступ приходит на почту сразу после оплаты."),
          h2('Что делает модель'), txt(e(m['what'])),
          h2('Чему учит'), txt('<ul>'+''.join(f'<li>{e(x)}</li>' for x in m['learn'])+'</ul>'),
          h2('Как запрограммировать'), txt(e(m['program']))]
    if m.get('program_img') and IM.get(slug+'-program.jpg'):
        body.append(img(IM[slug+'-program.jpg'], f"Программа для модели «{m['name']}» в блоках WeDo 2.0"))
    body += [txt(f"Собрать программу можно прямо в браузере, в нашей <a href=\"{S['app_url']}\" target=\"_blank\">онлайн-среде WeDo</a>: подключите смартхаб по Bluetooth и перетащите блоки."),
             h2('Задания для урока'), txt('<ol>'+''.join(f'<li>{e(x)}</li>' for x in m['challenge'])+'</ol>'),
             h2('Где взять инструкцию'),
             txt(f"Модель входит в «<a href=\"{S['url']}\" target=\"_blank\">{e(S['title'])}</a>» — 24 пошаговые PDF-инструкции для базового набора LEGO Education WeDo 2.0. Другие наборы — в <a href=\"{S['all_sets_url']}\">каталоге LEGO WeDo 2.0</a>, бесплатные уроки — на странице <a href=\"{S['free_url']}\">бесплатных материалов</a>.")]
    cover=IM[slug+'-cover.jpg']
    rows.append({'Alias':m['alias'],'Title':m['h1'],'Category':'Набор WeDo 2.0 №20','Media Type':'image','Media':cover,
        'Description':m['short'],'Text':''.join(body),'Date':'2026-10-15 12:00:00+03:00','Visibility':'draft',
        'Thumb Image':cover,'SEO Title':m['seo_title'],'SEO Description':m['seo_description'],
        'Social Title':m['seo_title'],'Social Description':m['seo_description'],'Social Image':cover})
buf=io.StringIO()
w=csv.DictWriter(buf,fieldnames=list(rows[0]),delimiter=';',quoting=csv.QUOTE_ALL,lineterminator='\n'); w.writeheader(); w.writerows(rows)
open('stream.csv','w',encoding='utf-8').write(buf.getvalue())
# Импорт CSV в Потоки теряет <figure>: на его месте остаётся пустой текстовый блок.
# После импорта картинки ставятся через редактор поста (tTextEditor.API.Blocks.updateBlock → type:image).
fix={m['alias']:[IM[m['slug']+'-program.jpg'], f"Программа для модели «{m['name']}» в блоках WeDo 2.0"]
     for m in D['models'] if m.get('program_img') and IM.get(m['slug']+'-program.jpg')}
json.dump(fix,open('imgfix.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(buf.getvalue()), [len(r['Text']) for r in rows])
print([ (r['SEO Title'],len(r['SEO Title'])) for r in rows])
