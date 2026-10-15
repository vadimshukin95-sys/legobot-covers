/* LEGObot: доп. скрипт сайта (15.10.2026, версия 2.2).
   1) Ссылка «Оплата по счёту для школ и организаций» (/dlya-organizatsiy) в карточке товара и в подвале.
   2) Цель VK Рекламы «lb_order» (пиксель 3803867): оформление заказа в корзине Тильды.
   3) Карточка товара: цена за занятие/проект под ценой, точная ссылка на бесплатный образец,
      строка о возврате денег в блоке «Доступ сразу после оплаты».
   4) /free?s=<uid товара>: прокрутка к бесплатному образцу этого товара и подсветка карточки.
   5) Вкладка каталога «Модули» ведёт сразу к блоку модулей на /programmy.
   Подключается одной строкой в head Тильды. */
(function () {
  var URL = '/dlya-organizatsiy';
  var HERE = location.pathname.replace(/\/$/, '') === URL;
  var ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 21v-6h6v6"/></svg>';
  var INFO = '.t-catalog__prod-popup__info, .t-store__prod-popup__info';
  var BTNW = '.t-catalog__prod-popup__btn-wrapper, .t-store__prod-popup__btn-wrapper';
  var PRICEW = '.t-catalog__prod-popup__price-wrapper, .t-store__prod-popup__price-wrapper';

  /* Сколько занятий/проектов в товаре. Только там, где число однозначно указано в описании. */
  var N = {"901618958493":[12,"z"],"293805346522":[7,"u"],"839099621912":[12,"u"],"435883242842":[17,"m"],"142701270192":[15,"u"],"838094231762":[14,"u"],"696465629392":[14,"u"],"236219282172":[17,"p"],"976869736692":[12,"u"],"532355804202":[15,"u"],"935571797982":[24,"p"],"604779154532":[6,"u"],"600182623282":[12,"p"],"442044889892":[14,"p"],"186191303442":[12,"p"],"348413999972":[13,"p"],"552911485962":[13,"p"],"528772165992":[12,"p"],"224862346802":[7,"p"],"868327278962":[9,"p"],"163995274422":[8,"p"],"745614872992":[12,"p"],"353901833982":[12,"p"],"267792810792":[16,"m"],"657848544472":[22,"p"],"515438778432":[12,"p"],"924391820292":[12,"p"],"861829750522":[12,"p"],"489602540072":[12,"m"],"806642115992":[12,"p"],"363185791022":[11,"p"],"670042776032":[6,"p"],"266076173742":[12,"m"],"193416478532":[12,"m"],"207321983272":[12,"m"],"279382143972":[12,"m"],"413473919382":[12,"m"],"714092548482":[19,"m"],"592406108442":[12,"u"],"384514077352":[12,"u"],"833150696412":[12,"u"],"358817540502":[13,"u"],"204372579072":[12,"u"],"216595345782":[12,"p"],"729946522912":[12,"p"],"488720662692":[13,"p"],"655648391642":[12,"p"],"953602141032":[12,"p"],"565003897992":[5,"u"],"394337210352":[13,"p"],"595450015492":[12,"p"],"542513975112":[12,"p"],"543730200862":[12,"p"],"102039327532":[12,"p"],"511343817622":[12,"p"],"764874542382":[12,"p"],"699274734302":[12,"p"],"956454334322":[12,"p"],"883688902162":[12,"p"],"627795536152":[15,"z"],"458855565132":[12,"z"],"527871527902":[12,"z"],"222910076462":[12,"z"],"512589990682":[12,"z"],"551862925672":[8,"z"],"884804429312":[9,"z"],"597143089732":[9,"v"],"728227751032":[7,"u"],"948833215422":[11,"z"],"320831997612":[12,"z"],"335387917012":[18,"u"],"990373488562":[18,"z"],"995663991372":[12,"u"],"591930146992":[13,"z"],"486455666512":[16,"z"],"120539163062":[15,"z"],"414325103392":[13,"z"],"187411270912":[11,"z"],"641636446923":[4,"l"],"774810129082":[36,"z"],"962792484412":[72,"z"],"362408943602":[12,"z"],"221008788142":[12,"u"],"365019728732":[7,"z"],"423556643092":[72,"u"],"201647972862":[21,"u"],"918379809843":[12,"z"],"882828919983":[12,"z"],"604503869863":[8,"z"],"917311354782":[17,"u"],"405289017982":[11,"u"],"467700396982":[12,"u"],"236584761192":[12,"p"],"169845365662":[7,"p"],"231507111052":[5,"p"],"653009945652":[5,"p"],"737310296122":[12,"p"],"385973104762":[12,"p"],"968843745222":[12,"p"],"558876309492":[7,"p"],"263544041162":[8,"p"],"288923012362":[8,"p"],"868350331012":[8,"p"],"564705714892":[8,"p"],"383363417852":[12,"p"],"181965590522":[10,"p"],"773974751292":[5,"i"],"982437469792":[9,"p"],"249910245182":[272,"p"],"876933129942":[163,"p"],"793861959912":[130,"p"],"322365895312":[461,"p"],"266841183272":[13,"p"],"723977087322":[11,"p"],"307716726122":[12,"p"],"306851502532":[9,"p"],"256833749692":[12,"p"],"715118901532":[9,"i"],"601060446802":[53,"p"],"494247170242":[13,"u"],"887744151652":[13,"u"],"806486718982":[12,"u"],"355785390082":[17,"u"],"433694354162":[16,"u"],"207399980172":[12,"u"],"374550830192":[6,"p"],"348202492462":[7,"p"],"594103504922":[12,"p"],"548680053802":[12,"p"],"919806588492":[70,"z"],"978425645022":[6,"z"],"832734947273":[36,"z"],"728076658503":[5,"u"],"680766098383":[13,"z"],"767011387422":[12,"z"],"871833543493":[10,"z"]};
  var U = { /* формы: 1, 2–4, 5+, род для «каждый» */
    p: ['проект', 'проекта', 'проектов', 'каждый'],
    u: ['урок', 'урока', 'уроков', 'каждый'],
    z: ['занятие', 'занятия', 'занятий', 'каждое'],
    m: ['модель', 'модели', 'моделей', 'каждую'],
    i: ['инструкция', 'инструкции', 'инструкций', 'каждую'],
    v: ['видеоурок', 'видеоурока', 'видеоуроков', 'каждый'],
    l: ['лист', 'листа', 'листов', 'каждый']
  };

  /* Бесплатный образец на /free: 1 — первый урок, 2 — урок целиком, 3 — фрагмент, 4 — лист, 5 — видео. */
  var FREE = {
    '458855565132': 1, '527871527902': 1, '222910076462': 1, '512589990682': 1, '551862925672': 1,
    '948833215422': 1, '320831997612': 1, '627795536152': 1, '728227751032': 1, '918379809843': 1,
    '882828919983': 1, '774810129082': 1, '680766098383': 1, '978425645022': 1, '266841183272': 1,
    '901618958493': 1, '884804429312': 2, '221008788142': 2, '362408943602': 2, '365019728732': 2,
    '728076658503': 2, '423556643092': 3, '962792484412': 3, '919806588492': 3, '832734947273': 3,
    '641636446923': 4, '597143089732': 5
  };
  var FREE_TXT = {
    1: ['Первый урок — бесплатно', 'Скачайте и проведите до покупки'],
    2: ['Урок из курса — бесплатно', 'Целиком: скачайте и проведите до покупки'],
    3: ['Пример материалов — бесплатно', 'Посмотрите, как всё устроено, до покупки'],
    4: ['Первый лист — бесплатно', 'Распечатайте и проведите до покупки'],
    5: ['Первое видео — бесплатно', 'Посмотрите в браузере до покупки'],
    6: ['Инструкция WeDo 2.0 — бесплатно', 'Соберите модель и оцените формат до покупки']
  };

  function css() {
    if (document.getElementById('lb-org-css')) return;
    var s = document.createElement('style');
    s.id = 'lb-org-css';
    s.textContent =
      '.lb-orgnote-wrap{margin-top:14px}' +
      '.lb-orgnote{display:inline-flex;align-items:center;gap:8px;font:700 15px/1.35 Nunito,Arial,sans-serif;color:#2e7a1c!important;text-decoration:none!important;border-bottom:1.5px solid rgba(46,122,28,.35);padding-bottom:2px}' +
      '.lb-orgnote:hover{border-bottom-color:#2e7a1c}' +
      '.lb-orgnote svg{width:17px;height:17px;flex:none}' +
      '.lb-ppl-on{margin-bottom:6px!important}' +
      '.lb-ppl{margin:0 0 20px;font:600 15.5px/1.4 Nunito,Arial,sans-serif;color:#5d655f}' +
      '.lb-ppl b{font-weight:800;color:#2e7a1c}' +
      '.lb-ptrust .lb-ptrust__g a{color:inherit!important;text-decoration:underline!important;text-decoration-color:rgba(61,68,63,.35)!important;text-underline-offset:3px}' +
      '.lb-ptrust .lb-ptrust__g a:hover{text-decoration-color:currentColor!important}' +
      '.lb-free__card.lb-hit{outline:3px solid #4bae2e;outline-offset:5px;animation:lbHit 1.4s ease-out 2}' +
      '@media (max-width:560px){.lb-free__card.lb-hit{outline-offset:2px}}' +
      '@keyframes lbHit{0%{box-shadow:0 0 0 0 rgba(75,174,46,.45)}100%{box-shadow:0 0 0 18px rgba(75,174,46,0)}}';
    (document.head || document.documentElement).appendChild(s);
  }

  function plural(n, f) {
    var a = n % 10, b = n % 100;
    return (a === 1 && b !== 11) ? f[0] : (a >= 2 && a <= 4 && (b < 12 || b > 14)) ? f[1] : f[2];
  }
  function money(x) { return String(x).replace(/\B(?=(\d{3})+(?!\d))/g, '\u00a0'); }
  function setHTML(el, h) { if (el.innerHTML !== h) el.innerHTML = h; }
  function uidOf(info) { var p = info.closest('[data-product-uid]'); return p ? p.getAttribute('data-product-uid') : ''; }
  function nameOf(info) { var h = info.querySelector('.js-product-name'); return h ? h.textContent : ''; }

  function orgnote(info) {
    var w = info.querySelector(BTNW);
    if (!w) return;
    var all = info.querySelectorAll('.lb-orgnote-wrap');
    for (var i = 1; i < all.length; i++) all[i].parentNode.removeChild(all[i]);
    if (all.length) return;
    var d = document.createElement('div');
    d.className = 'lb-orgnote-wrap';
    d.innerHTML = '<a class="lb-orgnote" href="' + URL + '">' + ICON + 'Оплата по счёту для школ и организаций</a>';
    w.parentNode.insertBefore(d, w.nextSibling);
  }

  /* «12 занятий — по 50 ₽ за каждое» под ценой */
  function perLesson(info, uid) {
    var pw = info.querySelector(PRICEW), old = info.querySelector('.lb-ppl');
    var c = N[uid], pe = info.querySelector('.js-product-price');
    var price = pe ? parseFloat(pe.getAttribute('data-product-price-def') || pe.textContent.replace(/[^\d.,]/g, '').replace(',', '.')) : 0;
    if (!pw || !c || !(price > 0) || c[0] < 2) { if (old) old.parentNode.removeChild(old); return; }
    var f = U[c[1]], per = price / c[0], r = Math.round(per);
    var h = c[0] + ' ' + plural(c[0], f) + ' — <b>' + (Math.abs(per - r) < 0.01 ? 'по ' : 'около ') + money(r) + '\u00a0₽</b> за ' + f[3];
    if (!old) {
      old = document.createElement('div');
      old.className = 'lb-ppl';
      pw.parentNode.insertBefore(old, pw.nextSibling);
    }
    if (!pw.classList.contains('lb-ppl-on')) pw.classList.add('lb-ppl-on');
    setHTML(old, h);
  }

  /* Строка о возврате денег. На странице товара блок .lb-ptrust создаёт основной скрипт сайта,
     во всплывающей карточке (из каталога) его нет — создаём такой же. */
  function trust(info) {
    var t = info.querySelector('.lb-ptrust');
    var isPage = !!document.querySelector('#allrecords[data-product-page="y"]') && !info.closest('.t-popup');
    if (!t) {
      if (isPage || !document.documentElement.classList.contains('lb-v2')) return;
      var after = info.querySelector('.lb-orgnote-wrap') || info.querySelector(BTNW);
      if (!after) return;
      t = document.createElement('div');
      t.className = 'lb-ptrust';
      t.innerHTML = '<span>Доступ сразу после оплаты — на почту</span><span>PDF, можно печатать</span><span>Вопрос — в чат или Telegram</span>';
      after.parentNode.insertBefore(t, after.nextSibling);
    }
    if (!t.querySelector('.lb-ptrust__g')) {
      var g = document.createElement('span');
      g.className = 'lb-ptrust__g';
      g.innerHTML = '<a href="/refund">Вернём деньги, если файлы не откроются</a>';
      t.appendChild(g);
    }
  }

  /* Бесплатный образец в блоке «Что взять дальше»: точная ссылка и подпись под конкретный товар */
  function freeLink(info, uid) {
    var xs = info.querySelector('.lb-xs');
    var nm = nameOf(info);
    var kind = FREE[uid] || (/инструкц/i.test(nm) && /wedo\s*2/i.test(nm) && !/9580/.test(nm) ? 6 : 0);
    if (!kind) return;
    /* Основной скрипт не строит «Что взять дальше» для части курсов (например, «Робо-парк») — создаём блок сами */
    var X = window.LBXS;
    if (!xs && X && X.E && !X.E[uid] && (!/инструкц/i.test(nm) || /курс|программ|модул|методич|карт|комплект/i.test(nm)) &&
        document.documentElement.classList.contains('lb-v2')) {
      var anchor = info.querySelector('.lb-ptrust') || info.querySelector(BTNW);
      if (!anchor) return;
      xs = document.createElement('div');
      xs.className = 'lb-xs';
      xs.setAttribute('data-uid', uid);
      xs.innerHTML = '<b>Что взять дальше</b>';
      anchor.parentNode.insertBefore(xs, anchor.nextSibling);
    }
    if (!xs || xs.getAttribute('data-uid') !== uid) return;
    var a = xs.querySelector('.lb-xs__free');
    var href = '/free?s=' + (kind === 6 ? 'wedo' : uid);
    if (a && a.getAttribute('data-lbfree') === href) return;
    if (!a) {
      a = document.createElement('a');
      a.className = 'lb-xs__i lb-xs__free';
      a.innerHTML = '<span></span><small></small>';
      var head = xs.querySelector('b');
      xs.insertBefore(a, head ? head.nextSibling : xs.firstChild);
      var items = xs.querySelectorAll('.lb-xs__i');
      if (items.length > 3) items[items.length - 1].parentNode.removeChild(items[items.length - 1]);
    }
    a.href = href;
    a.setAttribute('data-lbfree', href);
    a.querySelector('span').textContent = FREE_TXT[kind][0];
    a.querySelector('small').textContent = FREE_TXT[kind][1];
  }

  /* Исправленные подписи в «Что взять дальше» (данные блока лежат в head-scripts.js) */
  var XS_FIX = { mw2: ['995663991372', '12 занятий по 60–90 минут'] };
  function xsFix() {
    var X = window.LBXS, k, f, i, a, sm;
    for (k in XS_FIX) {
      f = XS_FIX[k];
      if (X && X.T && X.T[k] && X.T[k][3] !== f[1]) X.T[k][3] = f[1];
      a = document.querySelectorAll('.lb-xs__i[href*="-' + f[0] + '-"]');
      for (i = 0; i < a.length; i++) {
        sm = a[i].querySelector('small');
        if (sm && sm.textContent !== f[1]) sm.textContent = f[1];
      }
    }
  }

  /* Порядок под кнопкой: оплата по счёту → «Доступ сразу после оплаты» → «Что взять дальше» */
  function order(info) {
    var w = info.querySelector(BTNW);
    if (!w) return;
    var prev = w;
    [info.querySelector('.lb-orgnote-wrap'), info.querySelector('.lb-ptrust'), info.querySelector('.lb-xs')].forEach(function (el) {
      if (!el) return;
      if (prev.nextElementSibling !== el) prev.parentNode.insertBefore(el, prev.nextSibling);
      prev = el;
    });
  }

  function product() {
    var infos = document.querySelectorAll(INFO);
    for (var i = 0; i < infos.length; i++) {
      var info = infos[i], uid = uidOf(info);
      orgnote(info);
      if (!uid) continue;
      perLesson(info, uid);
      trust(info);
      freeLink(info, uid);
      order(info);
    }
  }

  function footer() {
    if (HERE) return;
    var x = document.querySelector('.lb-legal .lb-legal__links') || document.querySelector('.lb-legal');
    if (!x || x.querySelector('a[href="' + URL + '"]')) return;
    var a = document.createElement('a');
    a.href = URL;
    a.textContent = 'Оплата по счёту для организаций';
    x.appendChild(a);
  }

  /* /free?s=<uid>: прокрутить к образцу и подсветить карточку */
  var freeDone = false;
  function freeTarget() {
    if (freeDone || !/^\/free\/?$/.test(location.pathname)) return;
    var m = /[?&]s=(\w+)/.exec(location.search);
    if (!m) { freeDone = true; return; }
    var cards = [].slice.call(document.querySelectorAll('.lb-free__card'));
    if (!cards.length) return;
    freeDone = true;
    var hit = cards.filter(function (c) {
      var l = c.querySelector('a.lb-free__link'), h = l ? l.getAttribute('href') || '' : '';
      return m[1] === 'wedo' ? h === '/lego-wedo-2' : h.indexOf('-' + m[1] + '-') > -1;
    });
    if (!hit.length) return;
    hit.forEach(function (c) { c.classList.add('lb-hit'); });
    setTimeout(function () {
      var r = hit[0].getBoundingClientRect();
      var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({ top: Math.max(0, r.top + window.pageYOffset - (window.innerHeight - r.height) / 2), behavior: reduce ? 'auto' : 'smooth' });
    }, 350);
    setTimeout(function () { hit.forEach(function (c) { c.classList.remove('lb-hit'); }); }, 9000);
  }

  /* Вкладка каталога «Модули» привязана к странице /programmy, где модули — второй каталог ниже
     «Программ и методик». Ведём сразу к модулям: /programmy#moduli и прокрутка к блоку. */
  var MOD = { part: '189481412942', url: '/programmy', hash: '#moduli', rec: 'rec4598598301' };
  function onProgrammy() { return location.pathname.replace(/\/$/, '') === MOD.url; }
  function modTabs() {
    var a = document.querySelectorAll('a.t-catalog__parts-button-base[data-storepart-uid="' + MOD.part + '"]');
    for (var i = 0; i < a.length; i++) {
      if (a[i].getAttribute('href') !== MOD.url + MOD.hash) a[i].setAttribute('href', MOD.url + MOD.hash);
    }
  }
  /* Высота закреплённых сверху полос (промо-строка, меню), чтобы заголовок не прятался под ними */
  function topOffset() {
    var list = [], els = document.querySelectorAll('body *'), w = window.innerWidth, i, cs, r;
    for (i = 0; i < els.length; i++) {
      cs = getComputedStyle(els[i]);
      if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
      if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
      r = els[i].getBoundingClientRect();
      if (r.top < 200 && r.bottom > 0 && r.height > 20 && r.height < 220 && r.width > w / 2) list.push(r);
    }
    list.sort(function (a, b) { return a.top - b.top; });
    var max = 0;
    for (i = 0; i < list.length; i++) if (list[i].top <= max + 2) max = Math.max(max, list[i].bottom);
    return max;
  }
  function modTarget() {
    var rec = document.getElementById(MOD.rec);
    if (!rec) return null;
    var h = rec.querySelector('h2, .t-catalog__title, .t-section__title, .t-name') || rec;
    return Math.max(0, Math.round(h.getBoundingClientRect().top + window.pageYOffset - topOffset() - 16));
  }
  function scrollToMod(smooth) {
    var y = modTarget();
    if (y === null) return false;
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({ top: y, behavior: smooth && !reduce ? 'smooth' : 'auto' });
    return true;
  }
  var modDone = false;
  function modArrive() {
    if (modDone || !onProgrammy() || location.hash !== MOD.hash) return;
    modDone = true;
    var stop = false, n = 0, stable = 0;
    function halt() { stop = true; }
    ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function (ev) { window.addEventListener(ev, halt, { once: true, passive: true }); });
    /* Каталоги на странице дорисовываются после загрузки и сдвигают блок модулей вниз.
       Поправляем позицию, пока товары не появятся и положение не устоится, или пока человек не начнёт листать сам. */
    (function again() {
      if (stop || ++n > 45) return;
      var y = modTarget();
      if (y !== null) {
        if (Math.abs(window.pageYOffset - y) > 4) { window.scrollTo(0, y); stable = 0; } else stable++;
        var ready = document.querySelector('#' + MOD.rec + ' .js-product') && document.readyState === 'complete';
        if (ready && stable >= 3) return;
      }
      setTimeout(again, 300);
    })();
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a.t-catalog__parts-button-base[data-storepart-uid="' + MOD.part + '"]');
    if (!a || e.ctrlKey || e.metaKey || e.shiftKey || e.button > 0) return;
    e.preventDefault();
    e.stopPropagation();
    if (e.stopImmediatePropagation) e.stopImmediatePropagation();
    if (onProgrammy()) {
      try { history.replaceState(null, '', MOD.url + MOD.hash); } catch (er) {}
      scrollToMod(true);
    } else {
      location.href = MOD.url + MOD.hash;
    }
  }, true);

  /* Цель VK «lb_order»: Тильда при успешной отправке заказа из корзины вызывает
     Tilda.sendEventToStatistics(..., "Order <номер>", ..., сумма). Перехватываем этот вызов. */
  function hookOrder() {
    var T = window.Tilda;
    if (!T || typeof T.sendEventToStatistics !== 'function') return false;
    if (T.sendEventToStatistics.__lb) return true;
    var orig = T.sendEventToStatistics;
    var wrapped = function (name, title, products, price) {
      try {
        if (/^Order /.test(String(title || ''))) {
          var q = window._tmr || (window._tmr = []);
          var goal = { type: 'reachGoal', id: 3803867, goal: 'lb_order' };
          var v = parseFloat(price);
          if (v > 0) goal.value = v;
          q.push(goal);
        }
      } catch (e) {}
      return orig.apply(this, arguments);
    };
    wrapped.__lb = true;
    T.sendEventToStatistics = wrapped;
    return true;
  }

  function run() {
    try { css(); } catch (e) {}
    try { product(); } catch (e) {}
    try { xsFix(); } catch (e) {}
    try { footer(); } catch (e) {}
    try { freeTarget(); } catch (e) {}
    try { modTabs(); modArrive(); } catch (e) {}
    try { hookOrder(); } catch (e) {}
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
  var timer;
  new MutationObserver(function () { clearTimeout(timer); timer = setTimeout(run, 200); })
    .observe(document.documentElement, { childList: true, subtree: true });
  var tries = 0, iv = setInterval(function () { if (hookOrder() || ++tries > 60) clearInterval(iv); }, 500);
})();
