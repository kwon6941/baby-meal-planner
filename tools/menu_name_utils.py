import re

DISH_STYLES = [
    '크림리조또','리조또','볶음밥','비빔밥','덮밥','주먹밥','밥전','김밥','진밥','영양밥',
    '계란찜','달걀찜','동그랑땡','닭갈비','떡갈비','장조림','두부조림','감자조림','메추리알조림',
    '된장국','미역국','무국','계란국','달걀국','국밥','냉국','수제비','칼국수','국수','우동',
    '오트밀','팬케이크','핫케이크','토스트','샌드위치','오믈렛','그라탕','카레','파스타',
    '수프','스프','스튜','수육','완자','만두','잡채','나물','샐러드','또띠아',
    '조림','찜','구이','무침','볶음','전','죽','국','밥'
]

INGREDIENTS = [
    '소고기','쇠고기','닭고기','닭안심','닭가슴살','돼지고기','계란','달걀','두부','연어','대구','명태','흰살생선','생선','새우','오징어','참치',
    '감자','고구마','단호박','애호박','호박','브로콜리','당근','시금치','양배추','배추','버섯','양송이','표고','팽이','새송이','가지','무','미역','오이','연근','콩나물','청경채','양파','대파','옥수수','완두콩','밤','김','어묵',
    '사과','배','바나나','딸기','키위','복숭아','블루베리','요거트','치즈','우유','오트밀','쌀','밥','면','빵','메추리알','토마토','파프리카','아보카도'
]

MODIFIERS = {
    '야채','채소','크림','간장','치즈','버터','우유','된장','토마토','카레','참깨','들깨','김','밤','어묵','말이','미니','두부','계란','달걀','고기','닭','소고기','돼지고기','새우','생선','연어','감자','고구마','단호박','애호박','브로콜리','당근','시금치','양배추','배추','버섯','양송이','표고','사과','바나나'
}

NOISE_WORDS = {
    '요리','메뉴','식단','소스','양념','양념장','방법','법','추천','특식','반찬','간식','레시피','황금레시피',
    '아기','유아','유아식','아이','키즈','돌아기','두돌아기','돌전','돌이후','엄마표','초간단','간단','간단한',
    '한그릇','한끼','뚝딱','뚝딱한','완료','완성','먹는','먹기','잘먹는','잘','쉽게','간단히','맛있게','맛있는',
    '시원한','고소한','담백한','부드러운','촉촉한','든든한','건강한','영양만점','영양가득','아이들이','아이가','아기는',
    '넣어','넣고','넣은','삶은','삶아','삶고','끓여','끓인','끓이고','볶아','볶은','볶고','구워','구운','섞어','섞은','섞고',
    '만들어','만든','만들고','만들어요','만드는','해주세요','해요','먹어요','먹어','준비해요','완성해요','반죽','반죽을','재료','활용'
}

PARTICLES = ['으로','에서','에게','이랑','하고','랑','로','와','과','이','가','은','는','을','를','의','에','도','만']
VERB_ENDINGS = ('어요','아요','해요','합니다','합니다','세요','세요','습니다','는다','한다','하기','하는','해서','하고','하며','되어','되는','입니다','랍니다','죠','네요')
ADJ_ENDINGS = ('한','로운')
SEPARATORS = re.compile(r'[|/:;,·ㆍ~!?#♡♥★☆▶▷→←+=_\-]+')
BRACKETS = re.compile(r'\([^)]*\)|\[[^\]]*\]|\{[^}]*\}')


def _strip_particle(word: str) -> str:
    x = str(word or '').strip()
    for p in PARTICLES:
        if len(x) > len(p) + 1 and x.endswith(p):
            base = x[:-len(p)]
            if any(k in base for k in INGREDIENTS) or base in MODIFIERS:
                return base
    return x


def _is_noise(word: str) -> bool:
    w = _strip_particle(word)
    if not w or w in NOISE_WORDS:
        return True
    if any(w.endswith(e) for e in VERB_ENDINGS):
        return True
    if w.startswith(('만드는','만들기','넣어서','넣으면','삶아서','끓여서','볶아서','구워서','섞어서')):
        return True
    if w in {'시원','고소','담백','부드럽게','촉촉하게','든든하게','맛있게'}:
        return True
    return False


def _clean_title(title: str) -> str:
    x = BRACKETS.sub(' ', str(title or ''))
    x = re.sub(r'\b\d+\s*개월\b', ' ', x)
    x = re.sub(r'(?:돌아기|두돌아기|아기|유아|아이|키즈)(?:들이|에게|랑|와|가|는|은|을|를|의|도|만)?', ' ', x)
    x = re.sub(r'(?:유아식|아기반찬|유아반찬|아이반찬|무염반찬|특식)', ' ', x)
    x = re.sub(r'(?:양념장\s*)?(?:만드는\s*법|만드는법|만드는\s*방법|만들기)|황금레시피|레시피|엄마표|초간단|간단하게|한\s*그릇|한그릇|한\s*끼|한끼|뚝딱(?:한)?', ' ', x)
    x = SEPARATORS.sub(' § ', x)
    return re.sub(r'\s+', ' ', x).strip()


def _is_food_word(word: str) -> bool:
    w = _strip_particle(word)
    if _is_noise(w):
        return False
    if any(k in w for k in INGREDIENTS):
        return True
    if w in MODIFIERS:
        return True
    return False


def _sanitize(text: str) -> str:
    words = re.sub(r'[^가-힣A-Za-z0-9\s]', ' ', str(text or '')).split()
    out = []
    for word in words:
        w = _strip_particle(word)
        if _is_noise(w):
            continue
        if w not in out:
            out.append(w)
    # Remove redundant token if another token already contains it (e.g. 시금치 + 시금치크림리조또)
    keep = []
    for i, w in enumerate(out):
        if any(i != j and len(z) > len(w) and w in z for j, z in enumerate(out)):
            continue
        keep.append(w)
    return ' '.join(keep).strip()


def _style_candidates(segment: str):
    words = segment.split()
    candidates = []
    for i, raw in enumerate(words):
        safe = _sanitize(raw)
        if not safe:
            continue
        for style in DISH_STYLES:
            pos = safe.find(style)
            if pos < 0:
                continue
            # Keep the anchor token itself. Its prefix is often the real dish name: 감자수제비, 마파두부덮밥, 간장닭갈비.
            start = i
            prefix = safe[:pos]
            # If the anchor has little/no specific prefix, collect up to 3 food-like tokens immediately before it.
            if not prefix or prefix in MODIFIERS or prefix in {'야채','채소','크림','간장','치즈','된장'}:
                kept = 0
                for j in range(i - 1, -1, -1):
                    if words[j] == '§':
                        break
                    if _is_food_word(words[j]):
                        start = j
                        kept += 1
                        if kept >= 3:
                            break
                    elif _is_noise(words[j]):
                        continue
                    else:
                        break
            cand = _sanitize(' '.join(words[start:i+1]))
            if not cand:
                continue
            ingredient_hits = sum(1 for k in INGREDIENTS if k in cand)
            noise_penalty = sum(1 for w in cand.split() if _is_noise(w))
            score = 100 + len(style) * 3 + ingredient_hits * 8 + min(len(prefix), 8) * 2 - noise_penalty * 50 - max(0, len(cand) - 24) * 2
            candidates.append((score, len(cand), cand, style))
    return candidates


def derive_menu_name(recipe: dict) -> str:
    title = str(recipe.get('title') or '').strip()
    clean = _clean_title(title)
    segments = [s.strip() for s in clean.split('§') if s.strip()]
    candidates = []
    for seg in segments:
        candidates.extend(_style_candidates(seg))
    if candidates:
        candidates.sort(key=lambda x: (-x[0], x[1]))
        return candidates[0][2]

    # Use exact metadata if it contains a known style.
    exact = [str(x).strip() for x in (recipe.get('exact') or []) if str(x).strip()]
    style = next((s for s in DISH_STYLES if any(s in x for x in exact)), '')
    if style:
        parts = []
        for x in exact:
            if x == style or _is_noise(x):
                continue
            if any(k in x for k in INGREDIENTS) and x not in parts:
                parts.append(x)
        if parts:
            return _sanitize(' '.join(parts[:3] + [style]))

    # Last-resort title fallback: only keep food-like words; avoid sentence fragments.
    food = []
    for seg in segments:
        for w in seg.split():
            x = _strip_particle(w)
            if _is_food_word(x) and x not in food:
                food.append(x)
    if food:
        return _sanitize(' '.join(food[:4]))
    return '추천 메뉴'


def audit_reason(menu_name: str) -> list[str]:
    reasons = []
    name = str(menu_name or '')
    if not name or name == '추천 메뉴':
        reasons.append('no_menu_name')
    if re.search(r'[/|:;,·ㆍ~!?#♡♥★☆▶▷→←+=_\[\](){}]', name):
        reasons.append('symbol')
    words = name.split()
    if any(_is_noise(w) for w in words):
        reasons.append('noise_word')
    if any(w in {'이','가','은','는','을','를','의','에','에서','로','으로','와','과','도','만','랑','하고'} for w in words):
        reasons.append('particle')
    if any(w.endswith(VERB_ENDINGS) for w in words):
        reasons.append('sentence_ending')
    if len(name) > 28:
        reasons.append('too_long')
    if not any(style in name for style in DISH_STYLES) and len(words) > 3:
        reasons.append('no_style_long')
    return reasons
