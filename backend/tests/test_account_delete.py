"""
회원 탈퇴 회귀 테스트.

탈퇴는 되돌릴 수 없고, 개인정보처리방침이 약속한 파기 범위가 곧 법적 의무다.
그래서 두 방향을 같이 고정한다:

  - **지워져야 하는 것이 지워지는가** — 이메일·닉네임·비밀번호, 학습 사진,
    생성 이미지·프롬프트, 리딤 링크
  - **남아야 하는 것이 남는가** — 결제·환불 기록(전자상거래법 5년),
    고객 문의 기록(3년), 그리고 크레딧 원장의 정합성

두 번째가 첫 번째만큼 중요하다. "다 지우면 안전하다"가 아니라 결제 기록을
지우면 그것도 위법이다.

S3 삭제는 호출되는지만 확인한다 (실제 버킷에 붙지 않는다).
"""

from datetime import datetime, timedelta

import pytest

from app import account as account_mod
from app.account import (
    CONFIRM_PHRASE,
    REJOIN_BONUS_BLOCK_DAYS,
    _anonymize,
    _deactivate_redeem_codes,
    _delete_social_rows,
    _forfeit_credits,
    _purge_avatars,
    _purge_generations,
    _purge_training_requests,
    anonymized_email,
    signup_bonus_for,
)
from app.credits import balance, grant
from app.models import (
    Avatar,
    AvatarComment,
    AvatarRating,
    Bookmark,
    CreditOrder,
    CreditOrderStatus,
    Generation,
    Inquiry,
    RedeemCode,
    TrainingRequest,
    Transaction,
    TransactionType,
    User,
    UserStatus,
)

S3 = "https://bucket.s3.ap-northeast-2.amazonaws.com/"


@pytest.fixture(autouse=True)
def no_s3(monkeypatch):
    """
    실제 S3 를 부르지 않는다. 삭제 요청이 간 URL 만 모아둔다.
    (app.account 가 함수 안에서 임포트하므로 원본 모듈을 갈아끼운다)
    """
    deleted = []

    def _fake_delete(url: str) -> bool:
        deleted.append(url)
        return True

    from app import s3_utils

    monkeypatch.setattr(s3_utils, "delete_file_from_s3", _fake_delete)
    monkeypatch.setattr(account_mod.settings, "PREVIEW_LOCAL_DIR", "")
    return deleted


# ---------------------------------------------------------------------------
# 익명화
# ---------------------------------------------------------------------------


def test_익명화된_이메일은_원본을_담고_있지_않다():
    anon = anonymized_email("someone@gmail.com")

    assert "someone" not in anon
    assert "gmail" not in anon
    # .invalid 는 RFC 2606 예약 TLD — 이 주소로 메일이 나갈 수 없다.
    assert anon.endswith(".invalid")


def test_같은_이메일은_같은_값으로_익명화된다():
    """재가입을 알아보려면 결정적이어야 한다."""
    assert anonymized_email("a@b.com") == anonymized_email("a@b.com")
    assert anonymized_email("A@B.COM  ") == anonymized_email("a@b.com")
    assert anonymized_email("a@b.com") != anonymized_email("c@b.com")


def test_시크릿이_다르면_다른_값이_나온다(monkeypatch):
    """후추가 없으면 이메일 목록만으로 대입해 원본을 되찾을 수 있다."""
    first = anonymized_email("a@b.com")
    monkeypatch.setattr(account_mod.settings, "JWT_SECRET_KEY", "another-secret")
    assert anonymized_email("a@b.com") != first


def test_탈퇴하면_로그인_식별자가_전부_바뀐다(db, user):
    original_email, original_nickname = user.email, user.nickname
    original_hash = user.password_hash

    _anonymize(db, user)
    db.commit()
    db.refresh(user)

    assert user.email != original_email
    assert user.nickname != original_nickname
    assert user.password_hash != original_hash
    # 로그인 차단의 실제 근거. get_current_user 가 active 가 아니면 403 을 낸다.
    assert user.status == UserStatus.DELETED.value


def test_익명화된_닉네임은_서로_충돌하지_않는다(db, make_user):
    """닉네임은 유니크 제약이 있어 고정 문자열을 쓰면 두 번째 탈퇴가 실패한다."""
    a = make_user("a@example.com", "aaa")
    b = make_user("b@example.com", "bbb")

    _anonymize(db, a)
    _anonymize(db, b)
    db.commit()  # 유니크 위반이면 여기서 터진다

    assert a.nickname != b.nickname


# ---------------------------------------------------------------------------
# 파기 — 지워져야 하는 것
# ---------------------------------------------------------------------------


def test_학습_사진은_S3_에서도_DB_에서도_지워진다(db, user, no_s3):
    req = TrainingRequest(
        user_id=user.id,
        avatar_name="내 얼굴",
        credit_per_generation=1,
        instagram_id="my_insta",
        description="본인 사진입니다",
        preview_image_url=f"{S3}preview.jpg",
        front_photos_urls=[f"{S3}f1.jpg", f"{S3}f2.jpg"],
        side_photos_urls=[f"{S3}s1.jpg"],
        fullbody_photos_urls=None,
        other_photos_urls=[f"{S3}o1.jpg"],
    )
    db.add(req)
    db.commit()

    assert _purge_training_requests(db, user.id) == 1
    db.commit()
    db.refresh(req)

    # S3 객체 5개(preview + f1 + f2 + s1 + o1) 전부에 삭제가 갔다.
    assert len(no_s3) == 5
    assert req.front_photos_urls is None
    assert req.side_photos_urls is None
    assert req.other_photos_urls is None
    assert req.preview_image_url is None
    assert req.instagram_id is None
    assert req.description is None
    assert req.deleted_at is not None


def test_아바타는_논리삭제되고_LoRA_가_지워진다(db, user, no_s3):
    avatar = Avatar(
        user_id=user.id,
        title="내 아바타",
        lora_path=f"{S3}lora.safetensors",
        preview_image_url=f"{S3}avatar.png",
        instagram_id="my_insta",
        description="설명",
        special_notes="메모",
        is_public=True,
    )
    db.add(avatar)
    db.commit()

    assert _purge_avatars(db, user.id) == 1
    db.commit()
    db.refresh(avatar)

    assert sorted(no_s3) == sorted([f"{S3}lora.safetensors", f"{S3}avatar.png"])
    assert avatar.lora_path is None
    assert avatar.preview_image_url is None
    assert avatar.instagram_id is None
    assert avatar.description is None
    assert avatar.special_notes is None
    assert avatar.is_public is False
    assert avatar.deleted_at is not None


def test_이미_지운_아바타의_삭제시각은_덮어쓰지_않는다(db, user):
    """원래 지운 날짜가 파기 기록이다. 탈퇴일로 덮으면 이력이 사라진다."""
    earlier = datetime(2026, 1, 1)
    avatar = Avatar(user_id=user.id, title="예전 아바타", deleted_at=earlier)
    db.add(avatar)
    db.commit()

    _purge_avatars(db, user.id)
    db.commit()
    db.refresh(avatar)

    assert avatar.deleted_at == earlier


def test_생성_이미지와_프롬프트가_지워진다(db, user, no_s3):
    gen = Generation(
        buyer_id=user.id,
        credits_used=1,
        prompt="해변의 금발의 여자",
        negative_prompt="blurry",
        image_url=f"{S3}out.png",
        source_image_url=f"{S3}src.png",
        fail_reason="어떤 사유",
        status="success",
    )
    db.add(gen)
    db.commit()

    assert _purge_generations(db, user.id) == 1
    db.commit()
    db.refresh(gen)

    assert sorted(no_s3) == sorted([f"{S3}out.png", f"{S3}src.png"])
    assert gen.image_url is None
    assert gen.source_image_url is None
    assert gen.prompt == ""
    assert gen.negative_prompt is None
    assert gen.fail_reason is None


def test_팬이_리딤_링크로_만든_생성물도_파기된다(db, make_user, no_s3):
    """
    리딤 생성은 buyer_id 가 비고 creator_id 만 채워진다. buyer_id 만 보고
    지우면 크리에이터 얼굴로 만들어진 이미지가 그대로 남는다.
    """
    creator = make_user("creator@example.com", "creator")
    gen = Generation(
        buyer_id=None,
        creator_id=creator.id,
        credits_used=1,
        prompt="팬이 쓴 프롬프트",
        image_url=f"{S3}fan.png",
        source="fan",
    )
    db.add(gen)
    db.commit()

    assert _purge_generations(db, creator.id) == 1
    db.commit()
    db.refresh(gen)

    assert gen.image_url is None
    assert gen.prompt == ""


def test_생성_행_자체는_남는다(db, user):
    """
    credits_used 는 크레딧 원장과 짝이 맞아야 한다. 행을 지우면
    "크레딧은 빠졌는데 무엇에 썼는지 모르는" 기록만 남는다.
    """
    db.add(Generation(buyer_id=user.id, credits_used=1, prompt="x"))
    db.commit()

    _purge_generations(db, user.id)
    db.commit()

    row = db.query(Generation).filter(Generation.buyer_id == user.id).one()
    assert row.credits_used == 1


def test_리딤_링크는_비활성화된다(db, user):
    avatar = Avatar(user_id=user.id, title="아바타")
    db.add(avatar)
    db.commit()
    for i in range(3):
        db.add(
            RedeemCode(
                code=f"CODE{i}", creator_id=user.id, avatar_id=avatar.id, is_active=True
            )
        )
    db.add(
        RedeemCode(code="OFF", creator_id=user.id, avatar_id=avatar.id, is_active=False)
    )
    db.commit()

    # 이미 꺼둔 코드는 세지 않는다.
    assert _deactivate_redeem_codes(db, user.id) == 3
    db.commit()

    assert db.query(RedeemCode).filter(RedeemCode.is_active == True).count() == 0  # noqa: E712


def test_북마크_추천_댓글은_행째로_지워진다(db, user, make_user):
    other = make_user("other@example.com", "other")
    avatar = Avatar(user_id=other.id, title="남의 아바타")
    gen = Generation(buyer_id=other.id, credits_used=1, prompt="x")
    db.add_all([avatar, gen])
    db.commit()

    db.add_all([
        Bookmark(user_id=user.id, generation_id=gen.id),
        AvatarRating(avatar_id=avatar.id, user_id=user.id, is_up=True),
        AvatarComment(avatar_id=avatar.id, user_id=user.id, content="좋네요"),
        # 남의 행은 남아야 한다
        AvatarRating(avatar_id=avatar.id, user_id=other.id, is_up=False),
    ])
    db.commit()

    _delete_social_rows(db, user.id)
    db.commit()

    assert db.query(Bookmark).count() == 0
    assert db.query(AvatarComment).count() == 0
    assert db.query(AvatarRating).count() == 1


def test_남의_데이터는_건드리지_않는다(db, make_user, no_s3):
    leaver = make_user("leaver@example.com", "leaver")
    stayer = make_user("stayer@example.com", "stayer")

    mine = Avatar(user_id=leaver.id, title="내 것", lora_path=f"{S3}mine.bin")
    yours = Avatar(user_id=stayer.id, title="남의 것", lora_path=f"{S3}yours.bin")
    db.add_all([mine, yours])
    db.add(Generation(buyer_id=stayer.id, credits_used=1, prompt="남의 프롬프트"))
    db.commit()

    _purge_avatars(db, leaver.id)
    _purge_generations(db, leaver.id)
    db.commit()
    db.refresh(yours)

    assert no_s3 == [f"{S3}mine.bin"]
    assert yours.lora_path == f"{S3}yours.bin"
    assert yours.deleted_at is None
    assert db.query(Generation).one().prompt == "남의 프롬프트"


# ---------------------------------------------------------------------------
# 보존 — 남아야 하는 것
# ---------------------------------------------------------------------------


def test_결제_기록은_탈퇴해도_남는다(db, user, no_s3):
    """전자상거래법상 대금결제 기록은 5년 보관 의무가 있다."""
    order = CreditOrder(
        order_id="ab-keep-me",
        user_id=user.id,
        pack_code="pack100",
        pack_name="100장",
        credits=100,
        amount_krw=9_000,
        status=CreditOrderStatus.PAID.value,
        payment_key="tx-1",
    )
    db.add(order)
    grant(db, user_id=user.id, amount=100, reason=TransactionType.PURCHASE,
          reference_id="ab-keep-me")
    db.commit()

    _forfeit_credits(db, user)
    _purge_generations(db, user.id)
    _anonymize(db, user)
    db.commit()

    kept = db.query(CreditOrder).filter(CreditOrder.order_id == "ab-keep-me").one()
    assert kept.status == CreditOrderStatus.PAID.value
    assert kept.amount_krw == 9_000
    # user_id 를 끊지 않는다 — 끊으면 누구의 결제였는지 대조할 수 없어
    # 분쟁이나 세무 확인에 쓸 수 없는 기록이 된다.
    assert kept.user_id == user.id

    purchase = (
        db.query(Transaction)
        .filter(Transaction.type == TransactionType.PURCHASE.value)
        .one()
    )
    assert purchase.amount == 100


def test_고객_문의는_탈퇴해도_남는다(db, user):
    """방침상 문의 기록은 접수일로부터 3년 보관한다 (분쟁 대응)."""
    db.add(
        Inquiry(
            user_id=user.id,
            name="홍길동",
            email=user.email,
            subject="환불 문의",
            message="환불해 주세요",
        )
    )
    db.commit()

    _anonymize(db, user)
    db.commit()

    assert db.query(Inquiry).count() == 1


# ---------------------------------------------------------------------------
# 잔여 크레딧
# ---------------------------------------------------------------------------


def test_잔여_크레딧은_원장에_남기고_소멸된다(db, user):
    grant(db, user_id=user.id, amount=37, reason=TransactionType.PURCHASE)
    db.commit()

    assert _forfeit_credits(db, user) == 37
    db.commit()

    assert balance(db, user.id) == 0

    adjust = (
        db.query(Transaction)
        .filter(Transaction.type == TransactionType.ADJUST.value)
        .one()
    )
    assert adjust.amount == -37
    assert adjust.credit_after == 0
    # 조용히 0 으로 덮으면 원장 합계와 잔액이 어긋나 CS 문의에 답할 수 없다.
    assert adjust.reference_id == "withdrawal"


def test_잔액이_0_이면_원장에_아무것도_남기지_않는다(db, user):
    assert _forfeit_credits(db, user) == 0
    db.commit()

    assert db.query(Transaction).count() == 0


def test_소멸_후에도_원장_합계와_잔액이_맞는다(db, user):
    grant(db, user_id=user.id, amount=10, reason=TransactionType.BONUS)
    grant(db, user_id=user.id, amount=100, reason=TransactionType.PURCHASE)
    db.commit()

    _forfeit_credits(db, user)
    db.commit()

    rows = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    assert sum(t.amount for t in rows) == balance(db, user.id) == 0


# ---------------------------------------------------------------------------
# 재가입 축하 크레딧
# ---------------------------------------------------------------------------


def test_처음_가입이면_축하_크레딧을_준다(db, monkeypatch):
    monkeypatch.setattr(account_mod.settings, "SIGNUP_BONUS_CREDITS", 10)
    assert signup_bonus_for(db, "new@example.com") == 10


def test_최근_탈퇴한_이메일로_재가입하면_주지_않는다(db, user, monkeypatch):
    """탈퇴·재가입을 반복해 크레딧을 받는 걸 막는다 (장당 실제 원가가 나간다)."""
    monkeypatch.setattr(account_mod.settings, "SIGNUP_BONUS_CREDITS", 10)
    original = user.email

    _anonymize(db, user)
    db.commit()

    assert signup_bonus_for(db, original) == 0


def test_30일이_지나면_다시_준다(db, user, monkeypatch):
    """방침이 허용한 보관 기간은 30일이다. 영구 차단이 아니다."""
    monkeypatch.setattr(account_mod.settings, "SIGNUP_BONUS_CREDITS", 10)
    original = user.email

    _anonymize(db, user)
    db.commit()
    # updated_at 은 onupdate 로 갱신되므로 직접 과거로 돌린다.
    user.updated_at = datetime.utcnow() - timedelta(days=REJOIN_BONUS_BLOCK_DAYS + 1)
    db.query(User).filter(User.id == user.id).update(
        {"updated_at": user.updated_at}, synchronize_session=False
    )
    db.commit()

    assert signup_bonus_for(db, original) == 10


def test_탈퇴한_적_없는_다른_이메일은_영향_없다(db, user, monkeypatch):
    monkeypatch.setattr(account_mod.settings, "SIGNUP_BONUS_CREDITS", 10)
    _anonymize(db, user)
    db.commit()

    assert signup_bonus_for(db, "someone.else@example.com") == 10


def test_축하_크레딧_설정이_0_이면_조회도_하지_않는다(db, monkeypatch):
    monkeypatch.setattr(account_mod.settings, "SIGNUP_BONUS_CREDITS", 0)
    assert signup_bonus_for(db, "new@example.com") == 0


# ---------------------------------------------------------------------------
# 확인 문구
# ---------------------------------------------------------------------------


def test_확인_문구는_한국어_고정값이다():
    """
    구글 로그인 계정은 비밀번호가 없어(가입 시 랜덤 값을 해시해 둔다)
    비밀번호 재확인을 쓸 수 없다. 두 종류의 계정에 같은 방식이 필요하다.
    """
    assert CONFIRM_PHRASE == "탈퇴합니다"
