/* LEGObot: доп. скрипт сайта (15.10.2026).
   1) Ссылки на страницу «Оплата по счёту для организаций» (/dlya-organizatsiy):
      строка под кнопкой «В корзину» в карточках товаров и ссылка в подвале.
   2) Цель VK Рекламы «lb_order» (пиксель 3803867): оформление заказа в корзине Тильды.
   Подключается одной строкой в head Тильды. */
(function () {
  var URL = '/dlya-organizatsiy';
  var HERE = location.pathname.replace(/\/$/, '') === URL;
  var ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 21v-6h6v6"/></svg>';

  function css() {
    if (document.getElementById('lb-org-css')) return;
    var s = document.createElement('style');
    s.id = 'lb-org-css';
    s.textContent =
      '.lb-orgnote-wrap{margin-top:14px}' +
      '.lb-orgnote{display:inline-flex;align-items:center;gap:8px;font:700 15px/1.35 Nunito,Arial,sans-serif;color:#2e7a1c!important;text-decoration:none!important;border-bottom:1.5px solid rgba(46,122,28,.35);padding-bottom:2px}' +
      '.lb-orgnote:hover{border-bottom-color:#2e7a1c}' +
      '.lb-orgnote svg{width:17px;height:17px;flex:none}';
    (document.head || document.documentElement).appendChild(s);
  }

  function product() {
    var ws = document.querySelectorAll('.t-catalog__prod-popup__btn-wrapper, .t-store__prod-popup__btn-wrapper');
    for (var i = 0; i < ws.length; i++) {
      var w = ws[i], n = w.nextElementSibling;
      if (n && n.classList.contains('lb-orgnote-wrap')) continue;
      var d = document.createElement('div');
      d.className = 'lb-orgnote-wrap';
      d.innerHTML = '<a class="lb-orgnote" href="' + URL + '">' + ICON + 'Оплата по счёту для школ и организаций</a>';
      w.parentNode.insertBefore(d, w.nextSibling);
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
    try { css(); product(); footer(); hookOrder(); } catch (e) {}
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
  var timer;
  new MutationObserver(function () { clearTimeout(timer); timer = setTimeout(run, 200); })
    .observe(document.documentElement, { childList: true, subtree: true });
  var tries = 0, iv = setInterval(function () { if (hookOrder() || ++tries > 60) clearInterval(iv); }, 500);
})();
