from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# 1) Recommendation controls: expose the original/basic engine and DB engine separately.
old='''<section class="card auto"><div class="top"><div><h3>✨ 식단 추천 자동 채우기</h3><div class="muted" id="guide">레시피 DB를 우선 사용하고, 재료가 부족하면 중복을 줄여 조합합니다.</div></div><div class="actions"><button class="pri" id="fillWeek">이번 주 추천</button><button class="pri" id="fillMonth">이번 달 추천</button></div></div>'''
new='''<section class="card auto"><div class="top"><div><h3>✨ 식단 추천 자동 채우기</h3><div class="muted" id="guide"><b>기본 추천</b>은 처음 방식의 메뉴/재료 조합, <b>DB 추천</b>은 실제 레시피 300개를 우선 사용합니다.</div></div><div class="actions"><button class="pri" id="fillWeekBase">기본 주간 추천</button><button class="out" id="fillWeekDb">DB 주간 추천</button><button class="pri" id="fillMonthBase">기본 월간 추천</button><button class="out" id="fillMonthDb">DB 월간 추천</button></div></div>'''
if old not in s:
    raise SystemExit('top recommendation controls not found')
s=s.replace(old,new,1)

# 2) Mobile controls.
s=s.replace('.mobilebar>div{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px}', '.mobilebar>div{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}', 1)
old_mobile='<div class="mobilebar"><div><button class="pri" id="mRec">추천</button><button class="sec" id="mSave">저장</button><button class="out" id="mInfo">아기 정보</button></div></div>'
new_mobile='<div class="mobilebar"><div><button class="pri" id="mBase">기본 추천</button><button class="out" id="mDb">DB 추천</button><button class="sec" id="mSave">저장</button><button class="out" id="mInfo">정보</button></div></div>'
if old_mobile not in s:
    raise SystemExit('mobile controls not found')
s=s.replace(old_mobile,new_mobile,1)

# 3) Replace menu-title inference with a stricter semantic extractor + cleanup.
start=s.index("const MENU_NAME_STYLES=")
end=s.index("function recommend(date)", start)
menu_block=r'''const MENU_NAME_STYLES=['크림리조또','리조또','볶음밥','동그랑땡','닭갈비','떡갈비','밥전','주먹밥','계란찜','미역국','무국','된장국','국밥','덮밥','진밥','죽','조림','찜','전','구이','무침','오트밀','수육','완자','카레','파스타','국수','우동','팬케이크','샌드위치','오믈렛','그라탕','스프','수프','스튜','김밥','국'];
const MENU_FILLER=new Set(['요리','메뉴','식단','소스','양념','양념장','방법','법','추천','특식','반찬','간식','입','짧은','한','그릇','한그릇','한끼','아이가','아기가','아이들이','아이는','아기를','아기도','뚝딱한','뚝딱','먹는','먹기','잘먹는','잘','쉽게','간단히','맛있게','맛있는','건강한','영양','완료','만든','만드는','만들기','레시피','초간단','간단','엄마표','돌전','돌이후','돌']);
const MENU_PARTICLES=new Set(['이','가','은','는','을','를','의','에','에서','로','으로','와','과','도','만','랑','하고']);
function cleanRecipeTitle(title){let x=String(title||'');x=x.replace(/\([^)]*\)|\[[^\]]*\]/g,' ');x=x.replace(/\b\d+\s*개월\b/g,' ');x=x.replace(/(?:돌아기|두돌아기|아기|유아|아이|키즈)(?:들이|에게|랑|와|가|는|은|을|를|의|도|만)?/g,' ');x=x.replace(/(?:유아식|아기반찬|유아반찬|아이반찬|무염반찬|특식)/g,' ');x=x.replace(/(?:양념장\s*)?(?:만드는\s*법|만드는법|만드는\s*방법|만들기)|황금레시피|레시피|엄마표|초간단|간단하게|한\s*그릇|한그릇|한\s*끼|한끼|뚝딱(?:한)?/g,' ');x=x.replace(/[|/:;,·ㆍ~!?#♡♥★☆▶▷→←+=_'"“”‘’]+/g,' § ');return x.replace(/\s+/g,' ').trim()}
function stripKnownParticle(w){let x=String(w||'').trim();if(!x)return'';for(const j of ['으로','에서','에게','이랑','랑','하고','로','와','과','이','가','은','는','을','를','의','에','도','만']){if(x.length>j.length+1&&x.endsWith(j)){let base=x.slice(0,-j.length);if(majorTokens(base).length||/^(야채|채소|크림|간장|치즈|밤|어묵|말이|두부|계란|고기|닭|생선|새우|소고기|돼지고기)$/.test(base))return base}}return x}
function sanitizeMenuCandidate(text){let a=String(text||'').replace(/[^가-힣A-Za-z0-9\s]/g,' ').split(/\s+/).map(stripKnownParticle).filter(Boolean).filter(w=>!MENU_FILLER.has(w)&&!MENU_PARTICLES.has(w));a=a.filter((w,i)=>!a.some((z,j)=>j!==i&&z.length>w.length&&z.includes(w)));let out=[];a.forEach(w=>{if(!out.includes(w))out.push(w)});return out.join(' ').replace(/\s+/g,' ').trim()}
function menuPrevWord(w){w=sanitizeMenuCandidate(w);if(!w||w.length>10||MENU_FILLER.has(w)||MENU_PARTICLES.has(w))return false;if(/(요리|레시피|만들기|방법|양념장)$/.test(w))return false;return /^[가-힣A-Za-z0-9]+$/.test(w)}
function dishCandidateFromSegment(seg){let words=String(seg||'').trim().split(/\s+/).filter(Boolean),best='',bestScore=-1e9;MENU_NAME_STYLES.forEach(style=>{words.forEach((word,i)=>{let safe=sanitizeMenuCandidate(word),pos=safe.indexOf(style);if(pos<0)return;let prefix=safe.slice(0,pos),strongPrefix=prefix&&prefix.length>=2&&!/^(야채|채소|크림|간장|밥|치즈|두부|계란|고기|닭|밤|어묵|말이)$/.test(prefix),start=i;if(!strongPrefix){let c=0,max=3;for(let j=i-1;j>=0&&c<max;j--){if(words[j]==='§'||!menuPrevWord(words[j]))break;start=j;c++}}let cand=sanitizeMenuCandidate(words.slice(start,i+1).join(' '));if(!cand)return;let specificity=majorTokens(cand).length*7,styleBonus=style.length*2,prefixBonus=Math.max(0,prefix.length)*1.5,score=45+specificity+styleBonus+prefixBonus-Math.max(0,cand.length-26)*1.5;if(score>bestScore||(score===bestScore&&(!best||cand.length<best.length))){bestScore=score;best=cand}})});return best}
function fallbackTitleCandidate(clean){let segs=String(clean||'').split('§').map(sanitizeMenuCandidate).filter(Boolean),best='',score=-1e9;segs.forEach((x,i)=>{if(!x)return;let s=majorTokens(x).length*6-Math.max(0,x.length-20)*1.5+i*.1;if(s>score){score=s;best=x}});return best}
function recipeMenuName(r){let raw=String(r?.title||''),clean=cleanRecipeTitle(raw),segments=clean.split('§').map(x=>x.trim()).filter(Boolean),best='',bestScore=-1e9;segments.forEach((seg,i)=>{let cand=dishCandidateFromSegment(seg);if(!cand)return;let sc=majorTokens(cand).length*6-Math.max(0,cand.length-24)+i*.1;if(sc>bestScore){bestScore=sc;best=cand}});let out=sanitizeMenuCandidate(best||fallbackTitleCandidate(clean)||raw);return out||'추천 메뉴'}
'''
s=s[:start]+menu_block+s[end:]

# 4) Split the recommendation engines.
old_db="function recommend(date){let s=seed(date),set=new Set(pantry()),used=weekUsedMenus(date),out={};MEALS.forEach(([k],i)=>{let r=pickDbRecipe(k,date,set,used),menu=r?recipeMenuName(r):(state.settings.pantryOnly?pantryMeal(set,k,s+i*11,used):fallbackBase(k,s+i*11,used));out[k]=menu;used.push(menu)});return out}\nfunction fillDate(date){if(state.settings.pantryOnly&&!pantry().length){alert('보유 재료를 먼저 입력해 주세요.');return false}state.meals[date]=state.meals[date]||{};state.meta[date]=state.meta[date]||{};let r=recommend(date);MEALS.forEach(([k])=>{if(!$('emptyOnly').checked||!(state.meals[date][k]||'').trim()){state.meals[date][k]=r[k];state.meta[date][k]=r[k].startsWith('재료 부족')?'short':'rec'}});return true}"
new_db="function recommendBase(date){let s=seed(date),set=new Set(pantry()),used=weekUsedMenus(date),out={};MEALS.forEach(([k],i)=>{let menu=state.settings.pantryOnly?pantryMeal(set,k,s+i*11,used):fallbackBase(k,s+i*11,used);out[k]=menu;used.push(menu)});return out}\nfunction recommendDb(date){let s=seed(date),set=new Set(pantry()),used=weekUsedMenus(date),out={};MEALS.forEach(([k],i)=>{let r=pickDbRecipe(k,date,set,used),menu=r?recipeMenuName(r):(state.settings.pantryOnly?pantryMeal(set,k,s+i*11,used):fallbackBase(k,s+i*11,used));out[k]=menu;used.push(menu)});return out}\nfunction fillDate(date,mode='base'){if(state.settings.pantryOnly&&!pantry().length){alert('보유 재료를 먼저 입력해 주세요.');return false}state.meals[date]=state.meals[date]||{};state.meta[date]=state.meta[date]||{};let r=mode==='db'?recommendDb(date):recommendBase(date);MEALS.forEach(([k])=>{if(!$('emptyOnly').checked||!(state.meals[date][k]||'').trim()){state.meals[date][k]=r[k];state.meta[date][k]=r[k].startsWith('재료 부족')?'short':(mode==='db'?'db':'rec')}});return true}"
if old_db not in s:
    raise SystemExit('recommend/fillDate block not found')
s=s.replace(old_db,new_db,1)

# 5) Distinguish recommendation source in badges and give each day two buttons.
old_badge="cls=m[k]==='short'?'short':m[k]==='manual'?'manual':'',label=m[k]==='short'?'재료 부족':m[k]==='manual'?'수기':'추천';"
new_badge="cls=m[k]==='short'?'short':m[k]==='manual'?'manual':'',label=m[k]==='short'?'재료 부족':m[k]==='manual'?'수기':m[k]==='db'?'DB 추천':'기본 추천';"
if old_badge not in s:
    raise SystemExit('badge block not found')
s=s.replace(old_badge,new_badge,1)
old_tools='<div class="tools"><button class="pri rec" data-date="${date}">추천</button><button class="sec copy" data-date="${date}">전날 복사</button><button class="sec clear" data-date="${date}">비우기</button></div>'
new_tools='<div class="tools"><button class="pri recbase" data-date="${date}">기본</button><button class="out recdb" data-date="${date}">DB</button><button class="sec copy" data-date="${date}">전날 복사</button><button class="sec clear" data-date="${date}">비우기</button></div>'
if old_tools not in s:
    raise SystemExit('daily tools block not found')
s=s.replace(old_tools,new_tools,1)
old_handler="document.querySelectorAll('.rec').forEach(b=>b.onclick=()=>{if(fillDate(b.dataset.date)){save(false);render()}});"
new_handler="document.querySelectorAll('.recbase').forEach(b=>b.onclick=()=>{if(fillDate(b.dataset.date,'base')){save(false);render()}});document.querySelectorAll('.recdb').forEach(b=>b.onclick=()=>{if(fillDate(b.dataset.date,'db')){save(false);render()}});"
if old_handler not in s:
    raise SystemExit('daily recommendation handler not found')
s=s.replace(old_handler,new_handler,1)

# 6) Replace period fill handlers with mode-aware versions and wire all buttons.
pat=re.compile(r"function fillW\(\)\{.*?\}\s*function fillM\(\)\{.*?\}\s*\$\('fillWeek'\)\.onclick=fillW;\$\('fillMonth'\)\.onclick=fillM;\$\('mRec'\)\.onclick=\(\)=>view==='week'\?fillW\(\):fillM\(\);",re.S)
rep="function fillW(mode='base'){for(let i=0;i<7;i++){let d=new Date(weekStart);d.setDate(d.getDate()+i);if(fillDate(ds(d),mode)===false)return}save(false);render();toast(mode==='db'?'DB 기준으로 이번 주를 추천했습니다.':'기본 방식으로 이번 주를 추천했습니다.')}function fillM(mode='base'){let y=monthStart.getFullYear(),m=monthStart.getMonth(),last=new Date(y,m+1,0).getDate();for(let d=1;d<=last;d++)if(fillDate(ds(new Date(y,m,d)),mode)===false)return;save(false);render();toast(mode==='db'?'DB 기준으로 이번 달을 추천했습니다.':'기본 방식으로 이번 달을 추천했습니다.')} $('fillWeekBase').onclick=()=>fillW('base');$('fillWeekDb').onclick=()=>fillW('db');$('fillMonthBase').onclick=()=>fillM('base');$('fillMonthDb').onclick=()=>fillM('db');$('mBase').onclick=()=>view==='week'?fillW('base'):fillM('base');$('mDb').onclick=()=>view==='week'?fillW('db'):fillM('db');"
s,n=pat.subn(rep,s,count=1)
if n!=1:
    raise SystemExit('period recommendation handlers not found')

p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
if sw.exists():
    t=sw.read_text(encoding='utf-8')
    t=re.sub(r'baby-meal-planner-v\d+','baby-meal-planner-v14',t)
    sw.write_text(t,encoding='utf-8')
