"""
회원 탈퇴 엔드포인트 통합 테스트.

test_account_delete.py 는 파기 함수 하나씩을 본다. 여기서는 HTTP 로 들어와
한 트랜잭션으로 커밋되기까지의 전체 경로를 본다 — 확인 문구 검증, 관리자
차단, 커밋 후 실제로 로그인이 막히는지.

주의: TestClient 를 with 블록 없이 쓴다. 컨텍스트로 열면 startup 이벤트가
돌면서 운영 DB(engine)에 create_all 을 시도한다. 여기서는 테스트용 SQLite
세션만 주입하면 되므로 lifespan 을 태우지 않는다.
"""

import pytest
from fastapi.testclient import TestClient

from app import account as account_mod
from app.db import get_db
from app.dependencies import get_current_user
from app.main import app
from app.models import (
    Avatar,
    CreditOrder,
    CreditOrderStatus,
    Generation,
    Transaction,
    TransactionType,
    User,
    UserStatus,
)


@pytest.fixture(autouse=True)
def no_s3(monkeypatch):
    from app import s3_utils

    monkeypatch.setattr(s3_utils, "delete_file_from_s3", lambda url: True)
    monkeypatch.setattr(account_mod.settings, "PREVIEW_LOCAL_DIR", "")


@pytest.fixture()
def client(db, user):
    """테스트 DB 와 로그인 사용자를 주입한 클라이언트."""
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def full_account(db, user):
    """아바타·생성물·결제 기록이 있는 계정."""
    avatar = Avatar(user_id=user.id, title="내 아바타", lora_path="x")
    db.add(avatar)
    db.add(Generation(buyer_id=user.id, credits_used=1, prompt="프롬프트"))
    db.add(
        CreditOrder(
            order_id="ab-1",
            user_id=user.id,
            pack_code="pack30",
            pack_name="30장",
            credits=30,
            amount_krw=3_000,
            status=CreditOrderStatus.PAID.value,
        )
    )
    user.credit_balance = 12
    db.commit()
    return user


def test_미리보기는_아무것도_바꾸지_않는다(client, db, full_account):
    before = full_account.email

    response = client.get("/account/deletion-preview")

    assert response.status_code == 200
    assert response.json() == {
        "avatars": 1,
        "generations": 1,
        "redeem_codes": 0,
        "forfeited_credits": 12,
    }

    db.refresh(full_account)
    assert full_account.email == before
    assert full_account.status == UserStatus.ACTIVE.value


def test_확인_문구가_틀리면_거부한다(client, db, full_account):
    response = client.post("/account/delete", json={"confirm": "탈퇴"})

    assert response.status_code == 400
    assert "탈퇴합니다" in response.json()["detail"]

    # 아무것도 지워지지 않았다.
    db.refresh(full_account)
    assert full_account.status == UserStatus.ACTIVE.value
    assert db.query(Generation).one().prompt == "프롬프트"


def test_관리자_계정은_탈퇴할_수_없다(client, db, full_account, monkeypatch):
    """관리자가 스스로 지우면 운영 화면에 들어갈 방법이 없어진다."""
    monkeypatch.setattr(
        account_mod.settings, "ADMIN_EMAIL_WHITELIST", full_account.email
    )

    response = client.post("/account/delete", json={"confirm": "탈퇴합니다"})

    assert response.status_code == 403
    db.refresh(full_account)
    assert full_account.status == UserStatus.ACTIVE.value


def test_탈퇴가_한_번에_처리된다(client, db, full_account):
    response = client.post("/account/delete", json={"confirm": "탈퇴합니다"})

    assert response.status_code == 200
    assert response.json() == {
        "avatars": 1,
        "generations": 1,
        "redeem_codes": 0,
        "forfeited_credits": 12,
    }

    db.refresh(full_account)
    # 계정 잠금 + 식별자 파기
    assert full_account.status == UserStatus.DELETED.value
    assert full_account.email.endswith(".invalid")
    assert full_account.credit_balance == 0
    # 생성물 파기
    gen = db.query(Generation).one()
    assert gen.prompt == "" and gen.image_url is None
    # 아바타 논리 삭제
    assert db.query(Avatar).one().deleted_at is not None
    # 결제 기록 보존 (전자상거래법 5년)
    assert db.query(CreditOrder).one().status == CreditOrderStatus.PAID.value
    # 소멸 크레딧이 원장에 남는다
    adjust = (
        db.query(Transaction)
        .filter(Transaction.type == TransactionType.ADJUST.value)
        .one()
    )
    assert adjust.amount == -12


def test_탈퇴_후에는_인증이_막힌다(client, db, full_account):
    """
    get_current_user 가 status != 'active' 를 403 으로 막는다.
    JWT 는 상태가 없어서 이미 발급된 토큰이 만료 전까지 유효한데,
    이 검사가 유일한 즉시 차단 장치다.
    """
    client.post("/account/delete", json={"confirm": "탈퇴합니다"})
    db.refresh(full_account)

    # 실제 의존성으로 되돌려 잠금이 걸리는지 본다.
    app.dependency_overrides.pop(get_current_user)
    from app.auth import create_access_token

    token = create_access_token(data={"sub": full_account.id})
    response = client.get(
        "/account/deletion-preview", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_두_번_탈퇴_요청은_인증에서_막힌다(client, db, full_account):
    """
    첫 요청으로 status 가 deleted 가 되므로 두 번째는 엔드포인트에 닿지 못한다.
    (여기서는 get_current_user 를 덮어써서 닿게 만들고, 그래도 크레딧이
    음수로 가거나 원장이 두 번 쌓이지 않는지 본다)
    """
    assert client.post("/account/delete", json={"confirm": "탈퇴합니다"}).status_code == 200
    assert client.post("/account/delete", json={"confirm": "탈퇴합니다"}).status_code == 200

    db.refresh(full_account)
    assert full_account.credit_balance == 0
    # 잔액이 0 이므로 두 번째 호출은 ADJUST 를 남기지 않는다.
    assert (
        db.query(Transaction)
        .filter(Transaction.type == TransactionType.ADJUST.value)
        .count()
        == 1
    )
    # 닉네임에 "탈퇴회원" 이 중첩되지 않는다 (id 기반이라 멱등).
    assert db.query(User).filter(User.id == full_account.id).one().nickname == (
        f"탈퇴회원{full_account.id}"
    )
