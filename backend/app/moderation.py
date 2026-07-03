"""
프롬프트 모더레이션 (SFW 가드).

정책: 팬/크리에이터가 자유 프롬프트를 쓸 수 있으나, fal 호출 *전에* 명백한
NSFW/성적 프롬프트를 1차로 거른다. (fal 의 enable_safety_checker 는 결과 이미지
나체 감지기일 뿐이라 프롬프트 단계 방어가 별도로 필요.)

주의: 아래 워드리스트는 MVP용 기본 방어선이다. 운영 단계에서는 전용 모더레이션
API(OpenAI moderation, fal content-safety 등)로 교체/보강할 것.
"""

import re
from typing import Optional, Tuple

# 명백한 성적/노출 관련 차단어 (영문). 오탐 줄이려 단어 경계로 매칭.
_BLOCKED_WORDS_EN = [
    "nude", "nudes", "naked", "nsfw", "porn", "porno", "pornographic",
    "nipple", "nipples", "areola", "cleavage", "topless", "bottomless",
    "sex", "sexual", "sexy", "erotic", "erotica", "explicit", "lewd",
    "genital", "genitalia", "penis", "vagina", "vulva", "pussy", "cock",
    "boobs", "breast", "breasts", "tits", "titties", "butt", "buttocks",
    "ass", "anal", "cum", "cumshot", "orgasm", "masturbate", "masturbating",
    "fellatio", "blowjob", "handjob", "hentai", "bdsm", "fetish", "bikini",
    "lingerie", "underwear", "panties", "thong", "upskirt", "camel toe",
    "onlyfans", "nsfl", "gore", "child", "loli", "shota", "minor",
    "undress", "undressed", "undressing",
]

# 성적/불법 관련 차단어 (한글, 부분 문자열 매칭).
_BLOCKED_SUBSTR_KO = [
    "누드", "나체", "알몸", "벗은", "벗기", "야한", "야짤", "음란", "성적",
    "섹스", "섹시", "에로", "포르노", "야동", "노출", "젖꼭지", "유두",
    "가슴노출", "속옷", "란제리", "비키니", "성기", "자위", "아동", "미성년",
]

# 다중 단어 명시 표현 (영문, 부분 문자열).
_BLOCKED_SUBSTR_EN = [
    "no clothes", "without clothes", "see through", "see-through",
    "sexual act", "nsfw content", "adult content",
]

_WORD_RE = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in _BLOCKED_WORDS_EN) + r")\b",
    re.IGNORECASE,
)

# --- 난독화 우회 방어 ---------------------------------------------------------
# "n.u.d.e", "p0rn", "s-e-x-y" 같은 leet/구분자 우회를 잡기 위해
# 텍스트를 정규화(leet 치환 + 구분자 제거)한 뒤 부분 문자열로 검사한다.
# 오탐을 줄이기 위해 4자 이상 & 일반 단어에 잘 안 섞이는 고신뢰 표현만 사용.
_LEET_MAP = str.maketrans({
    "@": "a", "4": "a", "3": "e", "1": "i", "!": "i",
    "0": "o", "5": "s", "$": "s", "7": "t",
})
_SEP_RE = re.compile(r"[\s\.\-_\*\+,/\\|~`'\"()\[\]{}]+")

_BLOCKED_COMPACT = [
    # "undress" 류는 sundress 오탐이 있어 여기서 제외 (단어 경계 리스트에서 처리)
    "nude", "naked", "nsfw", "porn", "sexy", "topless", "bottomless",
    "nipple", "areola", "genital", "blowjob", "handjob", "hentai",
    "masturbat", "cumshot", "orgasm", "onlyfans", "fellatio", "erotic",
    "upskirt", "lingerie", "boobs", "titties",
    "noclothes", "withoutclothes", "seethrough",
]


def _compact(text: str) -> str:
    """소문자화 + leet 치환 + 구분자 제거."""
    return _SEP_RE.sub("", text.lower().translate(_LEET_MAP))


def check_prompt(text: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    (ok, matched_term) 반환.
    ok=False 이면 차단해야 하며 matched_term 에 걸린 표현이 담긴다.
    """
    if not text:
        return True, None
    lowered = text.lower()

    m = _WORD_RE.search(lowered)
    if m:
        return False, m.group(1)

    for term in _BLOCKED_SUBSTR_EN:
        if term in lowered:
            return False, term
    for term in _BLOCKED_SUBSTR_KO:
        if term in text:
            return False, term

    # 난독화 우회 검사 (leet/구분자 제거 후)
    compacted = _compact(text)
    for term in _BLOCKED_COMPACT:
        if term in compacted:
            return False, term

    return True, None


def assert_sfw_prompt(text: Optional[str]) -> None:
    """차단어가 있으면 HTTP 400 을 던진다."""
    from fastapi import HTTPException, status

    ok, term = check_prompt(text)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This prompt isn't allowed. Please keep it safe-for-work.",
        )
