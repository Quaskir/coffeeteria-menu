# iiko → данные сайта Coffeeteria: названия и цены из кассы; фото, описания, переводы — свои (Menu, шаг 1).
import sys, re, json
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from build_common import *
from build_names import STYLE, TR
SITE = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', 'index-new.html')
site = open(SITE, encoding='utf-8').read()

def js_obj(block_start, end):
    i = site.index(block_start); j = site.index(end, i); return site[i:j]
# вчерашние данные сайта: блюда, фото, греческие метки
old = {}
for m in re.finditer(r"\{ name: '([^']+)'(.*?)price: \d+ \}", site):
    fields = dict(re.findall(r"(name_kz|name_en|desc|desc_kz|desc_en): '([^']*)'", m.group(0)))
    old[m.group(1)] = fields
photos_old = dict(re.findall(r"'([^']+)': '([a-z0-9-]+)'", js_obj('const PHOTOS = {', '\n};')))
greek_old = set(re.findall(r"'([^']+)'", js_obj('const GREEK_DISHES = new Set([', ']);')))

def final_name(raw):
    n = re.sub(r'\s+', ' ', raw).strip()
    n = STYLE.get(n) or DISPLAY.get(n) or n
    n = re.sub(r'"([^"]+)"', r'«\1»', n)
    n = re.sub(r'(\d)\s*мл(?![а-я])', r'\1 мл', n)
    n = re.sub(r'(\d)\s*гр(?![а-я])', r'\1 г', n)
    return re.sub(r'(\d)\s*L$', r'\1 л', n)

rows = load_iiko()
by_norm = {norm(r['display']): r for r in rows}
old_of = {}  # имя iiko → вчерашнее имя на сайте
for n in old:
    r = by_norm.get(norm(ALIAS.get(n, n)))
    if r: old_of[r['name']] = n

esc = lambda s: s.replace('\\', '\\\\').replace("'", "\\'")
sections, photos, greek, report = [], {}, set(), []
for sid, ru, kz, en, gr in SECTIONS:
    items = sorted([r for r in rows if r['section'] == sid], key=lambda r: -r['qty'])
    if not items: continue
    lines = []
    for r in items:
        raw = re.sub(r'\s+', ' ', r['name']).strip()
        name = final_name(r['name'])
        was = old_of.get(r['name'])
        f = dict(old.get(was, {})) if was else {}
        if raw in TR: f['name_kz'], f['name_en'] = TR[raw]
        if 'name_kz' not in f: raise SystemExit(f'нет перевода: {raw}')
        parts = [f"name: '{esc(name)}'", f"name_kz: '{esc(f['name_kz'])}'", f"name_en: '{esc(f['name_en'])}'"]
        for k in ('desc', 'desc_kz', 'desc_en'):
            if f.get(k): parts.append(f"{k}: '{esc(f[k])}'")
        parts.append(f"price: {r['price']}")
        lines.append('      { ' + ', '.join(parts) + ' },')
        if was and was in photos_old: photos[name] = photos_old[was]
        if was and was in greek_old: greek.add(name)
        if raw != name and raw in DISPLAY: report.append(f'{raw} → {name}')
    sections.append(f"  {{\n    id: '{sid}',\n    name: '{ru}', name_kz: '{kz}', name_en: '{en}',\n    items: [\n" + '\n'.join(lines) + "\n    ]\n  },")
    sections_greek = None

menu_js = 'const menuData = [\n' + '\n'.join(sections) + '\n];'
json.dump({'photos': photos, 'greek': sorted(greek), 'typos': report, 'count': len(rows)}, open(__import__('os').path.join(HERE, 'out.json'), 'w'), ensure_ascii=False, indent=1)
open(__import__('os').path.join(HERE, 'menu_iiko.js'), 'w', encoding='utf-8').write(menu_js)
print('позиций', len(rows), '| разделов', len(sections), '| фото', len(photos), '| греческих', len(greek))
