"""
간단한 인메모리 레이트리미터 (MVP).

공개 리딤 엔드포인트(/r/*)는 인증이 없어서 코드만 알면 봇/스크립트로
크리에이터 쿼터를 고갈시킬 수 있다. IP당 슬라이딩 윈도우로 제한한다.

주의: 프로세스 로컬 메모리 기반 — uvicorn 워커/인스턴스가 여러 개면
인스턴스별로 따로 계산된다. 운영 규모에서는 Redis 기반으로 교체할 것.
"""

import threading
import time
from collections import deque

from fastapi import HTTPException, Request, status

from .config import settings


class SlidingWindowLimiter:
    """키(IP)당 window_seconds 안에 max_requests 초과 시 차단."""

    def __init__(self, max_requests: int, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.monotonic()

    def allow(self, key: str) -> bool:
        if self.max_requests <= 0:  # 0 = 비활성
            return True
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            self._maybe_cleanup(now, cutoff)
            q = self._hits.get(key)
            if q is None:
                q = deque()
                self._hits[key] = q
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= self.max_requests:
                return False
            q.append(now)
            return True

    def _maybe_cleanup(self, now: float, cutoff: float) -> None:
        """오래된 키 정리 (메모리 누수 방지). 60초마다 한 번."""
        if now - self._last_cleanup < 60.0:
            return
        self._last_cleanup = now
        stale = [k for k, q in self._hits.items() if not q or q[-1] < cutoff]
        for k in stale:
            del self._hits[k]


def _client_ip(request: Request) -> str:
    # 리버스 프록시(nginx) 뒤에서는 X-Forwarded-For 첫 값이 실제 클라이언트 IP.
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


_redeem_info_limiter = SlidingWindowLimiter(settings.REDEEM_INFO_RATE_LIMIT_PER_MINUTE)
_redeem_generate_limiter = SlidingWindowLimiter(settings.REDEEM_GENERATE_RATE_LIMIT_PER_MINUTE)


def rate_limit_redeem_info(request: Request) -> None:
    """GET /r/{code} 등 공개 조회용 레이트리밋 의존성."""
    if not _redeem_info_limiter.allow(_client_ip(request)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again in a minute.",
        )


def rate_limit_redeem_generate(request: Request) -> None:
    """POST /r/{code}/generate 등 쿼터 소모 엔드포인트용 레이트리밋 의존성."""
    if not _redeem_generate_limiter.allow(_client_ip(request)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many generation requests. Please try again in a minute.",
        )


_inquiry_limiter = SlidingWindowLimiter(settings.INQUIRY_RATE_LIMIT_PER_MINUTE)


def rate_limit_inquiry(request: Request) -> None:
    """POST /inquiries — 비로그인도 접수 가능하므로 스팸 방지용으로 낮게 잡는다."""
    if not _inquiry_limiter.allow(_client_ip(request)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="문의가 너무 잦아요. 잠시 후 다시 시도해 주세요.",
        )
