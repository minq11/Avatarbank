"""
고객 문의 라우터.

- 공개: POST /inquiries — 고객지원 페이지 폼. 비로그인도 접수 가능(레이트리밋).
- 관리자: GET /admin/inquiries, POST /admin/inquiries/{id}/reply — 문의 확인 후 답장.

메일은 베스트 에포트(mailer.send_email). SMTP 미설정/실패여도 문의는 DB 에 남아
관리자 페이지에서 확인할 수 있다. 답장은 메일 발송이 성공해야 answered 로 바꾼다
(발송 실패했는데 "답변 완료"로 보이면 안 되므로).
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .dependencies import get_current_user_optional, require_admin
from .mailer import send_email
from .models import Inquiry, InquiryStatus, User
from .rate_limit import rate_limit_inquiry
from .schemas import (
    AdminInquiryResponse,
    InquiryCreateRequest,
    InquiryCreateResponse,
    InquiryReplyRequest,
)

router = APIRouter(tags=["inquiries"])

CATEGORY_LABELS_KO = {
    "account": "계정/로그인",
    "avatar": "아바타 등록·학습",
    "generation": "생성/쿼터",
    "code": "리딤 링크",
    "billing": "결제/구독",
    "report": "신고 (도용·권리침해)",
    "etc": "기타",
}


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _to_response(row: Inquiry) -> AdminInquiryResponse:
    return AdminInquiryResponse(
        id=row.id,
        user_id=row.user_id,
        name=row.name,
        email=row.email,
        category=row.category,
        subject=row.subject,
        message=row.message,
        status=row.status,
        reply_body=row.reply_body,
        replied_at=row.replied_at,
        notified_at=row.notified_at,
        created_at=row.created_at,
    )


@router.post(
    "/inquiries",
    response_model=InquiryCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_inquiry)],
)
def create_inquiry(
    payload: InquiryCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> InquiryCreateResponse:
    """고객지원 폼 접수. 저장 후 내부 알림 메일을 베스트 에포트로 보낸다."""
    inquiry = Inquiry(
        user_id=current_user.id if current_user else None,
        name=payload.name,
        email=str(payload.email),
        category=payload.category,
        subject=payload.subject,
        message=payload.message,
        status=InquiryStatus.OPEN.value,
        client_ip=_client_ip(request),
    )
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)

    category_label = CATEGORY_LABELS_KO.get(inquiry.category, inquiry.category)
    body = (
        f"[AvatarClub] 새 문의가 접수됐습니다.\n\n"
        f"문의번호: #{inquiry.id}\n"
        f"분류: {category_label}\n"
        f"이름: {inquiry.name}\n"
        f"회신 주소: {inquiry.email}\n"
        f"회원: {'회원 #' + str(inquiry.user_id) if inquiry.user_id else '비회원'}\n"
        f"접수 시각(UTC): {inquiry.created_at:%Y-%m-%d %H:%M}\n\n"
        f"제목: {inquiry.subject}\n\n"
        f"{inquiry.message}\n\n"
        f"— 관리자 페이지(/admin/inquiries)에서 답장할 수 있습니다."
    )
    sent = send_email(
        to=settings.INQUIRY_NOTIFY_EMAIL,
        subject=f"[문의 #{inquiry.id}] {inquiry.subject}",
        body=body,
        reply_to=inquiry.email,
    )
    if sent:
        inquiry.notified_at = datetime.utcnow()
        db.commit()

    return InquiryCreateResponse(id=inquiry.id, status=inquiry.status, email_sent=sent)


@router.get("/admin/inquiries", response_model=List[AdminInquiryResponse], tags=["admin"])
def admin_list_inquiries(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> List[AdminInquiryResponse]:
    """문의 목록 (최신순). status=open/answered/closed 로 필터."""
    query = db.query(Inquiry)
    if status_filter:
        query = query.filter(Inquiry.status == status_filter)
    rows = query.order_by(Inquiry.created_at.desc()).limit(300).all()
    return [_to_response(r) for r in rows]


@router.post(
    "/admin/inquiries/{inquiry_id}/reply",
    response_model=AdminInquiryResponse,
    tags=["admin"],
)
def admin_reply_inquiry(
    inquiry_id: int,
    payload: InquiryReplyRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AdminInquiryResponse:
    """문의자에게 답장 메일 발송 후 answered 로 표시."""
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if inquiry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="문의를 찾을 수 없어요.")

    body = (
        f"{inquiry.name}님, 안녕하세요. AvatarClub 고객지원입니다.\n\n"
        f"{payload.reply_body}\n\n"
        f"────────────────────\n"
        f"[문의 #{inquiry.id}] {inquiry.subject}\n"
        f"{inquiry.message}\n"
        f"────────────────────\n"
        f"이 메일에 그대로 회신하시면 담당자에게 전달됩니다."
    )
    sent = send_email(
        to=inquiry.email,
        subject=f"[AvatarClub] 문의 #{inquiry.id} 답변드립니다 — {inquiry.subject}",
        body=body,
        reply_to=settings.INQUIRY_NOTIFY_EMAIL,
    )
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="메일 발송에 실패했어요. SMTP 설정을 확인해 주세요.",
        )

    inquiry.reply_body = payload.reply_body
    inquiry.replied_at = datetime.utcnow()
    inquiry.replied_by_id = admin.id
    inquiry.status = InquiryStatus.ANSWERED.value
    db.commit()
    db.refresh(inquiry)
    return _to_response(inquiry)


@router.post(
    "/admin/inquiries/{inquiry_id}/close",
    response_model=AdminInquiryResponse,
    tags=["admin"],
)
def admin_close_inquiry(
    inquiry_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> AdminInquiryResponse:
    """답장 없이 종료 (스팸 등)."""
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if inquiry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="문의를 찾을 수 없어요.")
    inquiry.status = InquiryStatus.CLOSED.value
    db.commit()
    db.refresh(inquiry)
    return _to_response(inquiry)
