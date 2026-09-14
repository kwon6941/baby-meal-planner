#!/usr/bin/env python3
import json
from pathlib import Path
from menu_name_utils import derive_menu_name, audit_reason

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / 'recipes.json'
AUDIT = ROOT / 'menu_name_audit.json'

data = json.loads(RECIPES.read_text(encoding='utf-8'))
recipes = data.get('recipes', [])
rows = []
for r in recipes:
    name = derive_menu_name(r)
    r['menu_name'] = name
    reasons = audit_reason(name)
    rows.append({
        'title': r.get('title',''),
        'menu_name': name,
        'reasons': reasons,
        'url': r.get('url',''),
    })

data['recipe_count'] = len(recipes)
RECIPES.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
flagged = [x for x in rows if x['reasons']]
report = {
    'total': len(rows),
    'flagged_count': len(flagged),
    'flagged': flagged,
    'all': rows,
}
AUDIT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"audited={len(rows)} flagged={len(flagged)}")
for x in flagged[:80]:
    print('FLAG', x['reasons'], '::', x['title'], '=>', x['menu_name'])
