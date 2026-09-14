#!/usr/bin/env python3
from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
idx=root/'index.html'
s=idx.read_text(encoding='utf-8')

# Prefer the pre-audited DB menu_name and only fall back to the browser parser for legacy entries.
old="function recipeMenuName(r){let raw=String(r?.title||''),clean=cleanRecipeTitle(raw),segments=clean.split('§').map(x=>x.trim()).filter(Boolean),best='',bestScore=-1e9;segments.forEach((seg,i)=>{let cand=dishCandidateFromSegment(seg);if(!cand)return;let sc=majorTokens(cand).length*6-Math.max(0,cand.length-24)+i*.1;if(sc>bestScore){bestScore=sc;best=cand}});let out=sanitizeMenuCandidate(best||fallbackTitleCandidate(clean)||raw);return out||'추천 메뉴'}"
new="function recipeMenuName(r){let audited=String(r?.menu_name||'').trim();if(audited&&audited!=='추천 메뉴')return audited;let raw=String(r?.title||''),clean=cleanRecipeTitle(raw),segments=clean.split('§').map(x=>x.trim()).filter(Boolean),best='',bestScore=-1e9;segments.forEach((seg,i)=>{let cand=dishCandidateFromSegment(seg);if(!cand)return;let sc=majorTokens(cand).length*6-Math.max(0,cand.length-24)+i*.1;if(sc>bestScore){bestScore=sc;best=cand}});let out=sanitizeMenuCandidate(best||fallbackTitleCandidate(clean)||raw);return out||'추천 메뉴'}"
if old not in s:
    raise SystemExit('recipeMenuName target not found')
s=s.replace(old,new,1)

old_pick="function pickDbRecipe(type,date,set,used){if(!RECIPES.length)return null;let c=RECIPES.filter(r=>recipeEligible(r,type,set)&&!used.includes(String(r.title||''))).map(r=>({r,score:recipeScore(r,type,set,used,date)})).sort((a,b)=>b.score-a.score);return c.length?c[0].r:null}"
new_pick="function pickDbRecipe(type,date,set,used){if(!RECIPES.length)return null;let c=RECIPES.filter(r=>{let n=String(r?.menu_name||'').trim();return n&&n!=='추천 메뉴'&&recipeEligible(r,type,set)&&!used.includes(n)}).map(r=>({r,score:recipeScore(r,type,set,used,date)})).sort((a,b)=>b.score-a.score);return c.length?c[0].r:null}"
if old_pick not in s:
    raise SystemExit('pickDbRecipe target not found')
s=s.replace(old_pick,new_pick,1)

# Prefer exact menu_name matching when linking back to the recipe.
old_best="const title=String(r.title||'');\n    const rt=new Set([...tokens(title),...((r.keywords||[]).filter(Boolean))]);"
new_best="const title=String(r.title||''),audited=String(r.menu_name||'');\n    if(audited&&compactRecipeText(audited)===mc){best=r;bestScore=999;return;}\n    const rt=new Set([...tokens(title+' '+audited),...((r.keywords||[]).filter(Boolean))]);"
if old_best not in s:
    raise SystemExit('bestRecipe target not found')
s=s.replace(old_best,new_best,1)

# Make the version visible and force PWA refresh.
s=s.replace('· <b>v15</b>','· <b>v16</b>')
s=s.replace('manifest.webmanifest?v=15','manifest.webmanifest?v=16')
s=s.replace("navigator.serviceWorker.register('./sw.js').catch(()=>{})","navigator.serviceWorker.register('./sw.js?v=16',{updateViaCache:'none'}).then(r=>r.update()).catch(()=>{})")
idx.write_text(s,encoding='utf-8')

sw=root/'sw.js'
t=sw.read_text(encoding='utf-8')
t=re.sub(r"baby-meal-planner-v\d+","baby-meal-planner-v16",t)
sw.write_text(t,encoding='utf-8')

# Ensure every daily update regenerates menu_name with the same audited parser.
up=root/'tools'/'update_recipes.py'
u=up.read_text(encoding='utf-8')
if 'from menu_name_utils import derive_menu_name' not in u:
    u=u.replace('from bs4 import BeautifulSoup\n','from bs4 import BeautifulSoup\nfrom menu_name_utils import derive_menu_name\n',1)
old="items=list(existing.values())\n    items.sort(key=lambda r:(len(r.get('keywords',[])),r.get('modified') or r.get('published') or r.get('discovered_at') or ''),reverse=True)"
new="items=list(existing.values())\n    for r in items:\n        r['menu_name']=derive_menu_name(r)\n    items.sort(key=lambda r:(len(r.get('keywords',[])),r.get('modified') or r.get('published') or r.get('discovered_at') or ''),reverse=True)"
if old not in u:
    raise SystemExit('updater save block not found')
u=u.replace(old,new,1)
up.write_text(u,encoding='utf-8')
