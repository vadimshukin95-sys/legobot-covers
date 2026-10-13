(function(){
  var PROMO={enabled:true, deadline:'2026-11-01T00:00:00+03:00', url:'https://legobot.ru/wedo-2-halloween', exclude:['/app']};
  if(!PROMO.enabled) return; var DEADLINE=new Date(PROMO.deadline); if(new Date()>=DEADLINE) return;
  var path=location.pathname.replace(/\/+$/,'')||'/'; if(PROMO.exclude.indexOf(path)>-1) return;
  function lbhwDays(){var e=new Date('2026-10-31T23:59:59+03:00'),n=new Date();var d=Math.floor((e-n)/864e5);return d<0?0:d;}function lbhwW(n){var a=n%10,b=n%100;return(a===1&&b!==11)?'день':(a>=2&&a<=4&&(b<12||b>14))?'дня':'дней';}
  var HTML="<div class=\"lbhw\" id=\"lbHw\" role=\"region\" aria-label=\"Мастер-классы на Хэллоуин\"><a class=\"lbhw__in\" id=\"lbHwLink\" href=\"#\"><svg class=\"lbhw__bat\" style=\"left:300px;top:6px;width:44px\" viewBox=\"0 0 30 14\" aria-hidden=\"true\"><path d=\"M0 10 Q6 0 11 7 Q13 2 15 6 Q17 2 19 7 Q24 0 30 10 Q24 8 21 12 Q18 9 15 14 Q12 9 9 12 Q6 8 0 10Z\"/></svg><svg class=\"lbhw__bat\" style=\"left:720px;top:46px;width:30px\" viewBox=\"0 0 30 14\" aria-hidden=\"true\"><path d=\"M0 10 Q6 0 11 7 Q13 2 15 6 Q17 2 19 7 Q24 0 30 10 Q24 8 21 12 Q18 9 15 14 Q12 9 9 12 Q6 8 0 10Z\"/></svg><span class=\"lbhw__moon\" aria-hidden=\"true\"></span><span class=\"lbhw__models\" aria-hidden=\"true\"><img src=\"https://cdn.jsdelivr.net/gh/vadimshukin95-sys/legobot-covers@f81ce30/halloween/models/m_wedo.png\" alt=\"\"><img src=\"https://cdn.jsdelivr.net/gh/vadimshukin95-sys/legobot-covers@f81ce30/halloween/models/m_spike.png\" alt=\"\"><img src=\"https://cdn.jsdelivr.net/gh/vadimshukin95-sys/legobot-covers@f81ce30/halloween/models/m_ess.png\" alt=\"\"><img src=\"https://cdn.jsdelivr.net/gh/vadimshukin95-sys/legobot-covers@f81ce30/halloween/models/m_ev3.png\" alt=\"\"></span><span class=\"lbhw__t\"><b>Сладость или гадость!</b><span>Мастер-классы на Хэллоуин · WeDo 2.0 · SPIKE · EV3</span></span><span class=\"lbhw__d\" id=\"lbHwD\">до Хэллоуина<strong>18 дней</strong></span><span class=\"lbhw__cta\">Смотреть</span></a><button class=\"lbhw__x\" id=\"lbHwX\" type=\"button\" aria-label=\"Закрыть\">×</button></div>";
  function mount(){
    if(document.getElementById('lbHw')) return; var old=document.getElementById('lbSpike'); if(old) old.parentNode.removeChild(old);
    var box=document.createElement('div'); box.innerHTML=HTML; var el=box.firstElementChild;
    var root=document.getElementById('allrecords')||document.body; root.insertBefore(el, root.firstChild);
    var R=document.documentElement; function fit(){ R.style.setProperty('--lbp-h',(window.innerWidth>960?el.offsetHeight:0)+'px'); R.style.setProperty('--lbp-hm',el.offsetHeight+'px'); }
    function off(){ R.classList.remove('lbp-on'); R.style.removeProperty('--lbp-h'); R.style.removeProperty('--lbp-hm'); window.removeEventListener('resize',fit); }
    R.classList.add('lbp-on'); fit(); window.addEventListener('resize',fit); window.addEventListener('load',fit); setTimeout(fit,1500);
    document.getElementById('lbHwLink').href=PROMO.url;
    var d=lbhwDays(), dd=document.getElementById('lbHwD'); if(dd) dd.innerHTML=d?('до Хэллоуина<strong>'+d+' '+lbhwW(d)+'</strong>'):'Хэллоуин<strong>сегодня!</strong>';
    document.getElementById('lbHwX').onclick=function(){ el.parentNode.removeChild(el); off(); };
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',mount); else mount();
})();
