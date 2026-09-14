from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

needle = "function fallbackBase(type,s,used){let arr=type.startsWith('snack')?BASE.snack:(BASE[type]||BASE.lunch),fresh=arr.filter(x=>!used.includes(x));return pick(fresh.length?fresh:arr,s)}\nfunction recommend(date){let s=seed(date),set=new Set(pantry()),used=weekUsedMenus(date),out={};MEALS.forEach(([k],i)=>{let r=pickDbRecipe(k,date,set,used),menu=r?String(r.title||'').trim():(state.settings.pantryOnly?pantryMeal(set,k,s+i*11,used):fallbackBase(k,s+i*11,used));out[k]=menu;used.push(menu)});return out}"

replacement = r'''function fallbackBase(type,s,used){let arr=type.startsWith('snack')?BASE.snack:(BASE[type]||BASE.lunch),fresh=arr.filter(x=>!used.includes(x));return pick(fresh.length?fresh:arr,s)}
function cleanRecipeTitle(title){let x=String(title||'').replace(/\([^)]*(아기|유아|돌|반찬|간식|레시피)[^)]*\)/g,' ').replace(/\[[^\]]*(아기|유아|돌|반찬|간식|레시피)[^\]]*\]/g,' ').replace(/^(돌아기|두돌아기|아기|유아식|유아|아이|키즈)[\s·:_-]*/g,' ').replace(/(돌아기|두돌아기|아기|유아식|유아|아이반찬|아기반찬|유아반찬|간단|초간단|한그릇|한 끼|한끼|레시피|만들기|만드는법|만드는 법|황금레시피|쉬운 요리|간단 요리)/g,' ').replace(/[|#♡♥★☆]/g,' ').replace(/\s+/g,' ').replace(/^[·,:_\-\s]+|[·,:_\-\s]+$/g,'').trim();return x}
function recipeMenuName(r){let raw=String(r?.title||''),clean=cleanRecipeTitle(raw),exact=(r?.exact||[]).filter(Boolean),style=menuStyleSimple(raw+' '+exact.join(' '));let generic=/^(요리|반찬|메뉴|식단|간식|한그릇)$/;let parts=exact.filter(x=>!generic.test(x)&&x!==style);let uniq=[...new Set(parts)];if(clean&&clean.length<=34&&(!style||clean.includes(style)))return clean;if(style&&uniq.length)return [...uniq.slice(0,3),style].join(' ');return clean||raw}
function recommend(date){let s=seed(date),set=new Set(pantry()),used=weekUsedMenus(date),out={};MEALS.forEach(([k],i)=>{let r=pickDbRecipe(k,date,set,used),menu=r?recipeMenuName(r):(state.settings.pantryOnly?pantryMeal(set,k,s+i*11,used):fallbackBase(k,s+i*11,used));out[k]=menu;used.push(menu)});return out}'''

if needle not in s:
    raise SystemExit('target recommendation block not found')

s = s.replace(needle, replacement, 1)
p.write_text(s, encoding='utf-8')

sw = Path('sw.js')
if sw.exists():
    t = sw.read_text(encoding='utf-8')
    t = re.sub(r'baby-meal-planner-v\d+', 'baby-meal-planner-v12', t)
    sw.write_text(t, encoding='utf-8')
