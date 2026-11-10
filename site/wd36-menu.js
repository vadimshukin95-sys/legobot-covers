/* LEGObot: пункт меню «Курс WeDo» (new) в шапке сайта (блок T2083), после «Программирования». 10.11.2026.
   Ведёт на страницу курса /inzhenernaya-masterskaya. Откат: убрать строку подключения этого файла из «HTML-кода в head» и опубликовать все страницы. */
(function(){
  if (window.__lbWd36Menu) return; window.__lbWd36Menu = 1;
  var HREF = '/inzhenernaya-masterskaya', TEXT = 'Курс WeDo';
  /* на 980–1599 px пунктам меню не хватает места: сужаем промежуток 30 → 14 px, метку new прячем до 1535 px */
  var css = '#allrecords .lb-wd36-li .lb-new{display:inline-block;margin-left:5px;padding:0 6px;border-radius:999px;font-size:10px;line-height:15px;font-weight:800;color:#fff;' +
    'background:linear-gradient(120deg,#1AA3FF,#20C997);vertical-align:3px;letter-spacing:.3px;text-transform:lowercase}' +
    '@media (min-width:980px) and (max-width:1599px){#allrecords .t-menu-base__list{column-gap:14px!important}}' +
    '@media (min-width:980px) and (max-width:1535px){#allrecords .lb-wd36-li .lb-new{display:none!important}}';
  function style(){
    if (document.getElementById('lb-wd36-css')) return;
    var s = document.createElement('style'); s.id = 'lb-wd36-css'; s.textContent = css;
    (document.head || document.documentElement).appendChild(s);
  }
  function txt(li){ var a = li.querySelector('a'); return a ? (a.textContent || '').trim() : ''; }
  function add(){
    var lists = document.querySelectorAll('.t-menu-base__list');
    if (!lists.length) return false;
    style();
    var done = false;
    for (var i = 0; i < lists.length; i++){
      var ul = lists[i];
      if (ul.querySelector('.lb-wd36-li')) { done = true; continue; }
      var items = [].slice.call(ul.children).filter(function(x){ return x.tagName === 'LI'; });
      if (!items.length) continue;
      var after = null, tpl = null, byText = {};
      items.forEach(function(li){
        var t = txt(li); byText[t] = li;
        if (t === 'Программирование') after = li;
      });
      /* образец — видимый простой пункт без подменю («Каталог» скрыт на ПК, его не берём) */
      ['Статьи', 'Контакты', 'Почему мы', 'Программирование'].some(function(k){
        var x = byText[k]; if (x && !x.querySelector('ul,.t-menu__submenu,[class*="submenu"]')) { tpl = x; return true; } return false;
      });
      if (!tpl) continue;
      var li = tpl.cloneNode(true);
      li.className = (li.className || '').replace(/\s*lb-[\w-]+-li/g, '') + ' lb-wd36-li';
      var a = li.querySelector('a');
      if (!a) continue;
      a.setAttribute('href', HREF);
      a.removeAttribute('target');
      a.classList.remove('t-active');
      a.innerHTML = TEXT + '<span class="lb-new">new</span>';
      if (location.pathname.replace(/\/$/, '') === HREF) a.classList.add('t-active');
      if (after && after.nextSibling) ul.insertBefore(li, after.nextSibling);
      else if (after) ul.appendChild(li);
      else ul.insertBefore(li, items[0]);
      done = true;
    }
    return done;
  }
  var n = 0, t = setInterval(function(){ n++; if ((add() && n > 3) || n > 40) clearInterval(t); }, 300);
  if (document.readyState !== 'loading') add(); else document.addEventListener('DOMContentLoaded', add);
})();
