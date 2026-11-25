/* LEGObot: строка «Новинка: Мастерская изобретателя — часть 2» вверху всех страниц.
   Подключение: одна строка в «HTML-код для HEAD» Тильды:
   <script src="https://cdn.jsdelivr.net/gh/vadimshukin95-sys/legobot-covers@<коммит>/mi2/strip.js" defer></script>
   Откат: удалить эту строку и переопубликовать страницы (или enabled:false в файле).
   Корневой id оставлен прежним (lbSpike): на него завязаны LB-CALM (анимации замирают через 10 с)
   и LB-MOBBAR (мобильная шапка не уходит под строку). */
(function () {
  /* ===== НАСТРОЙКИ ===== */
  var P = {
    enabled: true,
    id: 'mi2',                                          // смена id снова покажет строку тем, кто её закрыл
    priceUntil: '2026-11-29T23:59:59+03:00',            // до этого момента: дата и таймер спеццены
    showUntil: '2026-12-31T23:59:59+03:00',             // после спеццены строка остаётся просто «Новинкой»; новогодняя строка заменит её
    url: 'https://legobot.ru/kompl/tproduct/4598312901-431656117803-masterskaya-izobretatelya-chast-2-kurs-w',
    sprite: 'https://cdn.jsdelivr.net/gh/vadimshukin95-sys/legobot-covers@8da947e/mi2/mi2_models.png',
    css: 'https://cdn.jsdelivr.net/gh/vadimshukin95-sys/legobot-covers@b4d8f84/mi2/strip.css',
    exclude: ['/app'],
    metrika: 89718571
  };
  /* 12 моделей в спрайте: 0 Пильщик, 1 Пугало, 2 Штангист, 3 Атлет, 4 Черепаха, 5 Вездеход,
     6 Копилка, 7 Счётчик купюр, 8 Птичка-таймер, 9 Аттракцион, 10 Тир «Фрисби», 11 Баскетбол */
  var N = 12, ORDER = [0, 7, 11, 2, 9, 4, 1, 8, 3, 10, 5, 6];
  /* ===================== */
  if (!P.enabled) return;
  var now = new Date(), END = new Date(P.showUntil), PRICE = new Date(P.priceUntil);
  if (now >= END) return;
  var path = location.pathname.replace(/\/+$/, '') || '/';
  if (P.exclude.indexOf(path) > -1) return;
  try { if (localStorage.getItem('lb_strip_closed') === P.id) return; } catch (e) {}
  var R = document.documentElement;
  R.classList.add('lbp-pre');
  R.style.setProperty('--lbs-spr', 'url(' + P.sprite + ')');
  if (P.css && !document.getElementById('lbStripCss')) {
    var l = document.createElement('link'); l.id = 'lbStripCss'; l.rel = 'stylesheet'; l.href = P.css;
    document.head.appendChild(l);
  }
  function pos(i) { return (i / (N - 1) * 100) + '% 0'; }
  function price() { return new Date() < PRICE; }
  var D = PRICE.getDate();

  var HTML = '<div class="lbs' + (price() ? ' lbs--price' : '') + '" id="lbSpike" role="region" aria-label="Новый курс: Мастерская изобретателя, часть 2">'
    + '<div class="lbs__aur"><i></i><i></i><i></i></div><div class="lbs__studs"></div><div class="lbs__bricks"><b></b><b></b><b></b><b></b><b></b><b></b></div>'
    + '<div class="lbs__in"><div class="lbs__stage" aria-hidden="true"><div class="lbs__glow"></div><div class="lbs__m lbs__m--l"><i></i></div><div class="lbs__m lbs__m--r"><i></i></div><div class="lbs__m lbs__m--c"><i></i></div><span class="lbs__new">NEW</span><span class="lbs__spark lbs__s1">✦</span><span class="lbs__spark lbs__s2">✦</span><span class="lbs__spark lbs__s3">✦</span></div>'
    + '<div class="lbs__head"><span class="lbs__kick"><span class="lbs__kn">Новинка · </span><span class="lbs__kd">WeDo 2.0 · 8–12 лет</span><span class="lbs__kmo">спеццена до ' + D + '.11</span></span>'
    + '<span class="lbs__title"><span class="lbs__tl">Мастерская изобретателя —</span><span class="lbs__ts">Мастерская изобретателя:</span> <em>часть 2</em></span>'
    + '<span class="lbs__sub lbs__tl">12 моделей, которые работают: пилят, считают купюры, бросают мяч</span></div>'
    + '<div class="lbs__chips">'
    + '<a class="lbs__chip lbs__chip--free" href="#" data-goal="free"><span class="lbs__ico" style="background-position:' + pos(7) + '"></span><span class="lbs__t"><small>Бесплатно</small>урок 8 целиком</span></a>'
    + (price() ? '<a class="lbs__chip lbs__chip--time" href="#" data-goal="price"><span class="lbs__date"><b>' + D + '</b><i>ноя</i></span><span class="lbs__t"><small>Спеццена ещё</small><span class="lbs__tm" id="lbsTm">…</span></span></a>' : '')
    + '</div>'
    + '<a class="lbs__cta" href="#" data-goal="cta"><span class="lbs__cw">Смотреть<span class="lbs__tl"> курс</span></span><span class="lbs__cm">Курс</span> <span class="lbs__ar">→</span></a></div>'
    + '<button class="lbs__x" type="button" aria-label="Закрыть">×</button></div>';

  function mount() {
    if (document.getElementById('lbSpike')) return;
    var box = document.createElement('div'); box.innerHTML = HTML;
    var el = box.firstElementChild;
    var root = document.getElementById('allrecords') || document.body;
    root.insertBefore(el, root.firstChild); R.classList.remove('lbp-pre');
    /* корзина Тильды (фиксированная иконка справа сверху) сдвигается под плашку на столько, сколько плашки видно */
    var raf = 0;
    function cart() { raf = 0; R.style.setProperty('--lbs-cart', Math.max(0, Math.round(el.getBoundingClientRect().bottom)) + 'px'); }
    function onScroll() { if (!raf) raf = requestAnimationFrame(cart); }
    function fit() { R.style.setProperty('--lbp-h', (window.innerWidth > 960 ? el.offsetHeight : 0) + 'px'); cart(); }
    function off() { R.classList.remove('lbp-on'); R.style.removeProperty('--lbp-h'); R.style.removeProperty('--lbs-cart'); window.removeEventListener('resize', fit); window.removeEventListener('scroll', onScroll); if (ro) ro.disconnect(); clearInterval(tick); clearInterval(rot); }
    function close() { el.parentNode && el.parentNode.removeChild(el); off(); }
    R.classList.add('lbp-on'); fit(); window.addEventListener('resize', fit); window.addEventListener('scroll', onScroll, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    /* высота плашки меняется, когда догружаются стили и шрифты — пересчитываем сдвиг меню и корзины */
    var ro = window.ResizeObserver ? new ResizeObserver(fit) : null; if (ro) ro.observe(el);
    [600, 1500, 3500].forEach(function (ms) { setTimeout(function () { if (el.parentNode) fit(); }, ms); });
    [].forEach.call(el.querySelectorAll('a[data-goal]'), function (a) {
      a.href = P.url;
      a.addEventListener('click', function () { try { window.ym && ym(P.metrika, 'reachGoal', 'strip_' + P.id, { el: a.getAttribute('data-goal') }); } catch (e) {} });
    });
    /* карусель моделей */
    var slots = [el.querySelector('.lbs__m--l'), el.querySelector('.lbs__m--c'), el.querySelector('.lbs__m--r')], k = 0;
    function paint() { for (var s = 0; s < 3; s++) slots[s].firstChild.style.backgroundPosition = pos(ORDER[(k + s) % N]); }
    paint();
    var still = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    var rot = still ? 0 : setInterval(function () {
      if (document.hidden) return;
      slots.forEach(function (s, i) { setTimeout(function () { s.classList.remove('is-in'); s.classList.add('is-out'); }, i * 90); });
      setTimeout(function () { k = (k + 1) % N; paint(); slots.forEach(function (s, i) { setTimeout(function () { s.classList.remove('is-out'); s.classList.add('is-in'); }, i * 110); }); }, 420);
    }, 2800);
    /* таймер спеццены; по окончании плашка и дата в надзаголовке исчезают, строка остаётся */
    var tm = document.getElementById('lbsTm');
    function z(n) { return (n < 10 ? '0' : '') + n; }
    function upd() {
      var t = new Date();
      if (t >= END) { close(); return; }
      var ms = PRICE - t;
      if (ms <= 0) {
        el.classList.remove('lbs--price');
        var c = el.querySelector('.lbs__chip--time'); c && c.parentNode.removeChild(c); tm = null; fit(); return;
      }
      if (!tm) return;
      var s = Math.floor(ms / 1000), d = Math.floor(s / 86400), h = Math.floor(s % 86400 / 3600), m = Math.floor(s % 3600 / 60);
      tm.textContent = (d ? d + ' дн ' : '') + z(h) + ':' + z(m) + ':' + z(s % 60);
    }
    upd(); var tick = setInterval(upd, 1000);
    el.querySelector('.lbs__x').onclick = function () { try { localStorage.setItem('lb_strip_closed', P.id); } catch (e) {} close(); };
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
})();
