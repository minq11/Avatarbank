"""
회원 탈퇴.

개인정보처리방침 5항이 약속한 것을 그대로 구현한다:

  - 회원 정보        → 지체 없이 파기 (이메일·닉네임 익명화, 비밀번호 폐기)
  - 아바타 학습 사진 → 파기 (S3 객체 삭제 + URL 제거)
  - 생성 이미지·프롬프트 → 파기 (S3 객체 삭제 + 프롬프트 제거)
  - 고객 문의 기록   → 3년 보관 (건드리지 않는다)
  - 결제·환불 기록   → 5년 보관 (건드리지 않는다)

**행을 지우지 않고 익명화한다.** 두 가지 이유다.

1. 전자상거래법이 대금결제 기록을 5년 보관하게 한다. Transaction 과
   CreditOrder 는 user_id 로 사용자 행을 참조하므로, users 행을 DELETE 하면
   외래키가 깨지거나 결제 기록이 같이 날아간다. 법적 보존 의무와 파기 약속을
   동시에 지키는 방법은 "식별자는 지우고 거래 기록은 남기는" 익명화다.
2. Generation.credits_used 는 원장(Transaction)과 짝이 맞아야 한다. 생성 행을
   지우면 "크레딧은 빠졌는데 무엇에 썼는지 모르는" 기록이 남는다.

스키마를 바꾸지 않는다. 이 프로젝트에는 마이그레이션 장치가 없어서
(DEPLOY.md '알려진 제약') 컬럼을 추가하면 운영 DB 에 손으로 손대야 한다.
그래서 이미 있는 것만 쓴다 — User.status 의 'deleted', Avatar/TrainingRequest
의 deleted_at, User.updated_at(= 탈퇴 시각).

재가입 어뷰징: 이메일을 완전히 지우면 탈퇴 → 재가입을 반복해 가입 축하
크레딧을 무한히 받을 수 있다(장당 실제 원가가 나간다). 그래서 이메일을
되돌릴 수 없는 해시로 바꿔 두고, 가입 시 같은 해시가 최근 30일 안에 탈퇴한
계정으로 남아 있으면 축하 크레딧만 주지 않는다. 방침이 허용한
"부정 이용 재발 방지를 위한 최소한의 식별 정보 30일 보관" 범위다.
가입 자체를 막지는 않는다.
"""

from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .auth import get_password_hash
from .config import settings
from .credits import deduct
from .db import get_db
from .dependencies import get_current_user, is_admin_email
from .models import (
    Avatar,
    AvatarComment,
    AvatarRating,
    Bookmark,
    Generation,
    RedeemCode,
    TrainingRequest,
    TransactionType,
    User,
    UserStatus,
)
from .schemas import AccountDeleteRequest, AccountDeleteResponse

router = APIRouter(tags=["account"])
logger = logging.getLogger(__name__)

# 탈퇴 확인 문구. 실수로 누르는 걸 막는 장치다. 구글 로그인 계정은 비밀번호가
# 없어(가입 시 랜덤 값을 해시해 둔다) 비밀번호 재확인을 쓸 수 없으므로,
# 두 종류의 계정에 같은 방식으로 적용되는 문구 입력을 쓴다.
CONFIRM_PHRASE = "탈퇴합니다"

# 재가입 축하 크레딧을 주지 않는 기간. 방침의 30일과 같은 값이다.
REJOIN_BONUS_BLOCK_DAYS = 30

# 탈퇴 계정의 이메일에 쓰는 도메인. .invalid 는 RFC 2606 이 예약한 TLD 라
# 실제로 존재할 수 없다 — 익명화된 주소로 메일이 나갈 일이 없다.
_ANON_EMAIL_DOMAIN = "avatarclub.invalid"


def anonymized_email(email: str) -> str:
    """
    탈퇴 계정의 이메일로 쓸 되돌릴 수 없는 값.

    같은 원본 이메일은 항상 같은 값이 되므로 재가입을 알아볼 수 있고,
    JWT_SECRET_KEY 를 후추로 섞으므로 이 값만 봐서는 원본을 되찾을 수 없다
    (무지개표 대입도 막힌다).

    시크릿을 교체하면 이전 탈퇴 계정과의 대조가 끊긴다. 영향은 "재가입에
    축하 크레딧을 다시 준다" 뿐이라 안전한 방향으로 실패한다.
    """
    normalized = (email or "").strip().lower()
    digest = hashlib.sha256(
        f"{settings.JWT_SECRET_KEY}:{normalized}".encode("utf-8")
    ).hexdigest()
    return f"deleted-{digest[:32]}@{_ANON_EMAIL_DOMAIN}"


def signup_bonus_for(db: Session, email: str) -> int:
    """
    이 이메일에 줄 가입 축하 크레딧. 최근 탈퇴한 계정의 이메일이면 0.

    가입 경로가 두 개(이메일·구글)라 양쪽에서 같은 판단을 하도록 여기 모았다.
    """
    bonus = max(0, settings.SIGNUP_BONUS_CREDITS)
    if not bonus:
        return 0

    cutoff = datetime.utcnow() - timedelta(days=REJOIN_BONUS_BLOCK_DAYS)
    recent_withdrawal = (
        db.query(User.id)
        .filter(
            User.email == anonymized_email(email),
            User.status == UserStatus.DELETED.value,
            User.updated_at >= cutoff,
        )
        .first()
    )
    if recent_withdrawal:
        logger.info("최근 탈퇴 이력이 있어 가입 축하 크레딧을 지급하지 않습니다.")
        return 0
    return bonus


# ---------------------------------------------------------------------------
# 파기 도우미
# ---------------------------------------------------------------------------


def _purge_s3(urls: Iterable[Optional[str]]) -> int:
    """
    S3 객체를 지운다. 실패해도 탈퇴 자체를 막지 않는다.

    파일 삭제는 트랜잭션이 아니므로 일부만 지워질 수 있다. 그래도 DB 에서
    URL 을 지우는 편이 낫다 — 접근 경로가 없어지고, 남은 객체는 로그를 보고
    수동으로 정리할 수 있다. 반대로 파일 삭제 실패로 탈퇴를 거부하면
    사용자는 계정을 지울 방법이 없어진다.
    """
    from .s3_utils import delete_file_from_s3

    removed = 0
    for url in urls:
        if not url or "amazonaws" not in url or "s3" not in url.lower():
            continue
        if delete_file_from_s3(url):
            removed += 1
        else:
            logger.warning("탈퇴 처리 중 S3 객체 삭제 실패 (수동 정리 필요): %s", url)
    return removed


def _purge_local_preview(avatar_id: int) -> None:
    """PREVIEW_LOCAL_DIR 에 남은 아바타 미리보기 파일을 지운다."""
    if not settings.PREVIEW_LOCAL_DIR:
        return
    try:
        Path(settings.PREVIEW_LOCAL_DIR, f"{avatar_id}.png").unlink(missing_ok=True)
    except OSError as exc:
        logger.warning("미리보기 파일 삭제 실패 avatar_id=%s: %s", avatar_id, exc)


def _purge_avatars(db: Session, user_id: int) -> int:
    """아바타를 논리 삭제하고 LoRA·미리보기와 자유 입력 항목을 지운다."""
    avatars = db.query(Avatar).filter(Avatar.user_id == user_id).all()
    now = datetime.utcnow()

    for avatar in avatars:
        _purge_s3([avatar.lora_path, avatar.preview_image_url])
        _purge_local_preview(avatar.id)

        avatar.lora_path = None
        avatar.preview_image_url = None
        # 본인을 특정할 수 있는 항목들. 아바타 제목은 사용자가 지은 이름이라
        # 남겨두면 관리자 화면에서 누구였는지 짐작할 수 있으므로 같이 지운다.
        avatar.instagram_id = None
        avatar.description = None
        avatar.special_notes = None
        avatar.is_public = False
        if avatar.deleted_at is None:
            avatar.deleted_at = now
    return len(avatars)


def _purge_training_requests(db: Session, user_id: int) -> int:
    """학습 사진을 파기한다. 얼굴 사진이라 가장 민감한 자료다."""
    requests = db.query(TrainingRequest).filter(TrainingRequest.user_id == user_id).all()
    now = datetime.utcnow()

    for req in requests:
        photo_urls = [req.preview_image_url]
        for bucket in (
            req.front_photos_urls,
            req.side_photos_urls,
            req.fullbody_photos_urls,
            req.other_photos_urls,
        ):
            photo_urls.extend(bucket or [])
        _purge_s3(photo_urls)

        req.preview_image_url = None
        req.front_photos_urls = None
        req.side_photos_urls = None
        req.fullbody_photos_urls = None
        req.other_photos_urls = None
        req.instagram_id = None
        req.description = None
        if req.deleted_at is None:
            req.deleted_at = now
    return len(requests)


def _purge_generations(db: Session, user_id: int) -> int:
    """
    생성물과 프롬프트를 파기한다.

    행은 남긴다 — credits_used 가 원장과 짝이 맞아야 한다. 대신 이미지와
    프롬프트(자유 입력이라 개인정보가 섞일 수 있다)는 지운다.

    creator_id 로도 찾는 이유: 리딤 링크로 팬이 만든 생성물은 buyer_id 가
    비어 있고 creator_id 만 채워진다. buyer_id 만 보면 크리에이터 아바타로
    만들어진 이미지가 그대로 남는다.
    """
    generations = (
        db.query(Generation)
        .filter((Generation.buyer_id == user_id) | (Generation.creator_id == user_id))
        .all()
    )

    for gen in generations:
        _purge_s3([gen.image_url, gen.source_image_url])
        gen.image_url = None
        gen.source_image_url = None
        gen.prompt = ""  # NOT NULL 이라 None 을 넣을 수 없다
        gen.negative_prompt = None
        gen.fail_reason = None
    return len(generations)


def _deactivate_redeem_codes(db: Session, user_id: int) -> int:
    """
    리딤 링크를 비활성화한다.

    이미 배포된 링크가 살아 있으면 탈퇴한 사람의 아바타로 팬이 계속 생성을
    시도한다. 아바타도 논리 삭제되므로 이중으로 막히지만, 코드 자체를
    끄는 쪽이 팬에게 보이는 오류가 더 정확하다.
    """
    codes = (
        db.query(RedeemCode)
        .filter(RedeemCode.creator_id == user_id, RedeemCode.is_active == True)  # noqa: E712
        .all()
    )
    for code in codes:
        code.is_active = False
    return len(codes)


def _delete_social_rows(db: Session, user_id: int) -> None:
    """북마크·추천·댓글은 보존할 이유가 없으므로 행째로 지운다."""
    db.query(Bookmark).filter(Bookmark.user_id == user_id).delete(synchronize_session=False)
    db.query(AvatarRating).filter(AvatarRating.user_id == user_id).delete(synchronize_session=False)
    db.query(AvatarComment).filter(AvatarComment.user_id == user_id).delete(
        synchronize_session=False
    )


def _forfeit_credits(db: Session, user: User) -> int:
    """
    잔여 크레딧을 0 으로 만들고 원장에 남긴다.

    조용히 0 으로 덮으면 원장 합계와 잔액이 어긋나 나중에 CS 문의에 답할 수
    없다. ADJUST 로 기록해 "탈퇴로 소멸" 이 추적되게 한다.
    환불을 원하는 사용자는 탈퇴 전에 고객지원으로 요청해야 하며,
    그 안내는 탈퇴 화면에 표시한다.
    """
    remaining = int(user.credit_balance or 0)
    if remaining <= 0:
        return 0
    deduct(
        db,
        user_id=user.id,
        amount=remaining,
        reason=TransactionType.ADJUST,
        reference_id="withdrawal",
    )
    return remaining


def _anonymize(db: Session, user: User) -> None:
    """
    식별자를 지운다. 이 시점부터 로그인이 불가능하다
    (get_current_user 가 status != 'active' 를 403 으로 막는다).
    """
    user.email = anonymized_email(user.email)
    user.nickname = f"탈퇴회원{user.id}"  # 닉네임은 유니크 — id 를 붙여 충돌을 피한다
    # 아무도 모르는 값으로 덮는다. 비우면 NOT NULL 에 걸리고, 빈 해시를
    # 남기면 검증 로직에 따라 통과할 여지가 생긴다.
    user.password_hash = get_password_hash(secrets.token_urlsafe(32))
    user.status = UserStatus.DELETED.value
    user.locale = "ko"


# ---------------------------------------------------------------------------
# 엔드포인트
# ---------------------------------------------------------------------------


@router.get("/account/deletion-preview", response_model=AccountDeleteResponse)
def deletion_preview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccountDeleteResponse:
    """
    탈퇴하면 무엇이 사라지는지 미리 보여준다. 아무것도 바꾸지 않는다.

    "정말 탈퇴하시겠습니까?" 만 띄우는 것보다, 지워질 아바타 수와 소멸될
    크레딧을 숫자로 보여주는 편이 사용자가 실제로 판단할 수 있다.
    """
    avatars = (
        db.query(Avatar)
        .filter(Avatar.user_id == current_user.id, Avatar.deleted_at.is_(None))
        .count()
    )
    generations = (
        db.query(Generation)
        .filter(
            (Generation.buyer_id == current_user.id)
            | (Generation.creator_id == current_user.id)
        )
        .count()
    )
    codes = (
        db.query(RedeemCode)
        .filter(
            RedeemCode.creator_id == current_user.id,
            RedeemCode.is_active == True,  # noqa: E712
        )
        .count()
    )
    return AccountDeleteResponse(
        avatars=avatars,
        generations=generations,
        redeem_codes=codes,
        forfeited_credits=int(current_user.credit_balance or 0),
    )


# DELETE 가 의미상 맞지만 본문(확인 문구)을 받아야 한다. DELETE 본문은
# 프록시·클라이언트가 조용히 버리는 경우가 있어 POST 로 둔다.
@router.post("/account/delete", response_model=AccountDeleteResponse)
def delete_account(
    payload: AccountDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccountDeleteResponse:
    """
    회원 탈퇴. 돌이킬 수 없다.

    한 트랜잭션으로 처리한다. 중간에 실패하면 전부 되돌아가므로
    "아바타는 지워졌는데 계정은 살아 있는" 어중간한 상태가 남지 않는다.
    S3 객체 삭제만은 트랜잭션 밖의 일이라 되돌아가지 않는다 — 이미 지운
    파일은 다시 만들 수 없지만, 그건 어차피 사용자가 요청한 방향이다.
    """
    if payload.confirm.strip() != CONFIRM_PHRASE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"확인 문구가 달라요. '{CONFIRM_PHRASE}' 를 정확히 입력해 주세요.",
        )

    # 관리자 계정이 스스로 지워지면 운영 화면에 들어갈 방법이 없어진다.
    # 화이트리스트에서 이메일을 먼저 빼야 한다.
    if is_admin_email(current_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 계정은 이 화면에서 탈퇴할 수 없어요.",
        )

    user_id = current_user.id
    forfeited = _forfeit_credits(db, current_user)
    avatars = _purge_avatars(db, user_id)
    _purge_training_requests(db, user_id)
    generations = _purge_generations(db, user_id)
    codes = _deactivate_redeem_codes(db, user_id)
    _delete_social_rows(db, user_id)
    _anonymize(db, current_user)

    db.commit()

    # 이메일·닉네임은 이미 지워졌으므로 id 만 남긴다.
    logger.info(
        "회원 탈퇴 처리 완료 user_id=%s 아바타=%s 생성물=%s 리딤코드=%s 소멸크레딧=%s",
        user_id, avatars, generations, codes, forfeited,
    )

    return AccountDeleteResponse(
        avatars=avatars,
        generations=generations,
        redeem_codes=codes,
        forfeited_credits=forfeited,
    )
