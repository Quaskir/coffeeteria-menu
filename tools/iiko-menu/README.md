# Меню сайта из iiko (Menu, шаг 1 — 27.10.2026)

Названия и цены — из кассы (iiko), фото/описания/переводы — свои. Пока нет ядра Menu в Zadachi, пересборка вручную:

1. `node tools/iiko-menu/pull-menu.mjs` — продажи Coffeeteria за 30 дней → `coffeeteria-iiko.json` (логин iiko берётся из `.env` Zadachi; поменять даты в файле).
2. `python3 tools/iiko-menu/build.py` — собирает `menu_iiko.js` и `out.json` (фото, греческие метки, исправленные опечатки iiko).
3. Вставить `menu_iiko.js` вместо `const menuData = [...]` в `index-new.html`.

Таблицы: `build_common.py` — какие группы iiko в какие разделы сайта, что скрыто (кальяны, комплименты, ОПТ, допы), опечатки iiko;
`build_names.py` — вид названий и переводы новых позиций (ключ — название как в iiko).
