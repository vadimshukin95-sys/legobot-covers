/* LEGObot: кнопка «ИИ и инфобез» в шапке сайта (блок T2083), перед «Среда WeDo». 03.11.2026.
   Ведёт на страницу курса /ai-infobez. Откат: убрать строку подключения этого файла из «HTML-кода в head» и опубликовать все страницы. */
(function(){
  if (window.__lbAiBtn) return; window.__lbAiBtn = 1;
  var HREF = '/ai-infobez', TEXT = 'ИИ и инфобез';
  /* специфичность выше общего правила сайта для кнопок шапки (#allrecords [data-record-type="2083"] a.t-btn.t-btnflex_sm:not(.lb-wedobtn)) */
  var B = '#allrecords [data-record-type="2083"] a.t-btn.lb-aibtn.lb-aibtn.lb-aibtn';
  /* на ноутбуках 980–1439 px третья кнопка переносит меню на вторую строку — там её не показываем (в мобильном меню и от 1440 px — показываем) */
  var HIDE = '@media (min-width:980px) and (max-width:1439px){#allrecords [data-record-type="2083"] .lb-ai-box{display:none!important}}';
  var css =
    B + '{position:relative!important;overflow:hidden!important;color:#fff!important;border:0!important;' +
      'background:linear-gradient(110deg,#6D28D9,#06B6D4,#7C3AED,#22D3EE,#6D28D9)!important;background-size:300% 300%!important;' +
      'box-shadow:0 4px 14px rgba(109,40,217,.38)!important;animation:lbAiFlow 5s ease infinite}' +
    B + ':after{content:"";position:absolute;top:0;left:0;width:40%;height:100%;pointer-events:none;' +
      'background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.55),rgba(255,255,255,0));animation:lbAiShine 3.2s ease-in-out infinite}' +
    B + ':hover{transform:translateY(-1px);box-shadow:0 6px 18px rgba(109,40,217,.5)!important}' +
    B + ' .lb-ai-ico{display:inline-block;width:14px;height:16px;margin-right:7px;vertical-align:-2px;flex:none;animation:lbAiPulse 1.6s ease-in-out infinite}' +
    '@keyframes lbAiFlow{0%{background-position:0 50%}50%{background-position:100% 50%}100%{background-position:0 50%}}' +
    '@keyframes lbAiShine{0%,55%{transform:translateX(-120%) skewX(-20deg)}100%{transform:translateX(280%) skewX(-20deg)}}' +
    '@keyframes lbAiPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.22)}}' +
    '@media (prefers-reduced-motion:reduce){' + B + ',' + B + ':after,' + B + ' .lb-ai-ico{animation:none}}' + HIDE;
  var ICO = '<svg class="lb-ai-ico" viewBox="0 0 24 28" aria-hidden="true"><path d="M12 1.5 2.5 5.3v7.6c0 6.2 4 11 9.5 13.4 5.5-2.4 9.5-7.2 9.5-13.4V5.3L12 1.5z" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round"/><path d="m7.6 14 3.1 3.1 5.8-6.2" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  function style(){
    if (document.getElementById('lb-aibtn-css')) return;
    var s = document.createElement('style'); s.id = 'lb-aibtn-css'; s.textContent = css;
    (document.head || document.documentElement).appendChild(s);
  }
  function add(){
    var wraps = document.querySelectorAll('.t-menu-base__buttons');
    if (!wraps.length) return false;
    style();
    var done = false;
    for (var i = 0; i < wraps.length; i++){
      var w = wraps[i];
      if (w.querySelector('.lb-aibtn')) { done = true; continue; }
      var wedo = w.querySelector('.lb-wedo-box');
      var boxes = w.querySelectorAll('.t-menu-base__button:not(.lb-wedo-box):not(.lb-ai-box)');
      var src = boxes[boxes.length - 1];
      if (!src) continue;
      var clone = src.cloneNode(true);
      clone.className += ' lb-ai-box';
      var a = clone.querySelector('a');
      if (!a) continue;
      a.className = (a.className || '').replace(/\s*lb-(free|wedo)btn/g, '') + ' lb-aibtn';
      a.setAttribute('href', HREF);
      a.removeAttribute('data-tooltip-hook');
      a.removeAttribute('style');
      a.removeAttribute('target');
      var txt = a.querySelector('.t-btnflex__text');
      if (txt) { txt.innerHTML = ICO + TEXT; [].forEach.call(a.children, function(c){ if (c !== txt && !c.contains(txt)) c.style.display = 'none'; }); }
      else a.innerHTML = ICO + TEXT;
      w.insertBefore(clone, wedo || src);
      done = true;
    }
    return done;
  }
  var n = 0, t = setInterval(function(){ n++; if ((add() && n > 3) || n > 40) clearInterval(t); }, 300);
  if (document.readyState !== 'loading') add(); else document.addEventListener('DOMContentLoaded', add);
})();
