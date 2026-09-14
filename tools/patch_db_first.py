from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
start = s.index('function pantryMeal(')
end = s.index('function tokens(menu)', start)

new = r'''function avoidList(){return state.baby.avoid.split(/[,，;\n]+/).map(x=>x.trim()).filter(Boolean)}
function recipeText(r){return [r.title,...(r.keywords||[]),...(r.exact||[]),...(r.ingredients||[])].join(' ')}
function majorTokens(text){let all=[...C.carb,...C.protein,...C.veg,...C.fruit,...C.dairy,'양송이','양파','대파','미역','새우','오징어','청경채','연근','콩나물','오이'];return[...new Set(all.filter(x=>String(text||'').includes(x)))]}
function menuProtein(menu){return C.protein.find(x=>String(menu||'').includes(x))||''}
function menuStyleSimple(menu){let styles=['덮밥','볶음밥','리조또','진밥','죽','국밥','국','조림','찜','전','구이','무침','오트밀'];return styles.find(x=>String(menu||'').includes(x))||''}
function weekUsedMenus(date){let d=startWeek(pd(date)),out=[];for(let i=0;i<7;i++){let x=new Date(d);x.setDate(x.getDate()+i);let m=state.meals[ds(x)]||{};MEALS.forEach(([k])=>{let v=(m[k]||'').trim();if(v)out.push(v)})}return out}
function tinyHash(s){let h=0;for(let i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))>>>0;return h}
function countContaining(list,term){return term?list.filter(x=>String(x).includes(term)).length:0}
function recipeEligible(r,type,set){let txt=recipeText(r),title=String(r.title||''),avoid=avoidList();if(!title||avoid.some(x=>txt.includes(x)))return false;let snack=type.startsWith('snack');if(snack){if(!/(간식|오트밀|요거트|바나나|사과|배|고구마|단호박|감자|팬케이크|빵|치즈|과일|전)/.test(title))return false}else if(/(쿠키|머핀|케이크|아이스크림|스무디|주스|잼|과자)/.test(title))return false;if(!state.settings.pantryOnly)return true;let major=majorTokens([title,...(r.exact||[]),...(r.keywords||[])].join(' ')),proteins=C.protein.filter(x=>title.includes(x));if(proteins.length&&!proteins.some(x=>set.has(x)))return false;if(!major.length)return false;let hit=major.filter(x=>set.has(x)).length,coverage=hit/major.length;return hit>=1&&(major.length<3?coverage>=0.5:coverage>=0.4)}
function recipeScore(r,type,set,used,date){let title=String(r.title||''),major=majorTokens([title,...(r.exact||[]),...(r.keywords||[])].join(' ')),hit=major.filter(x=>set.has(x)).length,coverage=major.length?hit/major.length:0,score=20;if(/돌아기|아기|유아식/.test(title))score+=4;if(state.settings.pantryOnly)score+=hit*5+coverage*12;let p=menuProtein(title),st=menuStyleSimple(title);score-=countContaining(used,p)*7;score-=countContaining(used,st)*4;if(used.includes(title))score-=1000;if(type==='breakfast'&&/(오트밀|진밥|죽|리조또|계란찜)/.test(title))score+=4;if(type.startsWith('snack')&&/(간식|오트밀|요거트|바나나|사과|배|고구마|단호박|팬케이크|치즈)/.test(title))score+=7;if((type==='lunch'||type==='dinner')&&/(덮밥|볶음밥|리조또|진밥|국|조림|찜|전|구이)/.test(title))score+=4;score+=(tinyHash(date+'|'+type+'|'+title)%100)/100;return score}
function pickDbRecipe(type,date,set,used){if(!RECIPES.length)return null;let c=RECIPES.filter(r=>recipeEligible(r,type,set)&&!used.includes(String(r.title||''))).map(r=>({r,score:recipeScore(r,type,set,used,date)})).sort((a,b)=>b.score-a.score);return c.length?c[0].r:null}
function leastUsed(items,used,s){if(!items.length)return null;let arr=items.map((x,i)=>({x,n:countContaining(used,x),j:(tinyHash(String(s)+'|'+x)+i)%97})).sort((a,b)=>a.n-b.n||a.j-b.j);return arr[0].x}
function pantryMeal(set,type,s,used=[]){let p=leastUsed(cand('protein',set),used,s+2),v=leastUsed(cand('veg',set),used,s+5),f=leastUsed(cand('fruit',set),used,s+7),d=leastUsed(cand('dairy',set),used,s+9),rice=has(set,'밥'),oat=has(set,'오트밀'),st=leastUsed(cand('carb',set).filter(x=>x!=='밥'&&x!=='오트밀'),used,s+11);if(type.startsWith('snack')){let opts=[];if(f&&d)opts.push(`${f} + ${d}`);if(f)opts.push(`잘 익은 ${f}`);if(st)opts.push(`부드럽게 익힌 ${st}`);if(oat&&f)opts.push(`${f} 오트밀`);return leastUsed(opts,used,s+13)||'재료 부족 — 간식 직접 입력'}if(type==='breakfast'&&oat&&f)return`${f} 오트밀`;let styles=type==='breakfast'?['진밥','리조또','덮밥']:['덮밥','리조또','조림','전','진밥','부드러운찜'],style=leastUsed(styles,used,s+17);if(rice&&p&&v){if(style==='조림')return`${p} ${v} 조림 + 밥`;if(style==='전')return`${p} ${v} 전 + 밥`;if(style==='부드러운찜')return`${p} ${v} 부드러운찜 + 밥`;return`${p} ${v} ${style}`}if(has(set,'계란')&&v)return`${v} 계란찜`;if(has(set,'두부')&&v)return`두부 ${v} 부드러운찜`;if(rice&&p)return`${p} 덮밥`;if(rice&&v)return`${v} 진밥`;if(p&&st)return`${p} + 부드러운 ${st}`;return'재료 부족 — 직접 입력'}
function fallbackBase(type,s,used){let arr=type.startsWith('snack')?BASE.snack:(BASE[type]||BASE.lunch),fresh=arr.filter(x=>!used.includes(x));return pick(fresh.length?fresh:arr,s)}
function recommend(date){let s=seed(date),set=new Set(pantry()),used=weekUsedMenus(date),out={};MEALS.forEach(([k],i)=>{let r=pickDbRecipe(k,date,set,used),menu=r?String(r.title||'').trim():(state.settings.pantryOnly?pantryMeal(set,k,s+i*11,used):fallbackBase(k,s+i*11,used));out[k]=menu;used.push(menu)});return out}
'''

s = s[:start] + new + s[end:]
s = s.replace('생년월일과 보유 재료를 바탕으로 추천합니다.','레시피 DB를 우선 사용하고, 재료가 부족하면 중복을 줄여 조합합니다.')
p.write_text(s, encoding='utf-8')

sw = Path('sw.js')
if sw.exists():
    t = sw.read_text(encoding='utf-8').replace('baby-meal-planner-v9', 'baby-meal-planner-v10')
    sw.write_text(t, encoding='utf-8')
