/* LEGObot · акция «Чёрная пятница 11.11 · 1+1=3» (02.11–12.11.2026, МСК)
   Плашка-карточка (графит) на всех страницах + поле «Подарок» в корзине (name="podarok").
   После окончания акции скрипт ничего не делает — его можно просто убрать из HEAD. */
(function () {
  'use strict';
  var CFG = {
    start: new Date('2026-11-02T00:00:00+03:00'),
    end: new Date('2026-11-12T23:59:59+03:00'),
    catalog: '/#catalog',
    field: 'podarok',
    min: 2,
    excluded: ['WD2-002', 'SPP-001', 'EV3-003', 'L96-001', 'SPC-003'],
    noGift: ['SPC-001', 'PRG-002', 'KIT-WD2P', 'KIT-ESS', 'KIT-M9580', 'KIT-MWD2', 'KIT-MEV3', 'KIT-MSCR'],
    hits: ['WD2-30', 'SPP-21', 'ESS-006', 'WD2-31', 'WEDO-MC-05', 'EV3-15', 'LE9686-1', 'LB-SPK-72'],
    parts: {
      '834944430272': 'WeDo 2.0', '805464414372': 'SPIKE Prime', '687099458723': 'SPIKE Essential',
      '495585029632': 'EV3', '884948347352': '9686', '114076436112': 'WeDo 9580', '971020722062': 'Scratch',
      '945347836132': 'Программы и методики', '189481412942': 'Модули', '898389104672': 'Спецпредложения'
    },
    pages: [[/lego-wedo-2|wedo-2|wedo2/i, 'WeDo 2.0'], [/spike-prime/i, 'SPIKE Prime'], [/spike-essential/i, 'SPIKE Essential'],
            [/lego-ev3|\/ev3/i, 'EV3'], [/9686/, '9686'], [/9580/, 'WeDo 9580'], [/^\/prog/i, 'PROG']]
  };
  var now = new Date();
  if (now < CFG.start || now > CFG.end) return;

  var ORDER = ['WeDo 2.0', 'SPIKE Prime', 'SPIKE Essential', 'EV3', '9686', 'WeDo 9580', 'Scratch',
               'Программы и методики', 'Модули', 'Спецпредложения'];
  var norm = function (s) { return String(s || '').toUpperCase().replace(/[\s\-_]/g, ''); };
  var inList = function (list, sku) { var n = norm(sku); for (var i = 0; i < list.length; i++) if (norm(list[i]) === n) return true; return false; };
  var rub = function (n) { return Math.round(n).toLocaleString('ru-RU') + ' ₽'; };
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
                set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };

  /* ---------- каталог из Tilda Store API ---------- */
  var catalogPromise = null;
  function loadCatalog() {
    if (catalogPromise) return catalogPromise;
    var cached = null;
    try { cached = JSON.parse(sessionStorage.getItem('lbbf_cat') || 'null'); } catch (e) {}
    if (cached && Date.now() - cached.ts < 30 * 60 * 1000) return (catalogPromise = Promise.resolve(cached.items));
    var uids = Object.keys(CFG.parts), map = {};
    catalogPromise = Promise.all(uids.map(function (u) {
      return fetch('https://store.tildaapi.com/api/getproductslist/?storepartuid=' + u + '&slice=1&size=500')
        .then(function (r) { return r.json(); })
        .then(function (j) {
          (j.products || []).forEach(function (p) {
            if (!p.sku) return;
            var g = []; try { g = JSON.parse(p.gallery || '[]'); } catch (e) {}
            var it = map[p.sku] || { sku: p.sku, title: String(p.title || '').replace(/\s+/g, ' ').trim(),
              price: parseFloat(p.price) || 0, img: (g[0] && g[0].img) || '', groups: [] };
            if (it.groups.indexOf(CFG.parts[u]) < 0) it.groups.push(CFG.parts[u]);
            map[p.sku] = it;
          });
        })['catch'](function () {});
    })).then(function () {
      var items = Object.keys(map).map(function (k) {
        var it = map[k];
        it.group = ORDER.filter(function (g) { return it.groups.indexOf(g) >= 0; })[0] || 'Другое';
        return it;
      });
      try { sessionStorage.setItem('lbbf_cat', JSON.stringify({ ts: Date.now(), items: items })); } catch (e) {}
      return items;
    });
    return catalogPromise;
  }

  /* ---------- стили ---------- */
  var css = '' +
  '#lbbf{position:fixed;left:20px;bottom:20px;z-index:99980;font-family:Nunito,Arial,sans-serif;-webkit-font-smoothing:antialiased;transition:opacity .3s,transform .3s}' +
  '#lbbf.lbbf-hide{opacity:0;transform:translateY(20px);pointer-events:none}' +
  '#lbbf *{box-sizing:border-box}#lbbf a{color:inherit;text-decoration:none}' +
  '#lbbf .lbbf-c{position:relative;width:290px;padding:16px 18px;border-radius:18px;overflow:hidden;color:#fff;' +
  'background:radial-gradient(circle at 12px 12px,rgba(255,255,255,.05) 5px,transparent 6px) 0 0/24px 24px,linear-gradient(160deg,#41444d,#2b2d33);' +
  'box-shadow:0 14px 40px rgba(20,20,40,.25),inset 0 0 0 1px rgba(255,255,255,.08)}' +
  '#lbbf .lbbf-x{position:absolute;right:10px;top:10px;width:26px;height:26px;border-radius:50%;background:rgba(255,255,255,.1);color:#c3c5cc;font-size:17px;line-height:25px;text-align:center;cursor:pointer;z-index:5}' +
  '#lbbf .lbbf-fan{position:relative;height:118px;margin:6px 0 8px}' +
  '#lbbf .lbbf-cv{position:absolute;top:6px;left:50%;width:100px;height:100px;border-radius:10px;overflow:hidden;background:#fff;box-shadow:0 8px 18px rgba(0,0,0,.3)}' +
  '#lbbf .lbbf-cv img{width:100%;height:100%;object-fit:cover;display:block;transition:opacity .4s}' +
  '#lbbf .lbbf-l{transform:translate(-128%,12px) rotate(-10deg) scale(.86)}#lbbf .lbbf-m{transform:translate(-50%,0) scale(1.05);z-index:2}#lbbf .lbbf-r{transform:translate(28%,12px) rotate(10deg) scale(.86)}' +
  '#lbbf .lbbf-tag{position:absolute;left:50%;top:-2px;transform:translateX(-50%) rotate(-4deg);z-index:4;background:#F59F00;color:#fff;font-weight:900;font-size:11px;letter-spacing:1.2px;padding:3px 9px;border-radius:20px;box-shadow:0 3px 8px rgba(0,0,0,.25)}' +
  '#lbbf .lbbf-k{display:inline-block;font-size:10.5px;letter-spacing:2px;font-weight:800;background:rgba(255,255,255,.12);padding:4px 9px;border-radius:6px}' +
  '#lbbf .lbbf-big{font-weight:900;font-size:40px;line-height:1;letter-spacing:-1px;margin:8px 0 4px}#lbbf .lbbf-big em{font-style:normal;color:#F59F00}' +
  '#lbbf .lbbf-s{font-size:13.5px;line-height:1.35;opacity:.88;margin-bottom:10px}' +
  '#lbbf .lbbf-tm{display:flex;gap:5px;margin-bottom:12px}#lbbf .lbbf-tm div{background:rgba(255,255,255,.1);border-radius:8px;padding:4px 0;min-width:40px;text-align:center}' +
  '#lbbf .lbbf-tm b{display:block;font-size:17px;font-variant-numeric:tabular-nums}#lbbf .lbbf-tm small{font-size:9.5px;color:#c3c5cc}' +
  '#lbbf .lbbf-btn{display:block;text-align:center;background:#F59F00;color:#fff;font-weight:800;border-radius:10px;padding:11px 14px;font-size:15px;box-shadow:0 4px 14px rgba(245,159,0,.3)}#lbbf .lbbf-btn:hover{background:#ffad14}' +
  '#lbbf .lbbf-mb{display:none}' +
  '@media (max-width:640px){#lbbf{left:0;right:0;bottom:0}#lbbf .lbbf-c{display:none}' +
  '#lbbf .lbbf-mb{display:flex;align-items:center;gap:10px;padding:9px 12px;color:#fff;border-top:2px solid #F59F00;box-shadow:0 -6px 20px rgba(0,0,0,.2);' +
  'background:radial-gradient(circle at 12px 12px,rgba(255,255,255,.05) 5px,transparent 6px) 0 0/24px 24px,linear-gradient(90deg,#41444d,#2b2d33)}' +
  '#lbbf .lbbf-vis{position:relative;width:56px;height:46px;flex:0 0 56px}#lbbf .lbbf-vis .lbbf-cv{width:40px;height:40px;border-radius:7px;left:0;top:4px;transform:rotate(-8deg)}' +
  '#lbbf .lbbf-vis .lbbf-cv+.lbbf-cv{left:14px;top:2px;transform:rotate(7deg)}' +
  '#lbbf .lbbf-t{flex:1;min-width:0;line-height:1.25;white-space:nowrap;overflow:hidden}#lbbf .lbbf-t b{font-size:18px;font-weight:900;color:#F59F00;margin-right:4px}#lbbf .lbbf-t span{font-size:12.5px}' +
  '#lbbf .lbbf-t div{font-size:11.5px;color:#c3c5cc;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-variant-numeric:tabular-nums}' +
  '#lbbf .lbbf-go{background:#F59F00;border-radius:9px;padding:9px 12px;font-weight:800;font-size:13px}' +
  'body.lbbf-on .lb-chatbtn{bottom:84px!important}}' +
  /* витрина подарков в корзине */
  '.lbbf-g{margin:4px 0 18px;border-radius:14px;overflow:hidden;border:1px solid #e7e8ec;box-shadow:0 6px 18px rgba(20,20,40,.08);background:#fff;font-family:Nunito,Arial,sans-serif;color:#1c1c28;text-align:left}' +
  '.lbbf-g *{box-sizing:border-box}' +
  '.lbbf-gh{display:flex;align-items:center;gap:10px;padding:11px 14px;color:#fff;background:radial-gradient(circle at 12px 12px,rgba(255,255,255,.05) 5px,transparent 6px) 0 0/24px 24px,linear-gradient(160deg,#41444d,#2b2d33)}' +
  '.lbbf-gh em{font-style:normal;background:#F59F00;font-weight:900;padding:3px 8px;border-radius:8px;font-size:15px;white-space:nowrap}' +
  '.lbbf-gh b{display:block;font-size:14px;font-weight:900;line-height:1.2}.lbbf-gh small{display:block;font-size:11.5px;color:#c3c5cc;font-weight:600}' +
  '.lbbf-gch{display:flex;gap:6px;overflow-x:auto;padding:10px 12px 2px;scrollbar-width:none}.lbbf-gch::-webkit-scrollbar{display:none}' +
  '.lbbf-gch button{flex:0 0 auto;border:1px solid #e1e2e7;background:#fff;border-radius:20px;padding:5px 11px;font:700 12px Nunito,Arial,sans-serif;color:#444;cursor:pointer}' +
  '.lbbf-gch button.on{background:#34373f;color:#fff;border-color:#34373f}' +
  '.lbbf-grow{display:flex;gap:10px;overflow-x:auto;padding:10px 12px 12px;scroll-snap-type:x proximity;-webkit-overflow-scrolling:touch}' +
  '.lbbf-gc{flex:0 0 112px;scroll-snap-align:start;border-radius:10px;border:2px solid transparent;cursor:pointer;position:relative}' +
  '.lbbf-gc img{width:108px;height:108px;border-radius:8px;object-fit:cover;display:block;background:#f1f2f5;box-shadow:0 3px 10px rgba(0,0,0,.12)}' +
  '.lbbf-gc .t{font-size:11.5px;line-height:1.25;margin:6px 2px 2px;height:29px;overflow:hidden}.lbbf-gc .p{font-size:11.5px;margin:0 2px 2px}' +
  '.lbbf-gc .p s{color:#999}.lbbf-gc .p b{color:#F59F00}.lbbf-gc.on{border-color:#F59F00}' +
  '.lbbf-gc.on:after{content:"✓";position:absolute;right:6px;top:6px;width:22px;height:22px;border-radius:50%;background:#F59F00;color:#fff;font-weight:900;font-size:13px;line-height:22px;text-align:center}' +
  '.lbbf-gl{padding:12px 14px;font-size:13px;color:#5a5a66}.lbbf-gl .r{display:flex;gap:8px;margin-top:10px;filter:blur(1.5px) grayscale(.3);opacity:.6;overflow:hidden}' +
  '.lbbf-gl .r img{width:64px;height:64px;flex:0 0 64px;border-radius:8px;object-fit:cover}' +
  '.lbbf-gok{padding:0 14px 12px;font-size:12.5px;color:#2E9E5B;font-weight:700}.lbbf-gok a{color:#8b8b95;font-weight:600;margin-left:8px;cursor:pointer;text-decoration:underline}' +
  '.lbbf-ghl{margin-left:auto;font-size:11.5px;color:#c3c5cc!important;text-decoration:underline!important;white-space:nowrap}' +
  /* условия акции */
  '#lbbf .lbbf-tl{display:block;text-align:center;margin-top:8px;font-size:12px;color:#c3c5cc;text-decoration:underline}' +
  '#lbbf .lbbf-i{display:none}@media (max-width:640px){#lbbf .lbbf-i{display:flex;align-items:center;justify-content:center;flex:0 0 24px;height:24px;border-radius:50%;border:1.5px solid #c3c5cc;color:#c3c5cc;font:700 13px Georgia,serif}}' +
  '#lbbf-terms{position:fixed;inset:0;z-index:2147483100;background:rgba(20,20,30,.55);display:flex;align-items:center;justify-content:center;padding:16px;font-family:Nunito,Arial,sans-serif}' +
  '#lbbf-terms .w{position:relative;width:100%;max-width:520px;max-height:88vh;overflow:auto;background:#fff;color:#1c1c28;border-radius:16px;box-shadow:0 20px 50px rgba(0,0,0,.3)}' +
  '#lbbf-terms .h{padding:16px 48px 14px 18px;color:#fff;background:radial-gradient(circle at 12px 12px,rgba(255,255,255,.05) 5px,transparent 6px) 0 0/24px 24px,linear-gradient(160deg,#41444d,#2b2d33)}' +
  '#lbbf-terms .h small{display:block;font-size:11px;letter-spacing:2px;color:#c3c5cc;font-weight:800}#lbbf-terms .h b{font-size:19px;font-weight:900}#lbbf-terms .h em{font-style:normal;color:#F59F00}' +
  '#lbbf-terms .x{position:absolute;right:12px;top:12px;width:28px;height:28px;border-radius:50%;background:rgba(255,255,255,.15);color:#fff;text-align:center;line-height:27px;font-size:18px;cursor:pointer}' +
  '#lbbf-terms ol{margin:0;padding:14px 18px 6px 36px;font-size:14px;line-height:1.45}#lbbf-terms li{margin-bottom:8px}#lbbf-terms a{color:#e08e00}' +
  '#lbbf-terms .f{padding:0 18px 16px;font-size:12.5px;color:#6b6b76}';

  /* ---------- карточка ---------- */
  var root, rot, covers = [];
  function pickCovers(items) {
    var path = location.pathname, page = null;
    CFG.pages.forEach(function (p) { if (!page && p[0].test(path)) page = p[1]; });
    var ok = function (it) { return it.img && !inList(CFG.excluded, it.sku) && !inList(CFG.noGift, it.sku); };
    var list = [];
    if (page === 'PROG') list = items.filter(function (it) { return ok(it) && /^PROG-/i.test(it.sku); });
    else if (page) list = items.filter(function (it) { return ok(it) && it.groups.indexOf(page) >= 0; });
    if (list.length < 3) list = CFG.hits.map(function (s) { return items.filter(function (it) { return norm(it.sku) === norm(s); })[0]; })
      .filter(function (it) { return it && it.img; });
    for (var i = list.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = list[i]; list[i] = list[j]; list[j] = t; }
    return list.slice(0, 8);
  }
  function cv(cls, it) { return '<div class="lbbf-cv ' + cls + '"><img src="' + (it ? it.img : '') + '" alt="" loading="lazy"></div>'; }
  function buildCard(items) {
    covers = pickCovers(items);
    if (covers.length < 3) return;
    root = document.createElement('div');
    root.id = 'lbbf';
    root.innerHTML =
      '<div class="lbbf-c"><span class="lbbf-x" title="Скрыть">×</span>' +
      '<div class="lbbf-fan">' + cv('lbbf-l', covers[0]) + cv('lbbf-m', covers[1]) + cv('lbbf-r', covers[2]) + '<span class="lbbf-tag">ПОДАРОК</span></div>' +
      '<div class="lbbf-k">ЧЁРНАЯ ПЯТНИЦА 11.11</div><div class="lbbf-big">1+1<em>=3</em></div>' +
      '<div class="lbbf-s">Купите 2 материала — третий выберите в подарок</div>' +
      '<div class="lbbf-tm"><div><b data-d>0</b><small>дней</small></div><div><b data-h>00</b><small>часов</small></div><div><b data-m>00</b><small>минут</small></div><div><b data-s>00</b><small>секунд</small></div></div>' +
      '<a class="lbbf-btn" href="' + CFG.catalog + '">Выбрать материалы</a>' +
      '<a class="lbbf-tl" href="#" data-lbbf-terms>Условия акции</a></div>' +
      '<a class="lbbf-mb" href="' + CFG.catalog + '"><div class="lbbf-vis">' + cv('', covers[0]) + cv('', covers[1]) + '</div>' +
      '<div class="lbbf-t"><b>1+1=3</b><span>третий в подарок</span><div>ещё <span data-txt></span></div></div>' +
      '<span class="lbbf-i" data-lbbf-terms title="Условия акции">i</span><span class="lbbf-go">Выбрать</span></a>';
    document.body.appendChild(root);
    document.body.classList.add('lbbf-on');
    root.querySelector('.lbbf-x').addEventListener('click', function () {
      store.set('lbbf_closed', new Date().toDateString());
      root.parentNode.removeChild(root); document.body.classList.remove('lbbf-on'); clearInterval(rot);
    });
    var i = 0;
    rot = setInterval(function () {
      i = (i + 1) % covers.length;
      root.querySelectorAll('.lbbf-fan img').forEach(function (im, k) { im.src = covers[(i + k) % covers.length].img; });
    }, 2800);
    tick(); setInterval(tick, 1000);
  }
  function tick() {
    if (!root) return;
    var t = Math.max(0, CFG.end - new Date()), z = function (n) { return (n < 10 ? '0' : '') + n; };
    if (!t) { root.style.display = 'none'; return; }
    var d = Math.floor(t / 864e5), h = Math.floor(t / 36e5) % 24, m = Math.floor(t / 6e4) % 60, s = Math.floor(t / 1e3) % 60;
    var set = function (a, v) { root.querySelectorAll(a).forEach(function (e) { e.textContent = v; }); };
    set('[data-d]', d); set('[data-h]', z(h)); set('[data-m]', z(m)); set('[data-s]', z(s));
    set('[data-txt]', d + ' д ' + z(h) + ':' + z(m) + ':' + z(s));
    /* не мешаем корзине и напоминанию «Вы не закончили заказ» */
    var busy = document.querySelector('.lbcr-on, .t706__cartwin_showed');
    root.classList.toggle('lbbf-hide', !!busy);
  }

  /* ---------- витрина подарков в корзине ---------- */
  var G = { sig: '', chip: 'Все', sel: '' };
  var escA = function (s) { return String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;'); };
  function cartState() {
    var prods = (window.tcart && window.tcart.products) || [], seen = {}, count = 0, sum = 0, skus = [];
    prods.forEach(function (p) {
      if (!p || p.deleted === 'yes' || !p.sku) return;
      skus.push(norm(p.sku));
      if (inList(CFG.excluded, p.sku)) return;
      if (!seen[norm(p.sku)]) { seen[norm(p.sku)] = 1; count++; }
      sum += parseFloat(p.amount) || (parseFloat(p.price) || 0) * (parseFloat(p.quantity) || 1);
    });
    return { count: count, sum: sum, skus: skus };
  }
  function giftBox(form) {
    var box = form.querySelector('.lbbf-g');
    if (box) return box;
    var anchor = form.querySelector('.t-form__submit');
    if (!anchor) return null;
    box = document.createElement('div');
    box.className = 'lbbf-g';
    anchor.parentNode.insertBefore(box, anchor);
    box.addEventListener('click', function (e) {
      var t = e.target, c = t.closest('[data-c]'), k = t.closest('[data-k]'), x = t.closest('[data-x]');
      if (c) { e.preventDefault(); G.chip = c.getAttribute('data-c'); }
      else if (x) { e.preventDefault(); G.sel = ''; }
      else if (k) { var v = k.getAttribute('data-k'); G.sel = G.sel === v ? '' : v; }
      else return;
      G.sig = ''; renderGift(G.items);
    });
    return box;
  }
  function renderGift(items) {
    G.items = items;
    var form = document.querySelector('.t706 .t706__orderform form, .t706 form');
    if (!form) return;
    var box = giftBox(form);
    if (!box) return;
    var st = cartState();
    var gifts = st.count < CFG.min ? [] : items.filter(function (it) {
      return it.price > 0 && it.price <= st.sum && !inList(CFG.excluded, it.sku) && !inList(CFG.noGift, it.sku) &&
             st.skus.indexOf(norm(it.sku)) < 0;
    }).sort(function (a, b) { return (b.price - a.price) || a.title.localeCompare(b.title, 'ru'); });
    var gi = G.sel ? gifts.filter(function (it) { return it.sku === G.sel; })[0] : null;
    if (!gi) G.sel = '';
    var groups = ['Все'].concat(ORDER.filter(function (g) { return gifts.some(function (it) { return it.group === g; }); }));
    if (groups.indexOf(G.chip) < 0) G.chip = 'Все';
    var sig = [st.count, st.sum, st.skus.join(','), G.chip, G.sel].join('|');
    if (sig === G.sig) return;
    var row = box.querySelector('.lbbf-grow'), keep = row && box.getAttribute('data-chip') === G.chip ? row.scrollLeft : 0;
    G.sig = sig;
    var head = function (title, sub) {
      return '<div class="lbbf-gh"><em>1+1=3</em><div><b>' + title + '</b><small>' + sub + '</small></div>' +
        '<a class="lbbf-ghl" href="#" data-lbbf-terms>Условия</a></div>';
    };
    var html;
    if (st.count < CFG.min) {
      var teaser = CFG.hits.map(function (s) { return items.filter(function (it) { return norm(it.sku) === norm(s) && it.img; })[0]; })
        .filter(Boolean).slice(0, 5);
      html = head('Третий материал — в подарок', 'Чёрная пятница 11.11') +
        '<div class="lbbf-gl">' + (st.count ? 'Добавьте ещё ' + (CFG.min - st.count) + ' материал — и откроется выбор подарка'
                                              : 'Купите 2 материала — и третий выберете в подарок') +
        '<div class="r">' + teaser.map(function (it) { return '<img src="' + escA(it.img) + '" alt="">'; }).join('') + '</div></div>';
    } else {
      var list = gifts.filter(function (it) { return G.chip === 'Все' || it.group === G.chip; });
      html = head(gi ? 'Подарок выбран' : 'Выберите подарок', 'Чёрная пятница 11.11 · любой материал до ' + rub(st.sum)) +
        '<div class="lbbf-gch">' + groups.map(function (g) {
          return '<button type="button" data-c="' + escA(g) + '"' + (g === G.chip ? ' class="on"' : '') + '>' + g + '</button>';
        }).join('') + '</div>' +
        '<div class="lbbf-grow">' + list.map(function (it) {
          return '<div class="lbbf-gc' + (it.sku === G.sel ? ' on' : '') + '" data-k="' + escA(it.sku) + '" role="button" tabindex="0">' +
            '<img src="' + escA(it.img) + '" alt="" loading="lazy"><div class="t">' + escA(it.title) + '</div>' +
            '<div class="p"><s>' + rub(it.price) + '</s> <b>0 ₽</b></div></div>';
        }).join('') + '</div>' +
        (gi ? '<div class="lbbf-gok">✓ Подарок добавлен — придёт в одном письме с заказом<a data-x>убрать</a></div>' : '');
    }
    html += '<input type="hidden" name="' + CFG.field + '" value="' +
      (gi ? escA(gi.title + ' — ' + rub(gi.price) + ' (' + gi.sku + ')') : '') + '"' + (gi ? '' : ' disabled') + '>';
    box.innerHTML = html;
    box.setAttribute('data-chip', G.chip);
    row = box.querySelector('.lbbf-grow');
    if (row && keep) row.scrollLeft = keep;
  }

  /* ---------- условия акции ---------- */
  function openTerms() {
    var m = document.getElementById('lbbf-terms');
    if (!m) {
      m = document.createElement('div');
      m.id = 'lbbf-terms';
      m.innerHTML = '<div class="w" role="dialog" aria-label="Условия акции"><span class="x" data-close>×</span>' +
        '<div class="h"><small>ЧЁРНАЯ ПЯТНИЦА 11.11</small><b>Условия акции 1+1<em>=3</em></b></div><ol>' +
        '<li>Акция действует со 2 по 12 ноября 2026 года включительно, до 23:59 по московскому времени.</li>' +
        '<li>Положите в корзину 2 разных материала из акции — третий выберите в подарок прямо в корзине перед оплатой. Один подарок на заказ.</li>' +
        '<li>В подарок можно выбрать любой материал сайта, который стоит не дороже суммы материалов из акции в заказе.</li>' +
        '<li>Не участвуют в акции и не выдаются в подарок: «461 проект WeDo 2.0», «272 проекта Spike Prime», «163 проекта EV3», «130 проектов 9686», «53 проекта WeDo 2.0 + Scratch 3.0».</li>' +
        '<li>Участвуют в покупке, но не выдаются в подарок: «Учебная программа WeDo 2.0 — все 3 части», «Курс LEGO SPIKE Essential — все 4 части», модули «1-й и 2-й уровень», «Комплект учебных материалов LEGO EV3 + LEGO WeDo 2.0» и «Всё для увлекательных занятий по LEGO WeDo 2.0».</li>' +
        '<li>Ссылка на подарок приходит в одном письме с заказом сразу после оплаты.</li></ol>' +
        '<div class="f">Организатор акции — продавец, указанный в <a href="/offer" target="_blank">договоре-оферте</a>. ' +
        'Вопросы: <a href="mailto:legobotru@yandex.ru">legobotru@yandex.ru</a></div></div>';
      m.addEventListener('click', function (e) {
        if (e.target === m || e.target.hasAttribute('data-close')) m.style.display = 'none';
      });
      document.body.appendChild(m);
    }
    m.style.display = 'flex';
  }

  /* ---------- запуск ---------- */
  function boot() {
    var s = document.createElement('style'); s.id = 'lbbf-css'; s.textContent = css; document.head.appendChild(s);
    document.addEventListener('click', function (e) {
      if (e.target.closest && e.target.closest('[data-lbbf-terms]')) { e.preventDefault(); e.stopPropagation(); openTerms(); }
    }, true);
    loadCatalog().then(function (items) {
      if (!items || !items.length) return;
      if (store.get('lbbf_closed') !== new Date().toDateString()) buildCard(items);
      setInterval(function () { renderGift(items); }, 700);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
