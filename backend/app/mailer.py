"""
SMTP 메일 발송 (고객 문의 접수 알림 / 관리자 답장).

정책: 메일은 "베스트 에포트"다. SMTP 미설정이거나 발송이 실패해도 예외를 밖으로
던지지 않고 False 를 반환한다 — 문의 자체는 DB 에 남고 관리자 페이지에서 볼 수
있어야 하기 때문. 발송 성공 여부는 호출부에서 notified_at 등으로 기록한다.

주의: smtplib 는 동기 블로킹이다. 문의량이 늘면 BackgroundTasks/큐로 옮길 것.
"""

import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from typing import Optional

from .config import settings

logger = logging.getLogger(__name__)


def mail_configured() -> bool:
    """SMTP 설정이 갖춰졌는지 여부."""
    return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD)


def _from_address() -> str:
    return settings.SMTP_FROM or settings.SMTP_USER


def send_email(
    to: str,
    subject: str,
    body: str,
    reply_to: Optional[str] = None,
    from_name: str = "AvatarBank",
) -> bool:
    """평문 메일 1통 발송. 성공 시 True, 미설정/실패 시 False."""
    if not mail_configured():
        logger.warning("SMTP not configured — skipped email to %s (subject=%s)", to, subject)
        return False

    msg = EmailMessage()
    msg["From"] = formataddr((from_name, _from_address()))
    msg["To"] = to
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)

    try:
        if settings.SMTP_USE_TLS:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        return True
    except Exception:
        # 주소/본문은 로그에 남기지 않는다 (개인정보). 예외만 남김.
        logger.exception("Failed to send email (subject=%s)", subject)
        return False
