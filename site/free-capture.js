/* LEGObot: мягкий сбор почты на /free (15.10.2026).
   По клику «Скачать бесплатно» показывает окно: подписаться и скачать или просто скачать.
   Почта уходит через форму подписки на этой же странице (#rec3897400801) — те же сервисы приёма данных.
   Окно показывается один раз в 30 дней: после подписки или «Просто скачать» следующие клики сразу открывают материалы.
   Тест без памяти: ?lbcap=1 к адресу страницы. */
(function () {
  if (!/^\/free\/?$/.test(location.pathname)) return;
  var KEY = 'lb_free_capture', DAYS = 30, FORCE = /[?&]lbcap=1/.test(location.search);

  function seen() {
    if (FORCE) return false;
    try { var t = +localStorage.getItem(KEY); return t && Date.now() - t < DAYS * 864e5; } catch (e) { return false; }
  }
  function remember() { try { localStorage.setItem(KEY, String(Date.now())); } catch (e) {} }

  var css =
    '.lbcap{position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;padding:20px;background:rgba(31,36,33,.45);font-family:Nunito,Arial,sans-serif;opacity:0;transition:opacity .2s}' +
    '.lbcap[hidden]{display:none}' +
    '.lbcap *,.lbcap *:before,.lbcap *:after{box-sizing:border-box}' +
    '.lbcap.is-open{opacity:1}' +
    '.lbcap__box{position:relative;width:100%;max-width:460px;background:#fff;border-radius:24px;box-shadow:0 30px 80px rgba(31,36,33,.3);overflow:hidden;transform:translateY(12px);transition:transform .25s}' +
    '.lbcap.is-open .lbcap__box{transform:none}' +
    '.lbcap__item{display:flex;align-items:center;gap:14px;padding:18px 66px 18px 22px;background:#f2f5ef;border-bottom:1px solid #dde3d8}' +
    '.lbcap__item img{width:56px;height:56px;border-radius:12px;object-fit:cover;flex:none;box-shadow:0 4px 12px rgba(31,36,33,.12)}' +
    '.lbcap__item b{display:block;font-size:15.5px;line-height:1.3;color:#1f2421;font-weight:800}' +
    '.lbcap__item span{display:block;font-size:13.5px;color:#5d655f;margin-top:2px}' +
    '.lbcap__x{position:absolute;top:14px;right:14px;width:36px;height:36px;border:0;border-radius:50%;background:#fff;color:#1f2421;font-size:22px;line-height:36px;cursor:pointer;box-shadow:0 2px 8px rgba(31,36,33,.12)}' +
    '.lbcap__body{padding:24px 26px 22px}' +
    '.lbcap__h{margin:0 0 8px;font-size:24px;line-height:1.15;font-weight:900;color:#1f2421;letter-spacing:-.01em}' +
    '.lbcap__p{margin:0 0 18px;font-size:16px;line-height:1.5;color:#3b423d}' +
    '.lbcap__in{display:block;width:100%;box-sizing:border-box;height:54px;padding:0 16px;border:1.5px solid #dde3d8;border-radius:12px;background:#fbfcfa;font:600 16px Nunito,Arial,sans-serif;color:#1f2421;outline:none;transition:border-color .2s,box-shadow .2s}' +
    '.lbcap__in:focus{border-color:#4bae2e;box-shadow:0 0 0 4px rgba(75,174,46,.15)}' +
    '.lbcap__in.is-err{border-color:#d93a3a}' +
    '.lbcap__err{min-height:18px;margin:6px 2px 4px;font-size:13.5px;color:#c62f2f}' +
    '.lbcap__go{display:block;width:100%;height:56px;margin:0;padding:0 20px;border:0;border-radius:999px;background:#f7a300;color:#1f2421;font:800 17px Nunito,Arial,sans-serif;cursor:pointer;box-shadow:0 8px 20px rgba(247,163,0,.28);transition:background .2s}' +
    '.lbcap__go:hover{background:#e69500}' +
    '.lbcap__skip{display:block;width:100%;margin-top:10px;padding:10px;border:0;background:none;font:800 15.5px Nunito,Arial,sans-serif;color:#2e7a1c;cursor:pointer;text-decoration:underline;text-underline-offset:3px}' +
    '.lbcap__legal{margin:8px 0 0;font-size:12.5px;line-height:1.45;color:#7a827c;text-align:center}' +
    '.lbcap__legal a{color:#5d655f}' +
    '.lbcap__go:focus-visible,.lbcap__skip:focus-visible,.lbcap__x:focus-visible{outline:3px solid #4bae2e;outline-offset:3px}' +
    '@media (max-width:560px){.lbcap{align-items:flex-end;padding:0}.lbcap__box{max-width:none;border-radius:22px 22px 0 0;transform:translateY(40px)}.lbcap__body{padding:20px 18px calc(18px + env(safe-area-inset-bottom))}.lbcap__h{font-size:22px}.lbcap__item{padding:14px 62px 14px 18px}}' +
    '@media (prefers-reduced-motion:reduce){.lbcap,.lbcap__box{transition:none}}';

  var root, current;

  function build() {
    if (root) return;
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    root = document.createElement('div');
    root.className = 'lbcap';
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');
    root.setAttribute('aria-labelledby', 'lbcap-h');
    root.hidden = true;
    root.innerHTML =
      '<div class="lbcap__box">' +
        '<button type="button" class="lbcap__x" aria-label="Закрыть">×</button>' +
        '<div class="lbcap__item"><img alt=""><div><b></b><span>Материалы откроются в новой вкладке</span></div></div>' +
        '<form class="lbcap__body" novalidate>' +
          '<h2 class="lbcap__h" id="lbcap-h">Прислать новые бесплатные уроки на почту?</h2>' +
          '<p class="lbcap__p">Первые занятия из курсов, инструкции и рабочие листы — по мере выхода. Без спама, отписаться можно в один клик.</p>' +
          '<label for="lbcap-mail" style="position:absolute;left:-9999px">Email</label>' +
          '<input class="lbcap__in" id="lbcap-mail" type="email" autocomplete="email" placeholder="Ваш email" required>' +
          '<div class="lbcap__err" aria-live="polite"></div>' +
          '<button type="submit" class="lbcap__go">Подписаться и скачать</button>' +
          '<button type="button" class="lbcap__skip">Просто скачать</button>' +
          '<p class="lbcap__legal">Нажимая «Подписаться и скачать», вы соглашаетесь с <a href="/privacy" target="_blank" rel="noopener">политикой обработки персональных данных</a></p>' +
        '</form>' +
      '</div>';
    document.body.appendChild(root);
    root.addEventListener('click', function (e) { if (e.target === root) close(); });
    root.querySelector('.lbcap__x').addEventListener('click', close);
    root.querySelector('.lbcap__skip').addEventListener('click', function () { remember(); go(); });
    root.querySelector('form').addEventListener('submit', function (e) {
      e.preventDefault();
      var inp = root.querySelector('.lbcap__in'), v = inp.value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) {
        inp.classList.add('is-err');
        root.querySelector('.lbcap__err').textContent = 'Проверьте адрес: в нём должны быть @ и домен, например name@mail.ru';
        inp.focus();
        return;
      }
      subscribe(v);
      remember();
      go();
    });
    root.querySelector('.lbcap__in').addEventListener('input', function () {
      this.classList.remove('is-err'); root.querySelector('.lbcap__err').textContent = '';
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !root.hidden) close(); });
  }

  function subscribe(email) {
    var f = document.querySelector('#rec3897400801 form') ||
            document.querySelector('form.js-form-proccess input[name="Email"]') && document.querySelector('form.js-form-proccess input[name="Email"]').form;
    if (!f) return;
    var i = f.querySelector('input[name="Email"]'), b = f.querySelector('[type="submit"], .t-submit');
    if (!i || !b) return;
    i.value = email;
    i.dispatchEvent(new Event('input', { bubbles: true }));
    b.click();
  }

  function open(card) {
    build();
    current = card;
    root.querySelector('.lbcap__item img').src = card.img || '';
    root.querySelector('.lbcap__item img').style.display = card.img ? '' : 'none';
    root.querySelector('.lbcap__item b').textContent = card.name || 'Бесплатный материал';
    root.hidden = false;
    document.documentElement.style.overflow = 'hidden';
    requestAnimationFrame(function () { root.classList.add('is-open'); });
    setTimeout(function () { var i = root.querySelector('.lbcap__in'); if (i && window.innerWidth > 560) i.focus(); }, 60);
  }

  function close() {
    if (!root) return;
    root.classList.remove('is-open');
    root.hidden = true;
    document.documentElement.style.overflow = '';
    if (current && current.btn) current.btn.focus();
  }

  function go() {
    var href = current && current.href;
    close();
    if (href) window.open(href, '_blank', 'noopener');
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a.lb-free__btn');
    if (!a || seen() || e.ctrlKey || e.metaKey || e.shiftKey) return;
    e.preventDefault();
    var c = a.closest('.lb-free__card');
    var img = c && c.querySelector('img');
    var nm = c && c.querySelector('.lb-free__name');
    open({ href: a.href, btn: a, img: img ? (img.currentSrc || img.src) : '', name: nm ? nm.textContent.trim() : '' });
  }, true);
})();
