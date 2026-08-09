"""
크레딧 팩 결제 (토스페이먼츠).

흐름:
  1) POST /payments/toss/prepare  — 서버가 orderId 와 금액을 확정해 CreditOrder(pending) 저장
  2) 프론트가 결제위젯을 띄우고, 성공 시 successUrl 로 paymentKey/orderId/amount 수신
  3) POST /payments/toss/confirm  — 서버가 DB 의 금액과 대조한 뒤 토스 승인 API 호출,
                                    성공하면 크레딧 적립
  4) POST /payments/toss/webhook  — 승인 응답이 유실된 경우를 위한 상태 보정

보안상 절대 어기지 말 것:
  - 결제 금액은 클라이언트가 보낸 값이 아니라 CreditOrder.amount_krw 를 기준으로 검증한다.
    클라이언트 값을 그대로 승인에 쓰면 70,000원 팩을 100원에 사는 게 가능하다.
  - TOSS_SECRET_KEY 는 서버에서만 쓴다. 프론트에는 TOSS_CLIENT_KEY 만 내려간다.
  - 적립은 pending → paid 조건부 UPDATE 가 1행을 바꿨을 때만 한다 (멱등성).
    승인 재시도나 웹훅 중복 수신으로 크레딧이 두 번 들어가는 걸 막는 유일한 장치다.
"""

import base64
import secrets
from datetime import datetime
from typing import Any, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import update
from sqlalchemy.orm import Session

from .config import settings
from .credits import grant
from .db import get_db
from .dependencies import get_current_user
from .models import (
    CreditOrder,
    CreditOrderStatus,
    CreditPack,
    PaymentWebhook,
    Transaction,
    TransactionType,
    User,
)
from .schemas import (
    CreditOrderResponse,
    CreditPackResponse,
    MyCreditsResponse,
    OrderIdRequest,
    TossConfirmRequest,
    TossPrepareRequest,
    TransactionResponse,
)

router = APIRouter(tags=["payments"])

# 기본 크레딧 팩. 장당 100원 기준, 대용량일수록 할인.
# 대용량 팩은 크리에이터가 팬 배포용 리딤 링크에 쓰는 수요를 노린 구성이다.
DEFAULT_CREDIT_PACKS = [
    {"code": "pack30", "name": "30장", "credits": 30, "price_krw": 3_000, "sort_order": 0},
    {"code": "pack100", "name": "100장", "credits": 100, "price_krw": 9_000, "sort_order": 1},
    {"code": "pack300", "name": "300장", "credits": 300, "price_krw": 24_000, "sort_order": 2},
    {"code": "pack1000", "name": "1,000장", "credits": 1000, "price_krw": 70_000, "sort_order": 3},
]


def seed_credit_packs(db: Session) -> None:
    """기본 팩이 없으면 생성. 멱등 — 가격 변경은 관리자가 DB 에서 직접 한다."""
    for p in DEFAULT_CREDIT_PACKS:
        if db.query(CreditPack).filter(CreditPack.code == p["code"]).first():
            continue
        db.add(CreditPack(
            code=p["code"], name=p["name"], credits=p["credits"],
            price_krw=p["price_krw"], is_active=True, sort_order=p["sort_order"],
        ))
    db.commit()


def _toss_auth_header() -> dict:
    """토스 인증: 시크릿 키 + ':' 를 base64. 비밀번호 없는 Basic 인증 형태."""
    if not settings.TOSS_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="결제가 아직 설정되지 않았어요. 잠시 후 다시 시도해 주세요.",
        )
    token = base64.b64encode(f"{settings.TOSS_SECRET_KEY}:".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def _generate_order_id(db: Session) -> str:
    """토스 orderId 규격(6~64자, 영문/숫자/-/_)에 맞는 유니크 주문번호."""
    for _ in range(20):
        candidate = f"ab-{secrets.token_urlsafe(16)}"
        if not db.query(CreditOrder).filter(CreditOrder.order_id == candidate).first():
            return candidate
    raise HTTPException(status_code=500, detail="주문번호 생성에 실패했어요.")


# ---------------------------------------------------------------------------
# 조회
# ---------------------------------------------------------------------------


@router.get("/credits/packs", response_model=List[CreditPackResponse])
def list_credit_packs(db: Session = Depends(get_db)) -> List[CreditPackResponse]:
    """판매 중인 크레딧 팩 목록 (공개)."""
    packs = (
        db.query(CreditPack)
        .filter(CreditPack.is_active == True)  # noqa: E712
        .order_by(CreditPack.sort_order.asc())
        .all()
    )
    return [CreditPackResponse.model_validate(p) for p in packs]


@router.get("/my/credits", response_model=MyCreditsResponse)
def get_my_credits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MyCreditsResponse:
    """내 크레딧 잔액 + 최근 변동 내역."""
    return _my_credits_payload(db, current_user.id)


# ---------------------------------------------------------------------------
# 결제
# ---------------------------------------------------------------------------


@router.post("/payments/toss/prepare", response_model=CreditOrderResponse)
def prepare_payment(
    payload: TossPrepareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CreditOrderResponse:
    """
    결제창을 띄우기 전에 주문을 확정한다.
    금액·크레딧 수를 여기서 DB 에 박아두고, 승인 때 이 값과 대조한다.
    """
    pack = (
        db.query(CreditPack)
        .filter(CreditPack.code == payload.pack_code, CreditPack.is_active == True)  # noqa: E712
        .first()
    )
    if not pack:
        raise HTTPException(status_code=404, detail="판매 중인 팩이 아니에요.")

    order = CreditOrder(
        order_id=_generate_order_id(db),
        user_id=current_user.id,
        pack_code=pack.code,
        pack_name=pack.name,
        credits=pack.credits,
        amount_krw=pack.price_krw,
        status=CreditOrderStatus.PENDING.value,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return CreditOrderResponse(
        order_id=order.order_id,
        order_name=f"아바타뱅크 크레딧 {pack.name}",
        amount_krw=order.amount_krw,
        credits=order.credits,
        status=order.status,
        client_key=settings.TOSS_CLIENT_KEY,
        success_url=settings.PAYMENT_SUCCESS_URL,
        fail_url=settings.PAYMENT_FAIL_URL,
    )


@router.post("/payments/toss/confirm", response_model=MyCreditsResponse)
def confirm_payment(
    payload: TossConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MyCreditsResponse:
    """
    토스 결제 승인 + 크레딧 적립.
    이 엔드포인트를 통과해야 실제로 결제가 완료된다 (승인 없이는 취소됨).
    """
    order = (
        db.query(CreditOrder)
        .filter(CreditOrder.order_id == payload.order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없어요.")
    if order.user_id != current_user.id:
        # 남의 주문을 승인해 자기 잔액에 적립하는 시도를 막는다.
        raise HTTPException(status_code=403, detail="본인의 주문이 아니에요.")

    # 이미 처리된 주문이면 재승인하지 않고 현재 잔액만 돌려준다 (새로고침·중복 요청 대비).
    if order.status == CreditOrderStatus.PAID.value:
        return _my_credits_payload(db, current_user.id)

    # pending 이 아닌 주문(취소·실패)은 승인하지 않는다. 승인만 하고 적립은 아래
    # pending 조건부 UPDATE 에서 막히면 "결제는 됐는데 크레딧은 없는" 상태가 된다.
    # 실제로 결제가 완료된 건이라면 웹훅이 토스에 직접 확인한 뒤 되살린다.
    if order.status != CreditOrderStatus.PENDING.value:
        raise HTTPException(
            status_code=409,
            detail="이미 종료된 주문이에요. 다시 시도하거나 고객센터로 문의해 주세요.",
        )

    # 금액 검증: 클라이언트가 보낸 amount 가 아니라 주문 시점에 서버가 박아둔 값과 대조한다.
    if int(payload.amount) != int(order.amount_krw):
        order.status = CreditOrderStatus.FAILED.value
        order.fail_reason = (
            f"금액 불일치: 요청 {payload.amount} / 주문 {order.amount_krw}"
        )
        db.commit()
        raise HTTPException(status_code=400, detail="결제 금액이 주문과 달라요.")

    # 토스 승인 호출. 여기서 실패하면 결제는 자동 취소된다.
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{settings.TOSS_API_BASE_URL}/v1/payments/confirm",
                json={
                    "paymentKey": payload.payment_key,
                    "orderId": order.order_id,
                    "amount": order.amount_krw,
                },
                headers=_toss_auth_header(),
            )
    except httpx.HTTPError as exc:
        # 네트워크 실패는 결제 상태를 알 수 없는 상태다. pending 으로 남겨
        # 웹훅이 보정하게 하고, 사용자에게는 재시도를 안내한다.
        order.fail_reason = f"토스 승인 요청 실패: {exc}"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="결제 확인에 실패했어요. 잠시 후 결제 내역을 확인해 주세요.",
        )

    if response.status_code >= 400:
        detail = _extract_toss_error(response)
        order.status = CreditOrderStatus.FAILED.value
        order.fail_reason = detail
        order.raw_response = _safe_json(response)
        db.commit()
        raise HTTPException(status_code=400, detail=f"결제 승인 실패: {detail}")

    data = response.json()

    # 멱등 적립: pending 인 행만 paid 로 바꾼다. 1행이 바뀌었을 때만 크레딧을 넣는다.
    # 동시에 confirm 이 두 번 들어와도 UPDATE 는 한 번만 성공하므로 이중 적립이 없다.
    marked = db.execute(
        update(CreditOrder)
        .where(
            CreditOrder.id == order.id,
            CreditOrder.status == CreditOrderStatus.PENDING.value,
        )
        .values(
            status=CreditOrderStatus.PAID.value,
            payment_key=payload.payment_key,
            method=data.get("method"),
            raw_response=data,
            approved_at=datetime.utcnow(),
        )
    ).rowcount

    if marked:
        grant(
            db,
            user_id=order.user_id,
            amount=order.credits,
            reason=TransactionType.PURCHASE,
            reference_id=order.order_id,
        )
    db.commit()

    return _my_credits_payload(db, current_user.id)


@router.post("/payments/toss/webhook", status_code=status.HTTP_200_OK)
async def toss_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    """
    토스 웹훅. 승인 응답이 유실돼 confirm 이 끝나지 않은 주문을 보정한다.
    인증이 없는 공개 엔드포인트이므로 본문을 신뢰하지 않고,
    토스 API 로 결제 상태를 되물어 확인한 뒤에만 적립한다.
    """
    body = await request.json()
    event_id = str(body.get("eventId") or body.get("paymentKey") or "")
    if not event_id:
        raise HTTPException(status_code=400, detail="eventId 가 없어요.")

    # 중복 수신 차단: event_id 유니크 제약에 걸리면 이미 처리한 이벤트다.
    if db.query(PaymentWebhook).filter(PaymentWebhook.event_id == event_id).first():
        return {"status": "duplicate"}

    hook = PaymentWebhook(provider="toss", event_id=event_id, payload=body, status="received")
    db.add(hook)
    db.commit()

    order_id = (body.get("data") or body).get("orderId")
    if not order_id:
        hook.status = "ignored"
        db.commit()
        return {"status": "ignored"}

    order = db.query(CreditOrder).filter(CreditOrder.order_id == order_id).first()
    if not order or order.status == CreditOrderStatus.PAID.value:
        hook.status = "ignored"
        db.commit()
        return {"status": "ignored"}

    # 웹훅 본문 대신 토스에 직접 조회해서 실제 승인 여부·금액을 확인한다.
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{settings.TOSS_API_BASE_URL}/v1/payments/orders/{order_id}",
                headers=_toss_auth_header(),
            )
    except httpx.HTTPError as exc:
        hook.status = "error"
        hook.error_message = str(exc)
        db.commit()
        return {"status": "error"}

    if response.status_code >= 400:
        hook.status = "error"
        hook.error_message = _extract_toss_error(response)
        db.commit()
        return {"status": "error"}

    data = response.json()
    paid = data.get("status") == "DONE" and int(data.get("totalAmount") or 0) == int(order.amount_krw)
    if not paid:
        hook.status = "ignored"
        db.commit()
        return {"status": "ignored"}

    # 토스에 직접 물어 DONE 이고 금액도 맞는 걸 확인했으므로, 로컬에서 취소·실패로
    # 표시된 주문도 되살린다 (사용자가 창을 닫아 cancel 했지만 실제로는 결제가
    # 완료된 경우 — 이걸 막아두면 돈만 받고 크레딧을 안 주는 상태가 된다).
    # PAID 만 제외하면 이중 적립은 여전히 불가능하다.
    marked = db.execute(
        update(CreditOrder)
        .where(
            CreditOrder.id == order.id,
            CreditOrder.status != CreditOrderStatus.PAID.value,
        )
        .values(
            status=CreditOrderStatus.PAID.value,
            payment_key=data.get("paymentKey"),
            method=data.get("method"),
            raw_response=data,
            approved_at=datetime.utcnow(),
        )
    ).rowcount
    if marked:
        grant(
            db,
            user_id=order.user_id,
            amount=order.credits,
            reason=TransactionType.PURCHASE,
            reference_id=order.order_id,
        )
    hook.status = "processed"
    hook.processed_at = datetime.utcnow()
    db.commit()
    return {"status": "processed"}


@router.post("/payments/toss/cancel-order", status_code=status.HTTP_204_NO_CONTENT)
def cancel_pending_order(
    payload: OrderIdRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """사용자가 결제창을 닫았을 때 pending 주문을 정리한다."""
    order = (
        db.query(CreditOrder)
        .filter(
            CreditOrder.order_id == payload.order_id,
            CreditOrder.user_id == current_user.id,
            CreditOrder.status == CreditOrderStatus.PENDING.value,
        )
        .first()
    )
    if order:
        order.status = CreditOrderStatus.CANCELED.value
        db.commit()


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _my_credits_payload(db: Session, user_id: int) -> MyCreditsResponse:
    from .credits import balance as read_balance

    rows = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.currency == "CREDIT")
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
        .limit(30)
        .all()
    )
    return MyCreditsResponse(
        balance=read_balance(db, user_id),
        transactions=[TransactionResponse.model_validate(t) for t in rows],
    )


def _safe_json(response: Any) -> Optional[dict]:
    try:
        data = response.json()
        return data if isinstance(data, dict) else {"raw": data}
    except Exception:
        return None


def _extract_toss_error(response: Any) -> str:
    """토스 오류 응답에서 사람이 읽을 사유를 뽑는다."""
    try:
        data = response.json()
    except Exception:
        return (response.text or "")[:300] or f"HTTP {response.status_code}"
    if isinstance(data, dict):
        return str(data.get("message") or data.get("code") or data)[:300]
    return str(data)[:300]
