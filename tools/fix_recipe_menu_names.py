from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

start = s.index('function cleanRecipeTitle(')
end = s.index('function recommend(date)', start)

replacement = r'''const MENU_NAME_STYLES=['크림리조또','리조또','볶음밥','동그랑땡','닭갈비','떡갈비','밥전','주먹밥','계란찜','미역국','무국','된장국','국밥','덮밥','진밥','죽','조림','찜','전','구이','무침','오트밀','수육','완자','카레','파스타','국수','우동','팬케이크','샌드위치','오믈렛','그라탕','스프','수프','스튜','김밥','국'];
function cleanRecipeTitle(title){return String(title||'').replace(/\([^)]*\)|\[[^\]]*\]/g,' ').replace(/\b\d+\s*개월\b/g,' ').replace(/돌전|돌이후|돌 이후|돌아기|두돌아기|아기반찬|유아반찬|아이반찬|유아식|아기|유아|아이|키즈|특식|반찬/g,' ').replace(/양념장\s*(만드는\s*법|만드는법|레시피)?/g,' ').replace(/레시피|만들기|만드는\s*법|만드는법|만드는\s*방법|황금레시피|엄마표|초간단|간단하게|한그릇|한\s*그릇|한끼|한\s*끼|뚝딱/g,' ').replace(/[|/:;,]+/g,' § ').replace(/[♡♥★☆#]+/g,' ').replace(/\s+/g,' ').trim()}
function menuPrevWord(w){w=String(w||'').trim();if(!w||w==='§'||w.length>9)return false;if(/^(요리|메뉴|식단|소스|양념|양념장|방법|법|추천|입|짧은|한|그릇|아이가|아기가|아이들이|뚝딱한|뚝딱|먹는|먹기|잘먹는|잘|쉽게|간단히|맛있게|맛있는|건강한|영양|완료|만든|만드는)$/.test(w))return false;if(/(요리|레시피|만들기|방법)$/.test(w))return false;return /^[가-힣A-Za-z0-9]+$/.test(w)}
function dishCandidateFromSegment(seg){let words=String(seg||'').trim().split(/\s+/).filter(Boolean),best='',bestScore=-1e9;MENU_NAME_STYLES.forEach(style=>{words.forEach((word,i)=>{let pos=word.indexOf(style);if(pos<0)return;let prefix=word.slice(0,pos),genericPrefix=/^(야채|채소|크림|간장|밥|치즈|두부|계란|고기|닭|밤|어묵|말이)?$/.test(prefix),start=i;if(!prefix||genericPrefix){let max=prefix?1:3,c=0;for(let j=i-1;j>=0&&c<max;j--){if(!menuPrevWord(words[j]))break;start=j;c++}}let cand=words.slice(start,i+1).join(' ').replace(/^(요리\s*)+/,'').trim();if(!cand)return;let specificity=majorTokens(cand).length*6,score=40+style.length*2+(word.length-style.length)*1.5+(i-start)*2+specificity-Math.max(0,cand.length-24)*1.2;if(/요리|메뉴|식단|소스|양념장|방법/.test(cand))score-=15;if(score>bestScore||(score===bestScore&&(!best||cand.length<best.length))){bestScore=score;best=cand}})});return best}
function fallbackTitleCandidate(clean){let segs=String(clean||'').split('§').map(x=>x.trim()).filter(Boolean),best='',score=-1e9;segs.forEach((seg,i)=>{let x=seg.replace(/\s+/g,' ').trim();if(!x||/^(요리|메뉴|식단|간식)$/.test(x))return;let s=majorTokens(x).length*5-Math.max(0,x.length-22)*1.2+i*.2;if(s>score){score=s;best=x}});return best}
function recipeMenuName(r){let raw=String(r?.title||''),clean=cleanRecipeTitle(raw),segments=clean.split('§').map(x=>x.trim()).filter(Boolean),best='',bestScore=-1e9;segments.forEach((seg,i)=>{let cand=dishCandidateFromSegment(seg);if(!cand)return;let sc=majorTokens(cand).length*5-Math.max(0,cand.length-24)+i*.1;if(sc>bestScore){bestScore=sc;best=cand}});return best||fallbackTitleCandidate(clean)||raw}
'''

s = s[:start] + replacement + s[end:]
p.write_text(s, encoding='utf-8')

sw = Path('sw.js')
if sw.exists():
    t = sw.read_text(encoding='utf-8')
    t = re.sub(r'baby-meal-planner-v\d+', 'baby-meal-planner-v13', t)
    sw.write_text(t, encoding='utf-8')
