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
