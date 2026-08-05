"""
프롬프트 필터 훅.

현재 아무것도 차단하지 않는다 — 모든 프롬프트를 통과시킨다.
필터 정책은 서비스 운영자가 직접 정의한다.

연결 지점: 생성 경로 전체가 assert_sfw_prompt() 를 이미 호출하고 있으므로
(main.py 1곳, studio.py 4곳 — 크리에이터 생성 / 팬 리딤 생성 포함),
아래 check_prompt() 에 원하는 로직만 채우면 전 경로에 한 번에 적용된다.
"""

from typing import Optional, Tuple


def check_prompt(text: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    (ok, matched_term) 반환. ok=False 면 차단, matched_term 은 사유 표시용.

    현재는 전부 통과. 필터를 넣으려면 여기에 구현할 것.
    """
    return True, None


def assert_sfw_prompt(text: Optional[str]) -> None:
    """check_prompt 가 False 를 반환하면 HTTP 400 을 던진다."""
    from fastapi import HTTPException, status

    ok, term = check_prompt(text)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이 프롬프트는 허용되지 않아요.",
        )
