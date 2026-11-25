# Плашка «Новинка: Мастерская изобретателя — часть 2»

Подключение — одна строка в «HTML-код для HEAD» Тильды (метка LB-MI2-STRIP):
`<script src="https://cdn.jsdelivr.net/gh/vadimshukin95-sys/legobot-covers@<коммит>/mi2/strip.js" defer></script>`

- Спеццена с таймером — до 29.11.2026, 23:59 МСК; затем плашка остаётся «Новинкой» до 31.12 (или пока её не заменит новогодняя).
- Настройки — в начале strip.js (priceUntil, showUntil, url, exclude).
- Закрытие запоминается в localStorage (lb_strip_closed = id).
- Клики — цель Метрики strip_mi2.
- Откат: удалить строку LB-MI2-STRIP из HEAD и опубликовать все страницы.
