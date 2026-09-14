import re

DISH_STYLES = [
    '크림리조또','리조또','볶음밥','비빔밥','덮밥','주먹밥','밥전','김밥','진밥','영양밥','계란말이밥','달걀말이밥',
    '계란찜','달걀찜','계란말이','달걀말이','동그랑땡','닭갈비','떡갈비','불고기','장조림','두부조림','감자조림','메추리알조림',
    '된장국','미역국','무국','계란국','달걀국','배추국','국밥','냉국','수제비','칼국수','국수','우동','대구탕','탕',
    '오트밀','팬케이크','핫케이크','케이크','쿠키','비스켓','비스킷','피자','토스트','샌드위치','오믈렛','프리타타','그라탕','카레','파스타',
    '밥머핀','머핀','계란빵','분유빵','쌀빵','감자빵','빵','에그슬럿','무스롤','롤','카레볼','치즈볼','볼',
    '라구소스','타르타르소스','커스타드크림','크림','수프','스프','스튜','수육','완자','만두','찐빵','잡채','나물','샐러드','또띠아','타코야키','김치','쌈',
    '생선가스','가스','호떡','딤섬','매시스틱','스틱','튀김','겉절이','부침','소보루','스크램블','강정','말랭이','부각',
    '조림','찜','구이','무침','볶음','전','죽','국','밥'
]

INGREDIENTS = [
    '소고기','쇠고기','닭고기','닭안심','닭가슴살','돼지고기','계란','달걀','두부','연어','대구','명태','흰살생선','생선','새우','오징어','참치',
    '감자','고구마','단호박','애호박','호박','브로콜리','당근','시금치','양배추','배추','버섯','양송이','표고','팽이','새송이','가지','무','미역','오이','연근','콩나물','청경채','양파','대파','옥수수','완두콩','밤','김','어묵',
    '사과','배','바나나','딸기','키위','복숭아','블루베리','요거트','치즈','우유','오트밀','쌀','밥','면','빵','메추리알','토마토','파프리카','아보카도','부추','콩','서리태','다시마','귤','맛살','소세지','소시지'
]

MODIFIERS = {
    '야채','채소','크림','간장','치즈','버터','우유','된장','토마토','카레','참깨','들깨','김','밤','어묵','말이','미니','두부','계란','달걀','고기','닭','소고기','쇠고기','돼지고기','새우','생선','연어','감자','고구마','단호박','애호박','브로콜리','당근','시금치','양배추','배추','버섯','양송이','표고','사과','바나나','부추','콩','서리태','다시마','마파두부','라구','타르타르','귤','맛살','소세지','소시지'
}

NOISE_WORDS = {
    '요리','메뉴','식단','소스','양념','양념장','방법','법','추천','특식','반찬','간식','레시피','황금레시피','보관','활용','초기','중기','후기','완료기',
    '아기','유아','유아식','아이','키즈','돌아기','두돌아기','돌전','돌이후','엄마표','초간단','간단','간단한','간편','간편한','전자레인지','에어프라이어','노오븐','베이킹',
    '한그릇','한끼','뚝딱','뚝딱한','완료','완성','먹는','먹기','잘먹는','잘','쉽게','간단히','맛있게','맛있는','가득','가득한','고소함이',
    '시원한','구수한','고소한','담백한','부드러운','촉촉한','든든한','건강한','영양만점','영양가득','맑은','상큼한','달콤','짭짤','바삭','극강의','아이들이','아이가','아기는','온가족이','온가족',
    '넣어','넣고','넣은','삶은','삶아','삶고','끓여','끓인','끓이고','볶아','볶은','볶고','구워','구운','섞어','섞은','섞고','부어','부은','담아','담은',
    '만들어','만든','만들고','만들어요','만드는','해주세요','해요','먹어요','먹어','준비해요','완성해요','반죽','반죽을','재료','ver','feat','no','NO','정말','너무','좋아하는','걱정'
}

PARTICLES = ['으로','에서','에게','이랑','하고','랑','로','와','과','이','가','은','는','을','를','의','에','도','만']
VERB_ENDINGS = ('어요','아요','해요','합니다','세요','습니다','는다','한다','하기','하는','해서','하고','하며','되어','되는','입니다','랍니다','죠','네요','봐요','주세요')
SEPARATORS = re.compile(r'[|/:;,·ㆍ~!?#♡♥★☆▶▷→←+=_\-]+')
BRACKETS = re.compile(r'\([^)]*\)|\[[^\]]*\]|\{[^}]*\}')
NOISE_PREFIXES = ('시원한','구수한','고소한','담백한','부드러운','촉촉한','든든한','건강한','맑은','상큼한','달콤한','맛있는')


def _has_dish_ending(word: str) -> bool:
    w = str(word or '').strip()
    return any(w.endswith(s) for s in DISH_STYLES)


def _ingredient_match(word: str) -> bool:
    w = str(word or '').strip()
    if not w or w[0].isdigit():
        return False
    for k in sorted(INGREDIENTS, key=len, reverse=True):
        if len(k) <= 1:
            if w == k or w.endswith(k):
                return True
        elif k in w:
            return True
    return False


def _strip_particle(word: str) -> str:
    x = str(word or '').strip()
    # Never strip a real dish ending such as 계란말이.
    if _has_dish_ending(x):
        return x
    for p in PARTICLES:
        if len(x) > len(p) + 1 and x.endswith(p):
            base = x[:-len(p)]
            if _ingredient_match(base) or base in MODIFIERS:
                return base
    return x


def _is_noise(word: str) -> bool:
    w = _strip_particle(word)
    if not w or w in NOISE_WORDS:
        return True
    if w.endswith('요리') and not _has_dish_ending(w):
        return True
    if any(w.endswith(e) for e in VERB_ENDINGS):
        return True
    if w.startswith(('만드는','만들기','넣어서','넣으면','삶아서','끓여서','볶아서','구워서','섞어서','활용해','준비해')):
        return True
    return False


def _clean_title(title: str) -> str:
    x = BRACKETS.sub(' ', str(title or ''))
    x = re.sub(r'\b\d+\s*개월\b', ' ', x)
    x = re.sub(r'(?:돌아기|두돌아기|아기|유아|아이|키즈)(?:들이|에게|랑|와|가|는|은|을|를|의|도|만)?', ' ', x)
    x = re.sub(r'(?:유아식|아기반찬|유아반찬|아이반찬|어린이반찬|무염반찬|특식)', ' ', x)
    x = re.sub(r'(?:양념장\s*)?(?:만드는\s*법|만드는법|만드는\s*방법|만들기)|황금레시피|레시피|엄마표|초간단|간단하게|한\s*그릇|한그릇|한\s*끼|한끼|뚝딱(?:한)?', ' ', x)
    x = SEPARATORS.sub(' § ', x)
    return re.sub(r'\s+', ' ', x).strip()


def _is_food_word(word: str) -> bool:
    w = _strip_particle(word)
    if _is_noise(w):
        return False
    return _ingredient_match(w) or w in MODIFIERS


def _sanitize(text: str) -> str:
    words = re.sub(r'[^가-힣A-Za-z0-9\s]', ' ', str(text or '')).split()
    out = []
    for word in words:
        w = _strip_particle(word)
        if _is_noise(w):
            continue
        if w not in out:
            out.append(w)
    keep = []
    for i, w in enumerate(out):
        if any(i != j and len(z) > len(w) and w in z and not _has_dish_ending(w) for j, z in enumerate(out)):
            continue
        keep.append(w)
    return ' '.join(keep).strip()


def _find_style(token: str):
    safe = _sanitize(token)
    if not safe:
        return None
    matches = [s for s in DISH_STYLES if safe.endswith(s)]
    return max(matches, key=len) if matches else None


def _clean_anchor_token(token: str, style: str) -> str:
    safe = _sanitize(token)
    if not safe or not style or not safe.endswith(style):
        return safe
    prefix = safe[:-len(style)]
    changed = True
    while changed and prefix:
        changed = False
        for p in NOISE_PREFIXES:
            if prefix.startswith(p):
                prefix = prefix[len(p):]
                changed = True
                break
    return (prefix + style).strip()


def _style_candidates(segment: str):
    words = segment.split()
    candidates = []
    for i, raw in enumerate(words):
        style = _find_style(raw)
        if not style:
            continue
        anchor = _clean_anchor_token(raw, style)
        pos = anchor.rfind(style)
        start = i
        prefix = anchor[:pos]
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
        parts = words[start:i] + [anchor]
        cand = _sanitize(' '.join(parts))
        if not cand:
            continue
        ingredient_hits = sum(1 for k in INGREDIENTS if k in cand)
        score = 100 + len(style) * 4 + ingredient_hits * 8 + min(len(prefix), 8) * 2 - max(0, len(cand) - 24) * 2
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

    exact = [str(x).strip() for x in (recipe.get('exact') or []) if str(x).strip()]
    exact_styles = []
    for x in exact:
        st = _find_style(x)
        if st:
            exact_styles.append(st)
    if exact_styles:
        style = max(exact_styles, key=len)
        parts = []
        for x in exact:
            if x == style or _is_noise(x):
                continue
            if _ingredient_match(x) and x not in parts:
                parts.append(x)
        if parts:
            return _sanitize(' '.join(parts[:3] + [style]))

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
    if name and name != '추천 메뉴' and not _has_dish_ending(name):
        reasons.append('no_dish_anchor')
    if name and name[0].isdigit():
        reasons.append('starts_number')
    return sorted(set(reasons))
