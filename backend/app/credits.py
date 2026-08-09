"""
크레딧 잔액 차감/적립. 1 크레딧 = 이미지 1장.

잔액의 유일한 출처는 User.credit_balance 이고, 모든 변동은 Transaction 에 남긴다.
구독 쿼터(Subscription.quota_remaining)는 폐기했다 — 잔액 소스가 둘이면
어느 쪽을 먼저 쓸지 규칙이 필요해지고 동시성 방어가 두 배로 복잡해진다.

동시성: 잔액 변경은 전부 조건부 UPDATE ... RETURNING 한 방으로 처리한다.
읽고-검사하고-쓰는 방식은 동시 요청 두 개가 같은 잔액을 읽어 각자 차감하면
잔액이 음수로 내려간다. 호출부의 사전 잔액 체크는 UX용 fast-fail 일 뿐,
최종 방어선은 여기다.

commit 은 호출자 몫이다 (생성 로직이 Generation 저장과 같은 트랜잭션에 묶기 때문).
"""

from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .models import Transaction, TransactionType, User


def deduct(
    db: Session,
    *,
    user_id: int,
    amount: int = 1,
    reason: TransactionType = TransactionType.GENERATION,
    reference_id: Optional[str] = None,
) -> Optional[int]:
    """
    잔액에서 amount 를 원자적으로 차감하고 차감 후 잔액을 돌려준다.
    잔액이 부족하면 아무것도 바꾸지 않고 None (호출부가 409/400 으로 변환).
    """
    if amount <= 0:
        raise ValueError("amount must be positive")

    stmt = (
        update(User)
        .where(User.id == user_id, User.credit_balance >= amount)
        .values(credit_balance=User.credit_balance - amount)
        .returning(User.credit_balance)
    )
    row = db.execute(stmt).first()
    if row is None:
        return None  # 잔액 부족 (또는 없는 사용자)

    after = int(row[0])
    db.add(
        Transaction(
            user_id=user_id,
            type=reason.value,
            amount=-amount,
            currency="CREDIT",
            credit_before=after + amount,
            credit_after=after,
            reference_id=reference_id,
        )
    )
    return after


def grant(
    db: Session,
    *,
    user_id: int,
    amount: int,
    reason: TransactionType,
    reference_id: Optional[str] = None,
) -> Optional[int]:
    """
    잔액에 amount 를 원자적으로 적립하고 적립 후 잔액을 돌려준다.
    없는 사용자면 None.
    """
    if amount <= 0:
        raise ValueError("amount must be positive")

    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(credit_balance=User.credit_balance + amount)
        .returning(User.credit_balance)
    )
    row = db.execute(stmt).first()
    if row is None:
        return None

    after = int(row[0])
    db.add(
        Transaction(
            user_id=user_id,
            type=reason.value,
            amount=amount,
            currency="CREDIT",
            credit_before=after - amount,
            credit_after=after,
            reference_id=reference_id,
        )
    )
    return after


def refund(
    db: Session,
    *,
    user_id: int,
    amount: int = 1,
    reference_id: Optional[str] = None,
) -> Optional[int]:
    """생성 실패로 차감분을 되돌린다. grant 의 의미만 좁힌 래퍼."""
    return grant(
        db,
        user_id=user_id,
        amount=amount,
        reason=TransactionType.REFUND,
        reference_id=reference_id,
    )


def balance(db: Session, user_id: int) -> int:
    """현재 잔액. ORM 세션 캐시를 타지 않고 DB 값을 직접 읽는다."""
    row = db.execute(
        select(User.credit_balance).where(User.id == user_id)
    ).first()
    return int(row[0]) if row else 0
