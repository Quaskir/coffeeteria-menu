// Позиции Coffeeteria, проданные за 30 дней: группа, категория, цена в меню на последний день продажи, количество.
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
const env = Object.fromEntries(readFileSync('/Users/damir/Desktop/zadachi/.env', 'utf8').split('\n').filter(l => /^IIKO_/.test(l)).map(l => { const i = l.indexOf('='); return [l.slice(0, i), l.slice(i + 1).trim().replace(/^"|"$/g, '')]; }));
const url = env.IIKO_SERVER_URL.replace(/\/+$/, '');
const key = (await (await fetch(`${url}/resto/api/auth?login=${encodeURIComponent(env.IIKO_LOGIN)}&pass=${createHash('sha1').update(env.IIKO_PASSWORD).digest('hex')}`)).text()).trim();
try {
  const body = { reportType: 'SALES', buildSummary: false, groupByRowFields: ['DishCategory', 'DishGroup', 'DishName', 'OpenDate.Typed'], groupByColFields: [], aggregateFields: ['DishAmountInt', 'DishSumInt'],
    filters: { 'OpenDate.Typed': { filterType: 'DateRange', periodType: 'CUSTOM', from: '2026-09-27', to: '2026-10-27', includeLow: true, includeHigh: false },
      Department: { filterType: 'IncludeValues', values: ['Coffeeteria'] }, OrderDeleted: { filterType: 'IncludeValues', values: ['NOT_DELETED'] }, DeletedWithWriteoff: { filterType: 'IncludeValues', values: ['NOT_DELETED'] } } };
  const rows = (await (await fetch(`${url}/resto/api/v2/reports/olap?key=${key}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })).json()).data;
  const map = new Map();
  for (const r of rows) {
    if (!(r.DishAmountInt > 0)) continue;
    const k = r.DishName;
    const e = map.get(k) ?? { name: r.DishName, category: r.DishCategory, group: r.DishGroup, qty: 0, lastDate: '', price: 0 };
    e.qty += r.DishAmountInt;
    if (r['OpenDate.Typed'] > e.lastDate && r.DishSumInt > 0) { e.lastDate = r['OpenDate.Typed']; e.price = Math.round(r.DishSumInt / r.DishAmountInt); }
    map.set(k, e);
  }
  const list = [...map.values()].sort((a, b) => (a.group || '').localeCompare(b.group || '') || b.qty - a.qty);
  writeFileSync(new URL('./coffeeteria-iiko.json', import.meta.url), JSON.stringify(list, null, 1));
  const groups = {};
  for (const e of list) (groups[`${e.category} / ${e.group}`] ??= []).push(`${e.name.trim()} ${e.price}${e.price % 10 ? '(!)' : ''}·${e.qty}`);
  for (const [g, items] of Object.entries(groups)) console.log(`\n## ${g} (${items.length}): ${items.join(' | ')}`);
  console.log('\nвсего', list.length);
} finally { await fetch(`${url}/resto/api/logout?key=${key}`); }
