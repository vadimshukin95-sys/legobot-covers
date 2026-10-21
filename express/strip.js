/* LB EXPRESS STRIP — верхняя плашка «−30% по промокоду ЭКСПРЕСС», до 26.10.2026 23:59 мск.
   Подключение: strip.css + этот файл в «HTML-код для вставки внутрь head» проекта Tilda. После срока плашка не показывается сама. */
(function(){
  var P={
    deadline:'2026-10-26T23:59:59+03:00',
    code:'ЭКСПРЕСС',
    url:'https://legobot.ru/#rec2345240381',
    cards:'https://cdn.jsdelivr.net/gh/vadimshukin95-sys/legobot-covers@70eb42d/express/cards/',
    deck:['WD2-01','SPP-01','EV3-01','L96-01','SCR-001','PRG-001'],
    exclude:['/app']
  };
  var END=new Date(P.deadline);
  if(new Date()>=END) return;
  var path=location.pathname.replace(/\/+$/,'')||'/';
  if(!window.LBX_HOSTS && P.exclude.indexOf(path)>-1) return;
  try{ if(!window.LBX_HOSTS && sessionStorage.getItem('lbx_closed')==='1') return; }catch(e){}

  /* шрифт Unbounded только для знаков «−30%» — несколько килобайт */
  if(!document.getElementById('lbxFont')){
    var l=document.createElement('link'); l.id='lbxFont'; l.rel='stylesheet';
    l.href='https://fonts.googleapis.com/css2?family=Unbounded:wght@900&display=swap&text='+encodeURIComponent('−30%');
    (document.head||document.documentElement).appendChild(l);
  }

  function src(n){ return window.LBX_IMGS ? window.LBX_IMGS[n] : P.cards+n+'.jpg'; }
  var I_COPY='<svg class="i-copy" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5.5" y="5.5" width="8" height="8" rx="1.5"/><path d="M10.5 5.5V3.5A1.5 1.5 0 0 0 9 2H3.5A1.5 1.5 0 0 0 2 3.5V9a1.5 1.5 0 0 0 1.5 1.5h2"/></svg>';
  var I_OK='<svg class="i-ok" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3.2 3L13 4.5"/></svg>';
  var I_X='<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M2 2l8 8M10 2l-8 8"/></svg>';
  var deck=''; for(var i=0;i<P.deck.length;i++) deck+='<span class="lbx__card"><img src="'+src(P.deck[i])+'" alt="" loading="lazy" decoding="async"></span>';

  var HTML='<div class="lbx" id="lbExpress" role="region" aria-label="Скидка 30% на весь каталог по промокоду '+P.code+'"><div class="lbx__in">'+
    '<span class="lbx__big" data-t="−30%" aria-hidden="true"><span>−30%</span></span>'+
    '<span class="lbx__t"><span class="lbx__h"><b>Экспресс-скидка</b><span class="lbx__pill">на весь каталог</span></span>'+
      '<span class="lbx__s"><span class="d">промокод</span><button class="lbx__code" type="button" aria-label="Скопировать промокод '+P.code+'"><span data-lbl>'+P.code+'</span>'+I_COPY+I_OK+'</button>'+
      '<span class="dl d">· до 26 октября</span><span class="ds">· до 26.10</span></span></span>'+
    '<span class="lbx__deck" aria-hidden="true">'+deck+'</span>'+
    '<span class="lbx__cd" role="timer" aria-label="До конца акции"><i><b data-k="d">0</b><em>дн</em></i><i><b data-k="h">00</b><em>час</em></i><i><b data-k="m">00</b><em>мин</em></i><i><b data-k="s">00</b><em>сек</em></i></span>'+
    '<a class="lbx__cta" href="'+P.url+'"><span class="d">В каталог</span><span class="m">Каталог</span></a>'+
    '</div><button class="lbx__x" type="button" aria-label="Закрыть">'+I_X+'</button></div>';

  function pad(n){return (n<10?'0':'')+n;}
  var still=false; try{ still=window.matchMedia('(prefers-reduced-motion: reduce)').matches; }catch(_){}

  function setup(el, onClose){
    /* таймер */
    var keys=el.querySelectorAll('[data-k]');
    function tick(){
      var ms=END-new Date(); if(ms<=0){ onClose(); return false; }
      var v={d:String(Math.floor(ms/864e5)),h:pad(Math.floor(ms/36e5)%24),m:pad(Math.floor(ms/6e4)%60),s:pad(Math.floor(ms/1e3)%60)};
      for(var i=0;i<keys.length;i++){var k=keys[i],nv=v[k.getAttribute('data-k')]; if(k.textContent!==nv){k.textContent=nv;k.classList.remove('tick');void k.offsetWidth;k.classList.add('tick');}}
      return true;
    }
    if(tick()){ var t=setInterval(function(){ if(!tick()) clearInterval(t); },1000); }

    /* колода карточек: три видны, раз в 3 секунды сдвигаются на одну */
    var cards=el.querySelectorAll('.lbx__card'), n=cards.length, k=0;
    function lay(){ for(var i=0;i<n;i++){ var p=(i-k+n)%n; cards[i].setAttribute('data-p', p<3?String(p):(p===n-1?'out':'')); } }
    if(still){ lay(); }
    else{
      setTimeout(function(){ lay(); },350);
      setInterval(function(){ if(document.hidden) return; k=(k+1)%n; lay(); },3000);
    }

    /* копирование кода */
    var code=el.querySelector('.lbx__code'), lbl=code.querySelector('[data-lbl]');
    code.addEventListener('click',function(e){
      e.preventDefault(); e.stopPropagation();
      function done(){ code.setAttribute('data-done',''); lbl.textContent='Скопирован'; clearTimeout(code._t); code._t=setTimeout(function(){code.removeAttribute('data-done');lbl.textContent=P.code;},1800); }
      function fallback(){ try{var ta=document.createElement('textarea');ta.value=P.code;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta);}catch(_){} done(); }
      try{ navigator.clipboard.writeText(P.code).then(done,fallback); }catch(_){ fallback(); }
      fillCart();
    });
    el.querySelector('.lbx__x').addEventListener('click',function(e){ e.stopPropagation(); try{sessionStorage.setItem('lbx_closed','1');}catch(_){} onClose(); });
    el.addEventListener('click',function(e){ if(e.target.closest('a,button')) return; location.href=P.url; });
  }
  /* подставить код в поле промокода корзины Tilda, если оно пустое */
  function fillCart(){
    var inp=document.querySelector('.t-inputpromocode'); if(!inp||inp.value) return;
    inp.value=P.code; try{inp.dispatchEvent(new Event('input',{bubbles:true}));}catch(_){}
  }

  /* предпросмотр: отрисовать в заданные контейнеры */
  if(window.LBX_HOSTS){
    window.LBX_HOSTS.forEach(function(h){ h.innerHTML=HTML; var el=h.firstElementChild; el.style.position='relative'; setup(el,function(){ el.style.visibility='hidden'; setTimeout(function(){el.style.visibility='';},1500); }); });
    return;
  }

  function mount(){
    if(document.getElementById('lbExpress')) return;
    ['lbHw','lbSpike'].forEach(function(id){ var o=document.getElementById(id); if(o) o.parentNode.removeChild(o); });
    var box=document.createElement('div'); box.innerHTML=HTML; var el=box.firstElementChild;
    var root=document.getElementById('allrecords')||document.body; root.insertBefore(el, root.firstChild);
    var R=document.documentElement;
    function fit(){ R.style.setProperty('--lbp-h',(window.innerWidth>960?el.offsetHeight:0)+'px'); R.style.setProperty('--lbp-hm',el.offsetHeight+'px'); var mm=document.querySelector('.tmenu-mobile_positionfixed'); if(mm&&mm.offsetHeight) R.style.setProperty('--lbp-mm',mm.offsetHeight+'px'); }
    function off(){ if(el.parentNode) el.parentNode.removeChild(el); R.classList.remove('lbp-on'); ['--lbp-h','--lbp-hm','--lbp-mm'].forEach(function(v){R.style.removeProperty(v);}); window.removeEventListener('resize',fit); }
    R.classList.add('lbp-on'); fit(); window.addEventListener('resize',fit); window.addEventListener('load',fit); setTimeout(fit,1500);
    setup(el, off);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',mount); else mount();
})();
