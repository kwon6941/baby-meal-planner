from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Visible version marker so stale PWA screens are obvious.
s=s.replace('<b>DB 추천</b>은 실제 레시피 300개를 우선 사용합니다.</div>', '<b>DB 추천</b>은 실제 레시피 300개를 우선 사용합니다. · <b>v15</b></div>', 1)

# Strengthen title cleanup: drop Korean prose/adjectives/verbs that describe cooking rather than the dish.
old="const MENU_FILLER=new Set(['요리','메뉴','식단','소스','양념','양념장','방법','법','추천','특식','반찬','간식','입','짧은','한','그릇','한그릇','한끼','아이가','아기가','아이들이','아이는','아기를','아기도','뚝딱한','뚝딱','먹는','먹기','잘먹는','잘','쉽게','간단히','맛있게','맛있는','건강한','영양','완료','만든','만드는','만들기','레시피','초간단','간단','엄마표','돌전','돌이후','돌']);"
new="const MENU_FILLER=new Set(['요리','메뉴','식단','소스','양념','양념장','방법','법','추천','특식','반찬','간식','입','짧은','한','그릇','한그릇','한끼','아이가','아기가','아이들이','아이는','아기를','아기도','뚝딱한','뚝딱','먹는','먹기','잘먹는','잘','쉽게','간단히','맛있게','맛있는','건강한','영양','완료','만든','만드는','만들기','레시피','초간단','간단','엄마표','돌전','돌이후','돌','시원한','시원하게','고소한','고소하게','담백한','담백하게','부드러운','부드럽게','달콤한','달콤하게','촉촉한','촉촉하게','든든한','든든하게','영양만점','맛있고','맛있게','쉬운','쉽게','넣어','넣고','넣어서','섞어','섞고','볶아','볶고','끓여','끓이고','끓인','만들어','만들고','완성','완성한','반죽','반죽을','반죽에','재료','재료를','준비','준비한','활용','활용한','먹여','먹이는','먹어','먹고']);"
if old not in s:
    raise SystemExit('MENU_FILLER block not found')
s=s.replace(old,new,1)

# Extra sanitation for common prose endings that slip through as standalone words.
old_func="function sanitizeMenuCandidate(text){let a=String(text||'').replace(/[^가-힣A-Za-z0-9\\s]/g,' ').split(/\\s+/).map(stripKnownParticle).filter(Boolean).filter(w=>!MENU_FILLER.has(w)&&!MENU_PARTICLES.has(w));a=a.filter((w,i)=>!a.some((z,j)=>j!==i&&z.length>w.length&&z.includes(w)));let out=[];a.forEach(w=>{if(!out.includes(w))out.push(w)});return out.join(' ').replace(/\\s+/g,' ').trim()}"
new_func="function sanitizeMenuCandidate(text){let a=String(text||'').replace(/[^가-힣A-Za-z0-9\\s]/g,' ').split(/\\s+/).map(stripKnownParticle).filter(Boolean).filter(w=>!MENU_FILLER.has(w)&&!MENU_PARTICLES.has(w)).filter(w=>!/(?:하며|해서|하여|하고|넣어|넣고|섞어|섞고|끓여|끓이고|볶아|볶고|만들어|만들고|먹는|먹어|먹고)$/.test(w));a=a.filter((w,i)=>!a.some((z,j)=>j!==i&&z.length>w.length&&z.includes(w)));let out=[];a.forEach(w=>{if(!out.includes(w))out.push(w)});return out.join(' ').replace(/\\s+/g,' ').trim()}"
if old_func not in s:
    raise SystemExit('sanitizeMenuCandidate not found')
s=s.replace(old_func,new_func,1)

# Force manifest/SW refresh and one-time reload when the new worker takes control.
s=s.replace('<link rel="manifest" href="./manifest.webmanifest">','<link rel="manifest" href="./manifest.webmanifest?v=15">',1)
old_reg="render();loadRecipes();if('serviceWorker'in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{}));"
new_reg="render();loadRecipes();if('serviceWorker'in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js?v=15').then(r=>r.update()).catch(()=>{}));navigator.serviceWorker.addEventListener('controllerchange',()=>{if(!sessionStorage.getItem('pwa_v15_reload')){sessionStorage.setItem('pwa_v15_reload','1');location.reload()}})}"
if old_reg not in s:
    raise SystemExit('service worker registration block not found')
s=s.replace(old_reg,new_reg,1)

p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"baby-meal-planner-v\\d+","baby-meal-planner-v15",t)
sw.write_text(t,encoding='utf-8')

mf=Path('manifest.webmanifest')
m=mf.read_text(encoding='utf-8')
m=m.replace('"start_url": "./index.html"','"start_url": "./index.html?v=15"')
mf.write_text(m,encoding='utf-8')
