"""
결제 적립 회귀 테스트.

포트원은 결제창이 닫힌 시점에 **이미 승인이 끝나 있다.** 서버가 하는 일은
승인이 아니라 검증이고, 검증 뒤의 적립은 `_grant_once` 하나에 모여 있다.
이 함수가 깨지면 두 가지 사고 중 하나가 난다:

  - 두 번 적립 → 돈은 한 번 받고 크레딧은 두 배 (손실)
  - 한 번도 적립 안 됨 → 돈만 받고 크레딧 없음 (환불 + 신뢰 손상)

complete 와 webhook 이 같은 결제 건에 동시에/연달아 들어오는 건 정상 경로다
(성공 페이지 새로고침, 포트원 웹훅 재전송). 그래서 "중복 호출해도 한 번만
적립된다"가 여기서 가장 중요한 성질이다.

엔드포인트 자체(HTTP 계층)는 여기서 테스트하지 않는다. 금액 검증과 취소는
포트원 API 왕복이 섞여 있어 통합 테스트 영역이고, 돈이 실제로 틀어지는
지점은 아래 순수 함수들이다.
"""

import pytest

from app.credits import balance
from app.models import (
    CreditOrder,
    CreditOrderStatus,
    Transaction,
    TransactionType,
)
from app.payments import _grant_once, _paid_total


@pytest.fixture()
def make_order(db):
    """주문 팩토리. 기본은 9,000원 / 100크레딧 (pack100)."""

    def _make(
        user,
        *,
        status: str = CreditOrderStatus.PENDING.value,
        credits: int = 100,
        amount_krw: int = 9_000,
        order_id: str = "ab-test-order",
    ) -> CreditOrder:
        order = CreditOrder(
            order_id=order_id,
            user_id=user.id,
            pack_code="pack100",
            pack_name="100장",
            credits=credits,
            amount_krw=amount_krw,
            status=status,
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    return _make


def _payment(total: int = 9_000, **extra) -> dict:
    """포트원 결제 조회 응답의 최소 형태."""
    payload = {
        "id": "ab-test-order",
        "status": "PAID",
        "transactionId": "tx-abc123",
        "amount": {"total": total},
        "method": {"type": "PaymentMethodEasyPay", "provider": "KAKAOPAY"},
    }
    payload.update(extra)
    return payload


# ---------------------------------------------------------------------------
# 적립 (성공 경로)
# ---------------------------------------------------------------------------


def test_대기중_주문은_적립되고_paid_로_바뀐다(db, user, make_order):
    order = make_order(user)

    assert _grant_once(db, order, _payment(), allow_revive=False) is True
    db.commit()
    db.refresh(order)

    assert order.status == CreditOrderStatus.PAID.value
    assert balance(db, user.id) == 100
    assert order.approved_at is not None


def test_결제_식별자와_수단이_주문에_기록된다(db, user, make_order):
    """CS 문의나 대조 때 포트원 쪽 건을 찾을 수 있어야 한다."""
    order = make_order(user)
    payment = _payment()

    _grant_once(db, order, payment, allow_revive=False)
    db.commit()
    db.refresh(order)

    assert order.payment_key == "tx-abc123"
    assert order.method == "PaymentMethodEasyPay"
    assert order.raw_response == payment


def test_transactionId_가_없으면_id_를_쓴다(db, user, make_order):
    order = make_order(user)
    payment = _payment()
    payment.pop("transactionId")

    _grant_once(db, order, payment, allow_revive=False)
    db.commit()
    db.refresh(order)

    assert order.payment_key == "ab-test-order"


def test_method_형태가_달라도_터지지_않는다(db, user, make_order):
    """포트원 응답 형태가 바뀌어도 적립 자체는 막히면 안 된다."""
    order = make_order(user)

    assert _grant_once(db, order, _payment(method="EASY_PAY"), allow_revive=False) is True
    db.commit()
    db.refresh(order)

    assert order.method is None
    assert balance(db, user.id) == 100


def test_적립_기록이_주문번호로_추적_가능하다(db, user, make_order):
    order = make_order(user)
    _grant_once(db, order, _payment(), allow_revive=False)
    db.commit()

    tx = db.query(Transaction).filter(Transaction.user_id == user.id).one()
    assert tx.type == TransactionType.PURCHASE.value
    assert tx.amount == 100
    assert tx.reference_id == order.order_id


def test_주문에_박힌_크레딧_수로_적립한다(db, user, make_order):
    """
    팩 가격이 나중에 바뀌어도 주문 시점 값으로 지급된다.
    포트원 응답에는 크레딧 수가 없으므로 기준은 항상 주문 행이다.
    """
    order = make_order(user, credits=1000, amount_krw=70_000)

    _grant_once(db, order, _payment(total=70_000), allow_revive=False)
    db.commit()

    assert balance(db, user.id) == 1000


# ---------------------------------------------------------------------------
# 멱등성 (가장 중요한 성질)
# ---------------------------------------------------------------------------


def test_두_번_호출해도_한_번만_적립된다(db, user, make_order):
    order = make_order(user)

    assert _grant_once(db, order, _payment(), allow_revive=False) is True
    db.commit()
    assert _grant_once(db, order, _payment(), allow_revive=False) is False
    db.commit()

    assert balance(db, user.id) == 100
    assert db.query(Transaction).filter(Transaction.user_id == user.id).count() == 1


def test_이미_paid_인_주문은_웹훅_경로에서도_적립되지_않는다(db, user, make_order):
    """
    complete 로 적립이 끝난 뒤 웹훅이 뒤늦게 들어오는 건 정상 경로다.
    allow_revive=True 여도 PAID 는 제외되므로 이중 적립이 없어야 한다.
    """
    order = make_order(user)
    _grant_once(db, order, _payment(), allow_revive=False)
    db.commit()

    assert _grant_once(db, order, _payment(), allow_revive=True) is False
    db.commit()

    assert balance(db, user.id) == 100


def test_웹훅이_여러_번_와도_한_번만_적립된다(db, user, make_order):
    order = make_order(user)

    results = [_grant_once(db, order, _payment(), allow_revive=True) for _ in range(5)]
    db.commit()

    assert results == [True, False, False, False, False]
    assert balance(db, user.id) == 100


# ---------------------------------------------------------------------------
# 되살리기 (allow_revive)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "dead_status",
    [CreditOrderStatus.CANCELED.value, CreditOrderStatus.FAILED.value],
)
def test_취소_실패_주문은_complete_경로에서_되살아나지_않는다(
    db, user, make_order, dead_status
):
    order = make_order(user, status=dead_status)

    assert _grant_once(db, order, _payment(), allow_revive=False) is False
    db.commit()
    db.refresh(order)

    assert order.status == dead_status
    assert balance(db, user.id) == 0


@pytest.mark.parametrize(
    "dead_status",
    [CreditOrderStatus.CANCELED.value, CreditOrderStatus.FAILED.value],
)
def test_취소_실패_주문도_웹훅_경로에서는_되살린다(db, user, make_order, dead_status):
    """
    사용자가 창을 닫아 로컬에서 취소로 표시됐지만 실제로는 결제가 완료된 경우.
    웹훅은 포트원에 직접 물어 확인한 뒤 들어오므로 되살려야 한다.
    되살리지 않으면 돈만 받고 크레딧을 안 주는 상태가 된다.
    """
    order = make_order(user, status=dead_status)

    assert _grant_once(db, order, _payment(), allow_revive=True) is True
    db.commit()
    db.refresh(order)

    assert order.status == CreditOrderStatus.PAID.value
    assert balance(db, user.id) == 100


def test_되살린_주문도_두_번은_적립되지_않는다(db, user, make_order):
    order = make_order(user, status=CreditOrderStatus.CANCELED.value)

    assert _grant_once(db, order, _payment(), allow_revive=True) is True
    db.commit()
    assert _grant_once(db, order, _payment(), allow_revive=True) is False
    db.commit()

    assert balance(db, user.id) == 100


def test_적립은_주문_소유자에게만_들어간다(db, make_user, make_order):
    owner = make_user("owner@example.com", "owner")
    other = make_user("other@example.com", "other")
    order = make_order(owner)

    _grant_once(db, order, _payment(), allow_revive=False)
    db.commit()

    assert balance(db, owner.id) == 100
    assert balance(db, other.id) == 0


# ---------------------------------------------------------------------------
# 금액 파싱 — 금액 검증의 입력이므로 여기가 틀리면 검증이 통째로 무력해진다
# ---------------------------------------------------------------------------


def test_결제_총액을_정수로_꺼낸다():
    assert _paid_total({"amount": {"total": 9000}}) == 9000


def test_문자열_금액도_정수로_해석한다():
    assert _paid_total({"amount": {"total": "9000"}}) == 9000


@pytest.mark.parametrize(
    "payment",
    [
        {},                                  # amount 없음
        {"amount": None},                    # null
        {"amount": 9000},                    # dict 가 아님
        {"amount": {}},                      # total 없음
        {"amount": {"total": None}},         # total 이 null
        {"amount": {"total": "구천원"}},      # 숫자가 아님
    ],
)
def test_형태가_다르면_None_을_돌려준다(payment):
    """
    None 은 호출부에서 "금액 불일치" 로 처리돼 결제가 자동 취소된다.
    0 이나 예외가 아니라 None 이어야 한다 — 0 을 돌려주면 0원 주문이
    통과할 여지가 생기고, 예외는 500 이 되어 취소 로직을 건너뛴다.
    """
    assert _paid_total(payment) is None
