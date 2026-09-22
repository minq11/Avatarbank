"""
크레딧 잔액 회귀 테스트.

여기서 막고 싶은 사고는 하나다: **돈으로 산 잔액이 틀리는 것.**
잔액이 음수로 내려가거나, 차감했는데 기록이 안 남거나, 남의 잔액이
깎이는 일이 생기면 사용자에게 설명할 방법이 없다.

Transaction 의 credit_before / credit_after 까지 확인하는 이유:
CS 문의가 들어오면 이 두 값으로 "그때 잔액이 얼마였는지"를 되짚는다.
잔액만 맞고 장부가 틀리면 문의에 답할 수 없으므로 잔액과 같은 급으로 본다.
"""

import pytest

from app.credits import balance, deduct, grant, refund
from app.models import Transaction, TransactionType


def _ledger(db, user_id):
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.id.asc())
        .all()
    )


# ---------------------------------------------------------------------------
# 차감
# ---------------------------------------------------------------------------


def test_차감은_잔액을_줄이고_차감후_잔액을_돌려준다(db, user):
    grant(db, user_id=user.id, amount=10, reason=TransactionType.BONUS)
    db.commit()

    after = deduct(db, user_id=user.id, amount=3)
    db.commit()

    assert after == 7
    assert balance(db, user.id) == 7


def test_잔액이_부족하면_아무것도_바꾸지_않는다(db, user):
    grant(db, user_id=user.id, amount=2, reason=TransactionType.BONUS)
    db.commit()
    before_ledger = len(_ledger(db, user.id))

    assert deduct(db, user_id=user.id, amount=3) is None
    db.commit()

    # 잔액이 음수로 내려가지 않고, 실패한 차감은 장부에도 남지 않는다.
    assert balance(db, user.id) == 2
    assert len(_ledger(db, user.id)) == before_ledger


def test_잔액_전부를_차감해_0_까지는_내려간다(db, user):
    grant(db, user_id=user.id, amount=5, reason=TransactionType.BONUS)
    db.commit()

    assert deduct(db, user_id=user.id, amount=5) == 0
    db.commit()
    assert balance(db, user.id) == 0


def test_잔액_0_에서는_차감이_실패한다(db, user):
    assert deduct(db, user_id=user.id, amount=1) is None
    db.commit()
    assert balance(db, user.id) == 0


def test_없는_사용자_차감은_None(db):
    assert deduct(db, user_id=999_999, amount=1) is None


@pytest.mark.parametrize("amount", [0, -1, -100])
def test_0_이하_차감은_거부한다(db, user, amount):
    # 음수 차감이 통하면 그게 곧 무료 충전이다.
    with pytest.raises(ValueError):
        deduct(db, user_id=user.id, amount=amount)


def test_차감은_다른_사용자_잔액을_건드리지_않는다(db, make_user):
    a = make_user("a@example.com", "a", credit_balance=10)
    b = make_user("b@example.com", "b", credit_balance=10)

    deduct(db, user_id=a.id, amount=4)
    db.commit()

    assert balance(db, a.id) == 6
    assert balance(db, b.id) == 10


# ---------------------------------------------------------------------------
# 적립
# ---------------------------------------------------------------------------


def test_적립은_잔액을_늘린다(db, user):
    assert grant(db, user_id=user.id, amount=30, reason=TransactionType.PURCHASE) == 30
    db.commit()
    assert balance(db, user.id) == 30


def test_적립은_누적된다(db, user):
    grant(db, user_id=user.id, amount=30, reason=TransactionType.PURCHASE)
    grant(db, user_id=user.id, amount=100, reason=TransactionType.PURCHASE)
    db.commit()
    assert balance(db, user.id) == 130


def test_없는_사용자_적립은_None(db):
    assert grant(db, user_id=999_999, amount=10, reason=TransactionType.BONUS) is None


@pytest.mark.parametrize("amount", [0, -1])
def test_0_이하_적립은_거부한다(db, user, amount):
    with pytest.raises(ValueError):
        grant(db, user_id=user.id, amount=amount, reason=TransactionType.BONUS)


def test_생성_실패_환불은_차감을_되돌린다(db, user):
    grant(db, user_id=user.id, amount=5, reason=TransactionType.BONUS)
    deduct(db, user_id=user.id, amount=1, reference_id="gen-1")
    db.commit()
    assert balance(db, user.id) == 4

    assert refund(db, user_id=user.id, amount=1, reference_id="gen-1") == 5
    db.commit()
    assert balance(db, user.id) == 5

    kinds = [t.type for t in _ledger(db, user.id)]
    assert kinds[-1] == TransactionType.REFUND.value


# ---------------------------------------------------------------------------
# 장부 (Transaction)
# ---------------------------------------------------------------------------


def test_차감_기록의_부호와_전후_잔액이_맞는다(db, user):
    grant(db, user_id=user.id, amount=10, reason=TransactionType.PURCHASE)
    deduct(db, user_id=user.id, amount=2, reference_id="gen-7")
    db.commit()

    purchase, generation = _ledger(db, user.id)

    assert purchase.amount == 10
    assert (purchase.credit_before, purchase.credit_after) == (0, 10)
    assert purchase.type == TransactionType.PURCHASE.value

    assert generation.amount == -2
    assert (generation.credit_before, generation.credit_after) == (10, 8)
    assert generation.type == TransactionType.GENERATION.value
    assert generation.reference_id == "gen-7"


def test_장부_통화는_항상_CREDIT(db, user):
    # 마이페이지의 크레딧 내역은 currency == "CREDIT" 으로 걸러 보여준다.
    # 여기가 틀리면 내역이 빈 화면으로 보인다.
    grant(db, user_id=user.id, amount=1, reason=TransactionType.BONUS)
    deduct(db, user_id=user.id, amount=1)
    db.commit()

    assert {t.currency for t in _ledger(db, user.id)} == {"CREDIT"}


def test_장부의_마지막_잔액은_실제_잔액과_같다(db, user):
    grant(db, user_id=user.id, amount=100, reason=TransactionType.PURCHASE)
    for _ in range(7):
        deduct(db, user_id=user.id, amount=1)
    refund(db, user_id=user.id, amount=1)
    db.commit()

    ledger = _ledger(db, user.id)
    assert ledger[-1].credit_after == balance(db, user.id) == 94

    # 장부를 처음부터 더한 값도 잔액과 같아야 한다 (기록 누락 탐지).
    assert sum(t.amount for t in ledger) == balance(db, user.id)


def test_장부는_끊기지_않고_이어진다(db, user):
    """앞 기록의 credit_after 와 다음 기록의 credit_before 가 이어져야 한다."""
    grant(db, user_id=user.id, amount=50, reason=TransactionType.PURCHASE)
    deduct(db, user_id=user.id, amount=3)
    deduct(db, user_id=user.id, amount=1)
    refund(db, user_id=user.id, amount=1)
    db.commit()

    ledger = _ledger(db, user.id)
    for prev, cur in zip(ledger, ledger[1:]):
        assert cur.credit_before == prev.credit_after
