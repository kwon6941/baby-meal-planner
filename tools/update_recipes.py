#!/usr/bin/env python3
import json, re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from menu_name_utils import derive_menu_name

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'recipes.json'
UA={'User-Agent':'Mozilla/5.0 (compatible; BabyMealRecipeUpdater/3.0; +https://github.com/)'}
TIMEOUT=8
MAX_RECIPES=300
PAGES_PER_QUERY=4
LIST_WORKERS=16
DETAIL_WORKERS=14

QUERIES=[
'돌아기 유아식','돌아기 유아식 반찬','돌아기 반찬','돌아기 밥','돌아기 한그릇',
'아기 유아식','아기 유아식 반찬','아기 반찬','아기 밥','아기 한그릇',
'유아식 레시피','유아식 반찬','유아식 한그릇','유아식 국','유아식 덮밥','유아식 볶음밥','유아식 조림','유아식 찜','유아식 전','유아식 죽','유아식 리조또','유아식 완자','유아식 떡갈비','유아식 수프','유아식 오트밀',
'12개월 유아식','13개월 유아식','14개월 유아식','15개월 유아식','16개월 유아식','17개월 유아식','18개월 유아식','아이반찬','아이밥','어린이반찬','어린이 밥',
'아기 소고기','아기 닭고기','아기 돼지고기','아기 두부','아기 계란','아기 달걀','아기 연어','아기 흰살생선','아기 생선','아기 새우',
'아기 감자','아기 고구마','아기 단호박','아기 애호박','아기 브로콜리','아기 당근','아기 시금치','아기 양배추','아기 버섯','아기 무',
'아기 미역국','아기 소고기무국','아기 계란찜','아기 두부조림','아기 밥전','아기 볶음밥','아기 덮밥','아기 리조또','아기 국','아기 조림','아기 찜','아기 전','아기 완자','아기 떡갈비','아기 주먹밥',
'아기 오트밀','아기 바나나 오트밀','아기 단호박 오트밀','아기 고구마 오트밀','아기 간식',
'돌아기 소고기 애호박','돌아기 소고기 브로콜리','돌아기 닭고기 감자','돌아기 두부 애호박','돌아기 연어','돌아기 흰살생선','돌아기 소고기 두부','돌아기 닭고기 브로콜리','돌아기 계란 애호박','돌아기 두부 채소',
'유아 소고기','유아 닭고기','유아 두부','유아 계란','유아 생선','유아 채소','유아 국','유아 반찬'
]
CHILD_WORDS=('아기','유아식','유아','돌아기','두돌아기','12개월','13개월','14개월','15개월','16개월','17개월','18개월','아이반찬','아이 밥','아이밥','어린이','키즈')
BLOCK_WORDS=('청양고추','매운','불닭','술안주','소주','맥주','마라','고추장찌개','매콤','얼큰','닭발','곱창','제육','떡볶이','라면','짬뽕','아구찜','매운탕','고추기름')
VOCAB=['소고기','닭고기','돼지고기','계란','달걀','두부','연어','흰살생선','생선','새우','오징어','감자','고구마','단호박','애호박','브로콜리','당근','시금치','양배추','배추','버섯','양송이','가지','무','미역','오이','연근','콩나물','청경채','양파','대파','사과','배','바나나','딸기','키위','복숭아','블루베리','요거트','치즈','우유','오트밀','밥','쌀','면','빵','메추리알']
STYLE_WORDS=['덮밥','볶음밥','리조또','진밥','죽','국','국밥','조림','찜','전','구이','무침','스튜','수육','떡갈비','완자','주먹밥','수프','스프']

def get(url):
    r=requests.get(url,headers=UA,timeout=TIMEOUT)
    r.raise_for_status(); return r.text

def load_existing():
    if not OUT.exists(): return {}
    try:
        d=json.loads(OUT.read_text(encoding='utf-8'))
        return {r['url']:r for r in d.get('recipes',[]) if r.get('url')}
    except Exception: return {}

def list_one(args):
    q,page=args
    url=f'https://www.10000recipe.com/recipe/list.html?q={quote(q)}&page={page}'
    try: html=get(url)
    except Exception: return set()
    out=set()
    for m in re.finditer(r'href=["\'](?:https?://(?:m\.)?10000recipe\.com)?/recipe/(\d+)',html):
        rid=m.group(1)
        if len(rid)>=6: out.add(f'https://www.10000recipe.com/recipe/{rid}')
    return out

def collect_urls():
    jobs=[(q,p) for q in QUERIES for p in range(1,PAGES_PER_QUERY+1)]
    found=set()
    with ThreadPoolExecutor(max_workers=LIST_WORKERS) as ex:
        futs=[ex.submit(list_one,j) for j in jobs]
        for i,f in enumerate(as_completed(futs),1):
            try: found.update(f.result())
            except Exception: pass
            if i%50==0: print('list pages',i,'/',len(jobs),'candidates',len(found),flush=True)
    return list(found)

def jsonld_recipe(soup):
    for tag in soup.find_all('script',type='application/ld+json'):
        txt=tag.string or tag.get_text() or ''
        try: obj=json.loads(txt)
        except Exception: continue
        stack=obj if isinstance(obj,list) else [obj]
        for c in stack:
            if isinstance(c,dict) and c.get('@type')=='Recipe': return c
            if isinstance(c,dict) and isinstance(c.get('@graph'),list):
                for x in c['@graph']:
                    if isinstance(x,dict) and x.get('@type')=='Recipe': return x
    return None

def clean_ing(x):
    return re.sub(r'\s+',' ',str(x)).strip().strip(' -:,[]()')

def parse_recipe(url):
    try: html=get(url)
    except Exception: return None
    soup=BeautifulSoup(html,'html.parser'); ld=jsonld_recipe(soup)
    if ld:
        title=(ld.get('name') or '').strip()
        ings=[clean_ing(x) for x in (ld.get('recipeIngredient') or [])]
        pub=ld.get('datePublished'); mod=ld.get('dateModified')
    else:
        h=soup.select_one('h3') or soup.select_one('title')
        title=h.get_text(' ',strip=True) if h else ''; ings=[]; pub=mod=None
    if not title or not any(w in title for w in CHILD_WORDS): return None
    if any(w in title for w in BLOCK_WORDS): return None
    blob=' '.join([title]+ings); kw=[]
    for w in VOCAB:
        if w in blob:
            w={'달걀':'계란','생선':'흰살생선'}.get(w,w)
            if w not in kw: kw.append(w)
    styles=[w for w in STYLE_WORDS if w in title]
    return {'title':title,'source':'만개의레시피','url':url,'keywords':kw[:12],'exact':(kw[:3]+styles[:1])[:5],'ingredients':ings[:30],'published':pub,'modified':mod,'discovered_at':datetime.now(timezone.utc).isoformat()}

def main():
    existing=load_existing(); print('existing',len(existing),flush=True)
    urls=[u for u in collect_urls() if u not in existing]
    print('candidate urls',len(urls),flush=True)
    added=0; checked=0
    # Process in bounded batches so we can stop as soon as the DB reaches 300.
    for start in range(0,len(urls),120):
        batch=urls[start:start+120]
        with ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as ex:
            futs=[ex.submit(parse_recipe,u) for u in batch]
            for f in as_completed(futs):
                checked+=1
                try: item=f.result()
                except Exception: item=None
                if item and item['url'] not in existing:
                    existing[item['url']]=item; added+=1
                    if len(existing)%25==0: print('accepted',len(existing),flush=True)
        if len(existing)>=MAX_RECIPES: break
    items=list(existing.values())
    for r in items:
        r['menu_name']=derive_menu_name(r)
    items.sort(key=lambda r:(len(r.get('keywords',[])),r.get('modified') or r.get('published') or r.get('discovered_at') or ''),reverse=True)
    items=items[:MAX_RECIPES]
    out={'updated_at':datetime.now(timezone.utc).isoformat(),'recipe_count':len(items),'recipes':items}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print('saved',len(items),'recipes; added',added,'checked',checked,flush=True)

if __name__=='__main__': main()
