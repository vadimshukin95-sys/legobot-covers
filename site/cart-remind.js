/* LB-CART-REMIND v2 — напоминание о брошенной корзине для legobot.ru.
   Перенесено из HEAD-кода Tilda 28.10.2026, подключается в HEAD тегом <script defer>.
   На страницах без корзины кнопка ведёт в карточку товара и открывает корзину там (?lbcr=open).
   Цели Метрики: cart_reminder_show, cart_reminder_click. Проверка: ?cartremind=1 */
(function(){var s=document.createElement('style');s.id='lbcr-css';s.textContent="#lbcr{position:fixed;left:16px;bottom:16px;z-index:99990;width:360px;max-width:calc(100% - 20px);background:#fff;border-radius:16px;box-shadow:0 8px 28px rgba(0,0,0,.18);padding:16px;font-family:Nunito,Arial,sans-serif;color:#1f2421;transform:translateY(24px);opacity:0;transition:transform .3s ease,opacity .3s ease}\n#lbcr.lbcr-on{transform:none;opacity:1}\n#lbcr .lbcr-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:12px}\n#lbcr .lbcr-ttl{font-weight:800;font-size:16px;line-height:1.25}\n#lbcr .lbcr-x{background:none;border:0;padding:0 2px;font-size:22px;line-height:1;color:#9aa09c;cursor:pointer}\n#lbcr .lbcr-it{display:flex;gap:10px;align-items:center;margin-bottom:10px;text-decoration:none;color:inherit}\n#lbcr .lbcr-img{width:52px;height:52px;border-radius:10px;object-fit:cover;flex:none;background:#eef3e8}\n#lbcr .lbcr-n{font-size:14px;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}\n#lbcr .lbcr-p{font-weight:700;font-size:14px;margin-top:2px}\n#lbcr .lbcr-more{font-size:13px;color:#6b716d;margin:-2px 0 10px}\n#lbcr .lbcr-row{display:flex;align-items:center;gap:8px;margin-top:4px}\n#lbcr .lbcr-go{background:#f59f00;color:#fff;border:0;border-radius:40px;padding:11px 18px;font:700 15px Nunito,Arial,sans-serif;cursor:pointer;white-space:nowrap}\n#lbcr .lbcr-go:hover{background:#e08f00}\n#lbcr .lbcr-no{background:none;border:0;color:#6b716d;font:600 14px Nunito,Arial,sans-serif;padding:10px 8px;cursor:pointer}\n@media (max-width:640px){#lbcr{left:10px;right:10px;bottom:80px;width:auto;max-width:none}}";(document.head||document.documentElement).appendChild(s);})();
(function(){
var MIN_AGE=30*60, HIDE_DAYS=3, YM=89718571;
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);if(v===null)localStorage.removeItem(k);else localStorage.setItem(k,v);}catch(e){return null;}}
function goal(n){try{if(window.ym)ym(YM,'reachGoal',n);}catch(e){}}
function money(n){return Number(n).toLocaleString('ru-RU')+' р.';}
function word(n){var a=n%10,b=n%100;if(a==1&&b!=11)return 'материал';if(a>=2&&a<=4&&(b<12||b>14))return 'материала';return 'материалов';}
function hasCart(){return typeof window.tcart__openCart=='function'&&!!document.querySelector('.t706');}
if(/[?&]lbcr=open/.test(location.search)){
try{sessionStorage.setItem('lbcr_s','1');history.replaceState(null,'',location.pathname+location.search.replace(/([?&])lbcr=open&?/,'$1').replace(/[?&]$/,'')+location.hash);}catch(e){}
var tries=0,iv=setInterval(function(){tries++;if(hasCart()){clearInterval(iv);setTimeout(function(){window.tcart__openCart();},300);}else if(tries>60)clearInterval(iv);},250);
return;
}
var force=/[?&]cartremind=1/.test(location.search);
var newVisit=false;
try{newVisit=!sessionStorage.getItem('lbcr_s');sessionStorage.setItem('lbcr_s','1');}catch(e){}
if(!force){
if(!newVisit)return;
if(/^\/app/.test(location.pathname))return;
var h=Number(ls('lbcr_hide')||0);
if(h&&Date.now()-h<HIDE_DAYS*864e5)return;
}
function show(){
var c;try{c=JSON.parse(ls('tcart')||'null');}catch(e){c=null;}
if(!c||!c.products||!c.products.length)return;
var last=Number(c.updated||0);
c.products.forEach(function(p){if(Number(p.ts)>last)last=Number(p.ts);});
if(!force&&last&&(Date.now()/1000-last)<MIN_AGE)return;
if(document.getElementById('lbcr'))return;
var ps=c.products, n=0, sum=0;
ps.forEach(function(p){n+=Number(p.quantity||1);sum+=Number(p.amount||p.price||0);});
var box=document.createElement('div');box.id='lbcr';box.setAttribute('role','status');
var top=document.createElement('div');top.className='lbcr-top';
var ttl=document.createElement('div');ttl.className='lbcr-ttl';
ttl.textContent=ps.length==1?'Вы не закончили заказ':'В корзине '+n+' '+word(n)+' на '+money(sum);
var x=document.createElement('button');x.className='lbcr-x';x.type='button';x.setAttribute('aria-label','Закрыть');x.textContent='×';
top.appendChild(ttl);top.appendChild(x);box.appendChild(top);
ps.slice(0,2).forEach(function(p){
var it=document.createElement(p.url?'a':'div');it.className='lbcr-it';if(p.url)it.href=p.url;
var im=document.createElement('img');im.className='lbcr-img';im.alt='';im.loading='lazy';if(p.img)im.src=p.img;
var t=document.createElement('div');var nm=document.createElement('div');nm.className='lbcr-n';nm.textContent=p.name||'';
var pr=document.createElement('div');pr.className='lbcr-p';pr.textContent=money(p.amount||p.price||0);
t.appendChild(nm);t.appendChild(pr);it.appendChild(im);it.appendChild(t);box.appendChild(it);
});
if(ps.length>2){var m=document.createElement('div');m.className='lbcr-more';m.textContent='и ещё '+(ps.length-2);box.appendChild(m);}
var row=document.createElement('div');row.className='lbcr-row';
var go=document.createElement('button');go.className='lbcr-go';go.type='button';go.textContent='Перейти к оплате';
var no=document.createElement('button');no.className='lbcr-no';no.type='button';no.textContent='Не сейчас';
row.appendChild(go);row.appendChild(no);box.appendChild(row);
function close(){ls('lbcr_hide',String(Date.now()));box.classList.remove('lbcr-on');setTimeout(function(){box.remove();},300);}
x.onclick=close;no.onclick=close;
go.onclick=function(){goal('cart_reminder_click');box.remove();
if(hasCart()){window.tcart__openCart();return;}
var u=ps[0].url||'https://legobot.ru/';
setTimeout(function(){location.href=u+(u.indexOf('?')>-1?'&':'?')+'lbcr=open';},150);};
document.body.appendChild(box);
setTimeout(function(){box.classList.add('lbcr-on');},40);
goal('cart_reminder_show');
}
function start(){setTimeout(show,2500);}
if(document.readyState=='complete')start();else window.addEventListener('load',start);
})();
