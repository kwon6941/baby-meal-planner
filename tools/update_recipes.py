#!/usr/bin/env python3
import json, re, time
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"recipes.json"
UA={"User-Agent":"Mozilla/5.0 (compatible; BabyMealRecipeUpdater/1.0; +https://github.com/)"}
TIMEOUT=15
MAX_RECIPES=300
QUERIES=['돌아기유아식', '돌아기유아식반찬', '아기유아식', '13개월유아식', '14개월유아식', '아기유아식소고기', '아기유아식닭고기', '아기유아식두부', '아기유아식계란', '아기유아식연어', '아기유아식흰살생선', '돌아기오트밀', '아기유아식감자', '돌아기 소고기 애호박 덮밥', '돌아기 소고기 브로콜리 덮밥', '돌아기 닭고기 감자 조림', '돌아기 두부 애호박 전', '돌아기 연어 리조또', '돌아기 흰살생선 전', '돌아기 소고기 두부 국', '돌아기 닭고기 브로콜리 덮밥', '돌아기 계란 애호박 국', '돌아기 연어 감자', '돌아기 두부 채소 찜', '돌아기 바나나 오트밀', '돌아기 단호박 오트밀', '돌아기 계란 채소찜', '돌아기 소고기 미역국', '돌아기 소고기 무국', '돌아기 볶음밥', '돌아기 두부조림', '돌아기 계란찜', '돌아기 밥전', '돌아기 완자', '돌아기 떡갈비', '유아식 브로콜리 두부', '유아식 소고기 애호박', '유아식 닭고기 감자', '유아식 연어', '유아식 한그릇 덮밥']
PAGES_PER_QUERY=2
CHILD_WORDS=("아기","유아식","돌아기","두돌아기","12개월","13개월","14개월","15개월","16개월","17개월","18개월")
BLOCK_WORDS=("청양고추","매운","불닭","술안주","소주","맥주","마라","고추장찌개")
VOCAB=["소고기","닭고기","돼지고기","계란","달걀","두부","연어","흰살생선","생선","새우","오징어","감자","고구마","단호박","애호박","브로콜리","당근","시금치","양배추","배추","버섯","양송이","가지","무","미역","오이","연근","콩나물","청경채","양파","대파","사과","배","바나나","딸기","키위","복숭아","블루베리","요거트","치즈","우유","오트밀","밥","쌀","면","빵","메추리알"]
STYLE_WORDS=["덮밥","볶음밥","리조또","진밥","죽","국","국밥","조림","찜","전","구이","무침","스튜","수육","떡갈비","완자"]
session=requests.Session();session.headers.update(UA)
def fetch(url):
    r=session.get(url,timeout=TIMEOUT);r.raise_for_status();return r.text
def load_existing():
    if not OUT.exists():return {}
    try:
        data=json.loads(OUT.read_text(encoding="utf-8"));return {r["url"]:r for r in data.get("recipes",[]) if r.get("url")}
    except Exception:return {}
def list_recipe_urls():
    found=set()
    for q in QUERIES:
        for page in range(1,PAGES_PER_QUERY+1):
            url=f"https://www.10000recipe.com/recipe/list.html?q={quote(q)}&order=date&page={page}"
            try:html=fetch(url)
            except Exception as e:print("list fail",url,e);continue
            for m in re.finditer(r'href=["\'](?:https?://(?:m\.)?10000recipe\.com)?/recipe/(\d+)',html):
                rid=m.group(1)
                if len(rid)>=6:found.add(f"https://www.10000recipe.com/recipe/{rid}")
            time.sleep(.25)
    return sorted(found)
def find_recipe_jsonld(soup):
    for tag in soup.find_all("script",type="application/ld+json"):
        txt=tag.string or tag.get_text() or ""
        try:obj=json.loads(txt)
        except Exception:continue
        candidates=obj if isinstance(obj,list) else [obj]
        for c in candidates:
            if isinstance(c,dict) and c.get("@type")=="Recipe":return c
            if isinstance(c,dict) and isinstance(c.get("@graph"),list):
                for x in c["@graph"]:
                    if isinstance(x,dict) and x.get("@type")=="Recipe":return x
    return None
def canonical_ingredient(s):
    s=re.sub(r"\s+"," ",str(s)).strip();return s.strip(" -:,[]()")
def parse_recipe(url):
    try:html=fetch(url)
    except Exception as e:print("detail fail",url,e);return None
    soup=BeautifulSoup(html,"html.parser");ld=find_recipe_jsonld(soup)
    if ld:
        title=(ld.get("name") or "").strip();ingredients=[canonical_ingredient(x) for x in (ld.get("recipeIngredient") or [])];ingredients=[x for x in ingredients if x];published=ld.get("datePublished");modified=ld.get("dateModified")
    else:
        h=soup.select_one("h3") or soup.select_one("title");title=h.get_text(" ",strip=True) if h else "";ingredients=[];published=modified=None
    if not title or not any(w in title for w in CHILD_WORDS):return None
    if any(w in title for w in BLOCK_WORDS):return None
    blob=" ".join([title]+ingredients);keywords=[]
    for w in VOCAB:
        if w in blob:
            w={"달걀":"계란","생선":"흰살생선"}.get(w,w)
            if w not in keywords:keywords.append(w)
    exact=[w for w in STYLE_WORDS if w in title];exact=keywords[:3]+exact[:1]
    return {"title":title,"source":"만개의레시피","url":url,"keywords":keywords[:12],"exact":exact[:5],"ingredients":ingredients[:30],"published":published,"modified":modified,"discovered_at":datetime.now(timezone.utc).isoformat()}
def main():
    existing=load_existing();urls=list_recipe_urls();print("candidate urls",len(urls));added=0
    for url in urls:
        if url in existing:continue
        item=parse_recipe(url)
        if item:existing[url]=item;added+=1;print("+",item["title"])
        if len(existing)>=MAX_RECIPES:break
        time.sleep(.2)
    items=list(existing.values());items.sort(key=lambda r:(len(r.get("keywords",[])),r.get("modified") or r.get("published") or ""),reverse=True);items=items[:MAX_RECIPES]
    out={"updated_at":datetime.now(timezone.utc).isoformat(),"recipe_count":len(items),"recipes":items};OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8");print("saved",len(items),"recipes; added",added)
if __name__=="__main__":main()
