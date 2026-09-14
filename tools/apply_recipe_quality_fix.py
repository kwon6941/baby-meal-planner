from pathlib import Path
import re

# 1) Tighten recipe matching in the app.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

new_match = r'''function tokens(menu){let v=[...C.carb,...C.protein,...C.veg,...C.fruit,...C.dairy,'소고기','닭고기','돼지고기','계란','두부','연어','흰살생선','새우','오징어','애호박','브로콜리','당근','감자','고구마','단호박','시금치','양배추','배추','버섯','양송이','가지','무','미역','오이','연근','콩나물','청경채','양파','사과','배','바나나','딸기','키위','복숭아','블루베리','요거트','치즈','우유','오트밀','메추리알'];return [...new Set(v.filter(x=>String(menu||'').includes(x)))]}
const RECIPE_STYLES=['볶음밥','리조또','계란찜','미역국','무국','국밥','덮밥','진밥','죽','조림','찜','밥전','전','구이','무침','그라탕','오트밀','국'];
function recipeStyle(x){x=String(x||'');return RECIPE_STYLES.find(k=>x.includes(k))||''}
function compactRecipeText(x){return String(x||'').replace(/돌아기|두돌아기|아기|유아식|간단|초간단|레시피|만들기|만드는법|만드는 법|반찬|메뉴|한그릇|한 끼|한끼/g,'').replace(/[+\\s·,()[\\]{}\\/_-]/g,'').trim()}
function bestRecipe(menu){
  if(!menu||menu.startsWith('재료 부족'))return null;
  const mt=tokens(menu),ms=recipeStyle(menu),mc=compactRecipeText(menu);
  let best=null,bestScore=-1;
  RECIPES.forEach(r=>{
    const title=String(r.title||'');
    const rt=new Set([...tokens(title),...((r.keywords||[]).filter(Boolean))]);
    const overlap=mt.filter(k=>rt.has(k));
    const rs=recipeStyle(title+' '+(r.exact||[]).join(' '));
    const rc=compactRecipeText(title);
    const phrase=mc.length>=5&&(rc.includes(mc)||mc.includes(rc));
    const styleOK=!ms||rs===ms;
    const strong=overlap.length>=2;
    if(!(phrase||(styleOK&&strong)))return;
    const score=(phrase?20:0)+overlap.length*4+(ms&&rs===ms?5:0);
    if(score>bestScore){bestScore=score;best=r}
  });
  return best;
}
function yt(menu)'''

s, n = re.subn(r"function tokens\(menu\)\{.*?function yt\(menu\)", new_match, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Could not locate recipe matching block in index.html')

s = s.replace('실제/유사 레시피', '일치 레시피')
# Re-render after remote DB load so newly fetched recipes are reflected immediately.
s = s.replace("if(show)toast('최신 레시피 DB를 불러왔습니다.')", "render();if(show)toast('최신 레시피 DB를 불러왔습니다.')")
p.write_text(s, encoding='utf-8')

# 2) Broaden automated recipe discovery.
u = Path('tools/update_recipes.py')
t = u.read_text(encoding='utf-8')
queries = [
 '돌아기유아식','돌아기유아식반찬','아기유아식','13개월유아식','14개월유아식',
 '아기유아식소고기','아기유아식닭고기','아기유아식두부','아기유아식계란','아기유아식연어','아기유아식흰살생선','돌아기오트밀','아기유아식감자',
 '돌아기 소고기 애호박 덮밥','돌아기 소고기 브로콜리 덮밥','돌아기 닭고기 감자 조림','돌아기 두부 애호박 전','돌아기 연어 리조또','돌아기 흰살생선 전',
 '돌아기 소고기 두부 국','돌아기 닭고기 브로콜리 덮밥','돌아기 계란 애호박 국','돌아기 연어 감자','돌아기 두부 채소 찜',
 '돌아기 바나나 오트밀','돌아기 단호박 오트밀','돌아기 계란 채소찜','돌아기 소고기 미역국','돌아기 소고기 무국','돌아기 볶음밥',
 '돌아기 두부조림','돌아기 계란찜','돌아기 밥전','돌아기 완자','돌아기 떡갈비','유아식 브로콜리 두부','유아식 소고기 애호박','유아식 닭고기 감자','유아식 연어','유아식 한그릇 덮밥'
]
qtext = 'QUERIES=' + repr(queries) + '\nPAGES_PER_QUERY=2'
t, n = re.subn(r'QUERIES=\[.*?\]\nPAGES_PER_QUERY=\d+', qtext, t, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Could not update query list')
u.write_text(t, encoding='utf-8')

# 3) Bump cache so the stricter matching reaches installed PWAs.
sw = Path('sw.js')
w = sw.read_text(encoding='utf-8').replace("baby-meal-planner-v8", "baby-meal-planner-v9")
sw.write_text(w, encoding='utf-8')
