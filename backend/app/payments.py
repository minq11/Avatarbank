"""
크레딧 팩 결제 (포트원 PortOne V2).

흐름:
  1) POST /payments/portone/prepare  — 서버가 paymentId 와 금액을 확정해 CreditOrder(pending) 저장
  2) 프론트가 PortOne.requestPayment() 로 결제창을 띄운다
  3) POST /payments/portone/complete — 서버가 포트원 결제 조회 API 로 실제 상태·금액을
                                       확인하고, 주문 금액과 맞으면 크레딧 적립
  4) POST /payments/portone/webhook  — complete 가 유실된 경우를 위한 상태 보정

토스 직연동과 결정적으로 다른 점:
  토스는 서버가 승인(confirm)을 호출해야 결제가 확정되고, 호출하지 않으면 자동 취소됐다.
  포트원은 **결제창이 끝난 시점에 이미 승인이 끝나 있다.** 서버가 하는 일은 승인이 아니라
  검증이다. 그래서 금액이 어긋나면 "승인하지 않으면 그만"이 아니라 **이미 빠져나간 돈을
  취소 API 로 되돌려야** 한다. 이걸 빼먹으면 돈은 받고 크레딧은 안 주는 상태가 된다.

보안상 절대 어기지 말 것:
  - 결제 금액은 클라이언트가 보낸 값이 아니라 CreditOrder.amount_krw 와
    포트원 조회 응답의 amount.total 을 대조해 검증한다.
    클라이언트 값을 믿으면 70,000원 팩을 100원에 사는 게 가능하다.
  - PORTONE_API_SECRET 은 서버에서만 쓴다. 프론트에는 STORE_ID / CHANNEL_KEY 만 내려간다.
  - 적립은 pending → paid 조건부 UPDATE 가 1행을 바꿨을 때만 한다 (멱등성).
    complete 재호출이나 웹훅 중복 수신으로 크레딧이 두 번 들어가는 걸 막는 유일한 장치다.
  - 웹훅 본문은 신뢰하지 않는다. 공개 URL 이라 누구나 위조할 수 있으므로,
    paymentId 만 꺼내 포트원에 직접 되물어 확인한 응답으로만 적립한다.
    (포트원 문서가 서명 검증과 동등하게 인정하는 전략이다)
"""

import secrets
from datetime import datetime
from typing import Any, List, Optional
from urllib.parse import quote

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
    PaymentCompleteRequest,
    PaymentPrepareRequest,
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


def _portone_headers() -> dict:
    """포트원 V2 인증. 토큰 교환 없이 API Secret 을 그대로 쓴다."""
    if not settings.PORTONE_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="결제가 아직 설정되지 않았어요. 잠시 후 다시 시도해 주세요.",
        )
    return {
        "Authorization": f"PortOne {settings.PORTONE_API_SECRET}",
        "Content-Type": "application/json",
    }


def _generate_order_id(db: Session) -> str:
    """
    포트원 paymentId 로 쓸 유니크 주문번호.

    token_urlsafe 는 '-' 와 '_' 만 섞이므로 URL 경로에 그대로 넣어도 안전하다.
    (그래도 조회 시에는 quote() 로 한 번 더 감싼다)
    """
    for _ in range(20):
        candidate = f"ab-{secrets.token_urlsafe(16)}"
        if not db.query(CreditOrder).filter(CreditOrder.order_id == candidate).first():
            return candidate
    raise HTTPException(status_code=500, detail="주문번호 생성에 실패했어요.")


def _fetch_portone_payment(payment_id: str) -> dict:
    """
    포트원에서 결제 건을 조회한다. 결제 상태·금액 판단은 오직 이 응답만 신뢰한다.
    실패는 호출부가 상황에 맞게 처리하도록 예외로 올린다.
    """
    with httpx.Client(timeout=30) as client:
        response = client.get(
            f"{settings.PORTONE_API_BASE_URL}/payments/{quote(payment_id, safe='')}",
            headers=_portone_headers(),
        )
    if response.status_code >= 400:
        raise RuntimeError(_extract_portone_error(response))
    return response.json()


def _cancel_portone_payment(payment_id: str, reason: str) -> Optional[str]:
    """
    이미 승인된 결제를 되돌린다. 실패 사유를 문자열로 돌려주고, 성공하면 None.

    금액이 어긋난 결제를 그냥 두면 돈은 빠져나가고 크레딧은 안 들어간 상태가 된다.
    취소 자체가 실패할 수도 있으므로(네트워크·PG 정책) 호출부는 반드시 사유를
    주문에 기록해 수동 처리가 가능하게 남겨야 한다.
    """
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{settings.PORTONE_API_BASE_URL}/payments/{quote(payment_id, safe='')}/cancel",
                json={"reason": reason},
                headers=_portone_headers(),
            )
    except httpx.HTTPError as exc:
        return f"취소 요청 실패: {exc}"
    if response.status_code >= 400:
        return f"취소 거절: {_extract_portone_error(response)}"
    return None


def _grant_once(db: Session, order: CreditOrder, payment: dict, *, allow_revive: bool) -> bool:
    """
    조건부 UPDATE 로 주문을 paid 로 바꾸고, 실제로 바뀐 경우에만 크레딧을 적립한다.
    동시에 두 번 들어와도 UPDATE 는 한 번만 성공하므로 이중 적립이 없다.

    allow_revive=True 면 취소·실패로 표시된 주문도 되살린다. 웹훅 전용 경로에서만
    쓴다 — 포트원에 직접 물어 결제가 완료된 걸 확인한 상황이므로, 사용자가 창을
    닫아 로컬에서 취소 처리된 건이라도 적립해야 돈만 받는 상태를 피할 수 있다.
    PAID 는 어느 쪽이든 제외되므로 이중 적립은 여전히 불가능하다.
    """
    guard = (
        CreditOrder.status != CreditOrderStatus.PAID.value
        if allow_revive
        else CreditOrder.status == CreditOrderStatus.PENDING.value
    )
    method = payment.get("method") or {}
    marked = db.execute(
        update(CreditOrder)
        .where(CreditOrder.id == order.id, guard)
        .values(
            status=CreditOrderStatus.PAID.value,
            payment_key=payment.get("transactionId") or payment.get("id"),
            method=method.get("type") if isinstance(method, dict) else None,
            raw_response=payment,
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
    return bool(marked)


def _paid_total(payment: dict) -> Optional[int]:
    """포트원 응답에서 실제 결제된 총액을 꺼낸다. 형태가 다르면 None."""
    amount = payment.get("amount")
    if not isinstance(amount, dict):
        return None
    total = amount.get("total")
    try:
        return int(total)
    except (TypeError, ValueError):
        return None


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


@router.post("/payments/portone/prepare", response_model=CreditOrderResponse)
def prepare_payment(
    payload: PaymentPrepareRequest,
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
        order_name=f"아바타클럽 크레딧 {pack.name}",
        amount_krw=order.amount_krw,
        credits=order.credits,
        status=order.status,
        store_id=settings.PORTONE_STORE_ID,
        channel_key=settings.PORTONE_CHANNEL_KEY,
        redirect_url=settings.PAYMENT_SUCCESS_URL,
    )


@router.post("/payments/portone/complete", response_model=MyCreditsResponse)
def complete_payment(
    payload: PaymentCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MyCreditsResponse:
    """
    결제창이 끝난 뒤 서버가 결제를 검증하고 크레딧을 적립한다.

    포트원에서는 이 시점에 이미 승인이 끝나 있다. 여기서 하는 일은 승인이 아니라
    "의도한 주문이 맞는지" 확인이며, 어긋나면 이미 나간 돈을 취소해야 한다.
    """
    order = (
        db.query(CreditOrder)
        .filter(CreditOrder.order_id == payload.payment_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없어요.")
    if order.user_id != current_user.id:
        # 남의 주문을 완료 처리해 자기 잔액에 적립하는 시도를 막는다.
        raise HTTPException(status_code=403, detail="본인의 주문이 아니에요.")

    # 이미 처리된 주문이면 다시 조회하지 않고 현재 잔액만 돌려준다
    # (성공 페이지 새로고침·중복 요청 대비).
    if order.status == CreditOrderStatus.PAID.value:
        return _my_credits_payload(db, current_user.id)

    # pending 이 아닌 주문(취소·실패)은 여기서 되살리지 않는다.
    # 실제로 결제가 완료된 건이라면 웹훅이 포트원에 직접 확인한 뒤 되살린다.
    if order.status != CreditOrderStatus.PENDING.value:
        raise HTTPException(
            status_code=409,
            detail="이미 종료된 주문이에요. 다시 시도하거나 고객센터로 문의해 주세요.",
        )

    try:
        payment = _fetch_portone_payment(order.order_id)
    except (httpx.HTTPError, RuntimeError) as exc:
        # 조회 실패는 결제 상태를 알 수 없는 상태다. pending 으로 남겨
        # 웹훅이 보정하게 하고, 사용자에게는 재시도를 안내한다.
        order.fail_reason = f"포트원 결제 조회 실패: {exc}"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="결제 확인에 실패했어요. 잠시 후 결제 내역을 확인해 주세요.",
        )

    # 금액 검증: 클라이언트가 보낸 값이 아니라 주문 시점에 서버가 박아둔 금액과
    # 포트원이 알려준 실제 결제 금액을 대조한다.
    paid_total = _paid_total(payment)
    if paid_total is None or paid_total != int(order.amount_krw):
        order.status = CreditOrderStatus.FAILED.value
        order.raw_response = payment
        reason = f"금액 불일치: 결제 {paid_total} / 주문 {order.amount_krw}"

        # 토스와 달리 이 시점에 결제가 이미 승인돼 있다. 취소하지 않으면
        # 돈만 빠져나간 채로 끝난다.
        cancel_error = _cancel_portone_payment(order.order_id, "결제 금액 불일치")
        order.fail_reason = (
            f"{reason} / 자동취소 실패: {cancel_error} — 수동 취소 필요"
            if cancel_error
            else f"{reason} / 자동취소 완료"
        )
        db.commit()
        raise HTTPException(status_code=400, detail="결제 금액이 주문과 달라요.")

    # 승인 응답이 200 이어도 결제가 끝난 게 아닐 수 있다. 가상계좌는 계좌만 발급된
    # VIRTUAL_ACCOUNT_ISSUED 상태로 돌아오므로, PAID 를 확인하지 않으면 입금 전에
    # 크레딧이 나간다. 완료가 아니면 pending 으로 두고 웹훅이 적립하게 맡긴다.
    if payment.get("status") != "PAID":
        order.raw_response = payment
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="결제가 아직 완료되지 않았어요. 입금이 확인되면 크레딧이 자동으로 들어와요.",
        )

    _grant_once(db, order, payment, allow_revive=False)
    db.commit()

    return _my_credits_payload(db, current_user.id)


@router.post("/payments/portone/webhook", status_code=status.HTTP_200_OK)
async def portone_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    """
    포트원 웹훅. complete 가 끝나지 않은 주문을 보정한다.

    인증 없는 공개 엔드포인트라 본문을 신뢰하지 않는다. paymentId 만 꺼내
    포트원에 직접 되물어 확인한 응답으로만 적립한다. 포트원 문서가 서명 검증과
    동등하게 인정하는 전략이고, Python 용 서버 SDK 가 없어 서명 검증을 직접
    구현하는 것보다 실수할 여지가 적다.
    """
    body = await request.json()
    data = body.get("data") if isinstance(body.get("data"), dict) else {}
    payment_id = data.get("paymentId") or body.get("paymentId")

    # 같은 결제 건에 대해 상태별로 여러 번 올 수 있으므로 상태까지 묶어 중복을 가린다.
    event_id = str(body.get("type") or "") + ":" + str(payment_id or "")
    if not payment_id:
        raise HTTPException(status_code=400, detail="paymentId 가 없어요.")

    # 중복 수신 차단: event_id 유니크 제약에 걸리면 이미 처리한 이벤트다.
    if db.query(PaymentWebhook).filter(PaymentWebhook.event_id == event_id).first():
        return {"status": "duplicate"}

    hook = PaymentWebhook(provider="portone", event_id=event_id, payload=body, status="received")
    db.add(hook)
    db.commit()

    order = db.query(CreditOrder).filter(CreditOrder.order_id == payment_id).first()
    if not order or order.status == CreditOrderStatus.PAID.value:
        hook.status = "ignored"
        db.commit()
        return {"status": "ignored"}

    try:
        payment = _fetch_portone_payment(payment_id)
    except (httpx.HTTPError, RuntimeError) as exc:
        hook.status = "error"
        hook.error_message = str(exc)[:500]
        db.commit()
        return {"status": "error"}

    paid = payment.get("status") == "PAID" and _paid_total(payment) == int(order.amount_krw)
    if not paid:
        hook.status = "ignored"
        db.commit()
        return {"status": "ignored"}

    # 포트원에 직접 물어 PAID 이고 금액도 맞는 걸 확인했으므로, 로컬에서 취소·실패로
    # 표시된 주문도 되살린다 (사용자가 창을 닫아 cancel 됐지만 실제로는 결제가 완료된
    # 경우 — 이걸 막아두면 돈만 받고 크레딧을 안 주는 상태가 된다).
    _grant_once(db, order, payment, allow_revive=True)
    hook.status = "processed"
    hook.processed_at = datetime.utcnow()
    db.commit()
    return {"status": "processed"}


@router.post("/payments/portone/cancel-order", status_code=status.HTTP_204_NO_CONTENT)
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


def _extract_portone_error(response: Any) -> str:
    """포트원 오류 응답에서 사람이 읽을 사유를 뽑는다."""
    try:
        data = response.json()
    except Exception:
        return (response.text or "")[:300] or f"HTTP {response.status_code}"
    if isinstance(data, dict):
        return str(data.get("message") or data.get("type") or data)[:300]
    return str(data)[:300]
