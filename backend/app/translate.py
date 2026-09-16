"""
프롬프트 번역 (한국어 → 영어).

z-image 를 포함한 대부분의 확산 모델은 영어 캡션으로 학습돼 있어 한국어
프롬프트를 제대로 알아듣지 못한다. 사용자는 한국어로 쓰게 두고, fal 로 나가기
직전에 영어로 바꾼다.

설계상 지켜야 할 것:

  - **한글이 섞여 있을 때만** 호출한다. 영어로 쓴 프롬프트까지 왕복시키면
    비용도 지연도 이유 없이 늘어난다.
  - **실패하면 원문 그대로 통과시킨다.** 번역은 품질을 올리는 보조 장치지
    생성의 전제 조건이 아니다. 번역기가 죽었다고 생성까지 막히면 안 된다.
  - **타임아웃을 짧게 잡는다.** 생성 경로는 이미 fal 호출로 길고, 그 앞단이
    오래 끌면 Cloudflare 무료 플랜의 100초 제한(524)에 먼저 걸린다.

번역 결과는 그대로 fal 프롬프트가 되므로, 앞으로 프롬프트 차단 필터를
넣는다면 원문뿐 아니라 **번역 결과에도** 걸어야 한다. 영어 차단어 목록은
한국어 원문에 반응하지 않는다.
"""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from typing import Optional

import httpx

from .config import settings

logger = logging.getLogger(__name__)

# 한글 음절(가–힣) 과 자모. 하나라도 있으면 번역 대상으로 본다.
_HANGUL = re.compile(r"[가-힣ㄱ-ㆎ]")

# 모델이 "Here is the translation:" 같은 군말을 붙이는 경우를 걷어낸다.
_PREAMBLE = re.compile(
    r"^\s*(here\s+is\s+[^:]*:|translation\s*:|영어\s*:|번역\s*:)\s*",
    re.IGNORECASE,
)

_INSTRUCTION = (
    "You rewrite image-generation prompts into English.\n"
    "Rules:\n"
    "1. Output ONLY the rewritten prompt. No preamble, no quotes, no explanation.\n"
    "2. NEVER introduce the subject. Do not begin with or insert 'a woman', "
    "'a man', 'a girl', 'a person', 'she', 'he' or any similar wording, even if "
    "it sounds more natural. The subject's gender, age and nationality are added "
    "separately before your text — if you name a subject it can contradict them.\n"
    "3. Describe only what the user described: clothing, pose, place, time of day, "
    "mood, camera framing. Keep every concrete detail.\n"
    "4. Write it as comma-separated descriptive phrases, not a full sentence.\n"
    "5. Do not add nudity, brands, or written text that the user did not ask for.\n"
    "6. If the input is already English, return it unchanged.\n"
    "\n"
    "Example:\n"
    "  input : 노을 지는 바닷가에서 흰 원피스 입고\n"
    "  output: wearing a white dress, standing on a beach at sunset, "
    "golden hour lighting, warm tones\n"
)


def contains_korean(text: Optional[str]) -> bool:
    """한글이 하나라도 들어 있는지."""
    return bool(text) and bool(_HANGUL.search(text))


def to_english_prompt(text: str) -> str:
    """
    한국어 프롬프트를 영어로 바꿔 돌려준다.

    번역이 필요 없거나(영문 입력·기능 꺼짐) 실패하면 **원문을 그대로** 돌려준다.
    호출부는 반환값을 그냥 쓰면 되고, 예외를 처리할 필요가 없다.
    """
    if not text or not text.strip():
        return text
    if settings.TRANSLATE_PROVIDER.strip().lower() != "gemini":
        return text
    if not contains_korean(text):
        return text
    if not settings.GEMINI_API_KEY:
        # 키 없이 켜둔 설정 실수. 생성을 막을 일은 아니라 경고만 남긴다.
        logger.warning("TRANSLATE_PROVIDER=gemini 인데 GEMINI_API_KEY 가 비어 있어 번역을 건너뜁니다.")
        return text

    try:
        translated = _translate_cached(text.strip())
    except Exception as exc:  # noqa: BLE001 - 어떤 실패든 원문으로 폴백한다
        logger.warning("프롬프트 번역 실패, 원문으로 진행합니다: %s", exc)
        return text

    # 번역이 의도대로 됐는지는 로그로만 확인할 수 있다 (생성 결과만 봐서는
    # 프롬프트가 어떻게 나갔는지 알 수 없다). 이용자 입력이 남는 지점이므로,
    # 남기고 싶지 않으면 .env 의 LOG_LEVEL 을 WARNING 으로 올리면 된다.
    logger.info("프롬프트 번역: %s → %s", _clip(text), _clip(translated))
    return translated


def _clip(text: str, limit: int = 120) -> str:
    """로그 한 줄이 길어지지 않게 자른다."""
    one_line = " ".join(text.split())
    return one_line if len(one_line) <= limit else one_line[:limit] + "…"


@lru_cache(maxsize=512)
def _translate_cached(text: str) -> str:
    """
    같은 프롬프트를 반복 번역하지 않는다.

    크리에이터가 템플릿에 묶어 배포한 리딤 코드는 팬 여러 명이 같은 프롬프트로
    생성하므로 적중률이 높다. 프로세스 로컬이라 재시작하면 비워진다.
    """
    translated = _call_gemini(text)
    return translated or text


def _call_gemini(text: str) -> Optional[str]:
    """Gemini 로 번역. 실패는 예외로 올려 호출부가 원문 폴백하게 한다."""
    url = (
        f"{settings.GEMINI_API_BASE_URL}/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": _INSTRUCTION}]},
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "generationConfig": {
            # 번역은 창작이 아니다. 낮게 잡아 같은 입력에 같은 결과가 나오게 한다.
            "temperature": 0.2,
            "maxOutputTokens": 512,
        },
    }
    with httpx.Client(timeout=settings.TRANSLATE_TIMEOUT_SECONDS) as client:
        response = client.post(
            url,
            json=payload,
            headers={
                # 키를 쿼리스트링에 넣으면 프록시·액세스 로그에 그대로 남는다.
                "x-goog-api-key": settings.GEMINI_API_KEY,
                "Content-Type": "application/json",
            },
        )
    if response.status_code >= 400:
        raise RuntimeError(f"Gemini {response.status_code}: {response.text[:200]}")

    data = response.json()
    candidates = data.get("candidates") or []
    if not candidates:
        # 안전 필터에 걸리면 candidates 가 비어 온다. 차단 사유를 남겨 추적 가능하게.
        raise RuntimeError(f"번역 결과 없음: {str(data.get('promptFeedback'))[:200]}")

    parts = (candidates[0].get("content") or {}).get("parts") or []
    out = "".join(p.get("text", "") for p in parts).strip()
    if not out:
        return None

    out = _PREAMBLE.sub("", out).strip().strip('"').strip()
    return out or None


if __name__ == "__main__":
    # 크레딧을 쓰지 않고 번역만 확인하는 진단용 진입점.
    #   docker compose -f docker-compose.prod.yml exec backend \
    #     python -m app.translate "노을 지는 바닷가에서 흰 원피스 입고"
    # 설정이 맞는지(키·모델·네트워크) 이미지 생성 전에 가려낼 수 있다.
    import sys

    sample = " ".join(sys.argv[1:]) or "노을 지는 바닷가에서 흰 원피스 입고"

    print(f"provider : {settings.TRANSLATE_PROVIDER}")
    print(f"model    : {settings.GEMINI_MODEL}")
    print(f"key      : {'설정됨' if settings.GEMINI_API_KEY else '(비어 있음)'}")
    print(f"한글 포함 : {contains_korean(sample)}")
    print(f"입력     : {sample}")

    result = to_english_prompt(sample)
    print(f"출력     : {result}")

    if result == sample:
        print(
            "\n원문이 그대로 나왔습니다. 위의 provider/key/한글 포함 값을 보세요.\n"
            "  - provider 가 none  → .env 에 TRANSLATE_PROVIDER=gemini\n"
            "  - key 가 비어 있음   → .env 에 GEMINI_API_KEY\n"
            "  - 한글 포함 False    → 영어 입력이라 번역 대상이 아님 (정상)\n"
            "  - 셋 다 정상인데 같다 → 위에 찍힌 경고 로그에서 실패 사유 확인"
        )
    else:
        print("\n번역이 동작합니다.")
