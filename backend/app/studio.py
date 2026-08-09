"""
Creator Studio 피벗 라우터.

- 크리에이터: 크레딧(장당) / 팬 배포용 리딤 링크 / 본인 생성
- 팬(비회원): 코드로 진입 → 프롬프트 입력 → 생성

모든 생성은 fal 호출 전 moderation.assert_sfw_prompt 를 거친다.
생성 1장 = 크레딧 1 차감. 잔액은 User.credit_balance 이고 credits.py 가 관리한다
(구독/쿼터는 폐기 — 결제·요금제 관련은 payments.py 로 옮겼다).
"""

from datetime import datetime
from io import BytesIO
import secrets
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import credits
from .config import settings
from .db import get_db
from .dependencies import get_current_user
from .fal_client import run_generation_sync
from .moderation import assert_sfw_prompt
from .rate_limit import rate_limit_redeem_generate, rate_limit_redeem_info
from .models import (
    Avatar,
    AvatarStatus,
    Generation,
    GenerationStatus,
    RedeemCode,
    User,
)
from .schemas import (
    CodeCreateRequest,
    CodeResponse,
    RedeemGenerateRequest,
    RedeemGenerateResponse,
    RedeemInfoResponse,
    SourceImageResponse,
    StudioGenerateRequest,
)

router = APIRouter(tags=["studio"])

# 소스 이미지 업로드 제한 (fal 로 data URI 로 실어 보내므로 과도하게 크면 안 됨)
MAX_SOURCE_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_SOURCE_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


def _assert_image_upload(content: bytes, content_type: Optional[str]) -> None:
    """업로드된 소스 이미지의 크기·형식 검증."""
    if not content:
        raise HTTPException(status_code=400, detail="빈 파일이에요.")
    if len(content) > MAX_SOURCE_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"이미지는 {MAX_SOURCE_IMAGE_BYTES // (1024 * 1024)}MB 이하여야 해요.",
        )
    if content_type and content_type.lower() not in ALLOWED_SOURCE_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="PNG·JPEG·WebP 이미지만 올릴 수 있어요.")

# DB 코드 → fal 프롬프트 풀네임 변환 (main.py 와 동일 정책)
NATIONALITY_FOR_PROMPT = {
    "KR": "Korean", "US": "American", "JP": "Japanese", "CN": "Chinese",
    "GB": "British", "FR": "French", "DE": "German", "IT": "Italian",
    "ES": "Spanish", "BR": "Brazilian", "IN": "Indian", "RU": "Russian",
    "AU": "Australian", "CA": "Canadian", "MX": "Mexican", "ETC": " ",
}
GENDER_FOR_PROMPT = {"M": "male", "W": "female", "ETC": " "}

# 코드 문자셋: 헷갈리는 문자(0/O, 1/I/L) 제외
_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

def _generate_unique_code(db: Session, length: int = 8) -> str:
    """DB에 없는 유니크 코드 생성 (XXXX-XXXX 형태)."""
    for _ in range(20):
        raw = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(length))
        code = f"{raw[:4]}-{raw[4:]}"
        if not db.query(RedeemCode).filter(RedeemCode.code == code).first():
            return code
    raise HTTPException(status_code=500, detail="Failed to generate unique code.")


def _build_prompt_for_fal(avatar: Avatar, prompt: str) -> str:
    """아바타 국적/성별/나이를 프롬프트 prefix 로 합성 (main.py 와 동일)."""
    prefix_parts: list[str] = []
    if getattr(avatar, "nationality", None) and str(avatar.nationality).strip():
        code = str(avatar.nationality).strip().upper()
        prefix_parts.append(NATIONALITY_FOR_PROMPT.get(code, avatar.nationality.strip()))
    if getattr(avatar, "gender", None) and str(avatar.gender).strip():
        code = str(avatar.gender).strip().upper()
        prefix_parts.append(GENDER_FOR_PROMPT.get(code, avatar.gender.strip()))
    if getattr(avatar, "age", None) is not None:
        prefix_parts.append(f"{avatar.age} years old")
    if prefix_parts:
        return ", ".join(prefix_parts) + ". " + prompt
    return prompt


def _run_generation(
    db: Session,
    *,
    creator: User,
    avatar: Avatar,
    prompt: str,
    image_size: str,
    num_inference_steps: int,
    lora_scale: float,
    output_format: str,
    seed: Optional[int],
    source: str,
    buyer_id: Optional[int],
    source_image_url: Optional[str] = None,
    strength: float = 0.6,
    redeem_code: Optional[RedeemCode] = None,
) -> Generation:
    """
    크레딧 1 차감 → fal 호출 → 성공/실패 기록.
    호출 전 avatar.lora_path 는 검증되어 있어야 함.
    차감은 여기서 원자적으로 수행 (동시 요청 race 방지) — 잔액 부족이면 409.
    실패 시 환불.

    크레딧은 항상 아바타 주인(creator)에게서 나간다. 팬이 리딤 코드로 생성해도
    비용 부담자는 크리에이터다.
    """
    # 안전 검사 여부는 .env 의 FAL_ENABLE_SAFETY_CHECKER 하나로만 결정한다.
    safety_on = settings.FAL_ENABLE_SAFETY_CHECKER

    # 네거티브 프롬프트는 아바타 등록 시 정해진 값을 그대로 쓴다 (생성별 입력 없음).
    generation = Generation(
        avatar_id=avatar.id,
        buyer_id=buyer_id,
        creator_id=creator.id,
        redeem_code_id=redeem_code.id if redeem_code else None,
        source=source,
        credits_used=1,
        prompt=prompt,
        negative_prompt=avatar.negative_prompt,
        image_size=image_size,
        num_inference_steps=num_inference_steps,
        enable_safety_checker=safety_on,
        lora_scale=lora_scale,
        source_image_url=source_image_url,
        strength=strength,
        status=GenerationStatus.PENDING.value,
    )
    db.add(generation)
    # 거래 내역에 어느 생성 건인지 남기려면 id 가 먼저 필요하다.
    db.flush()

    # 크레딧 원자적 선차감. 호출자의 사전 잔액 체크는 UX용 fast-fail 일 뿐,
    # 동시 요청 시 잔액이 음수로 내려가는 걸 막는 최종 방어선은 여기다.
    if credits.deduct(db, user_id=creator.id, reference_id=str(generation.id)) is None:
        db.rollback()
        raise HTTPException(status_code=409, detail="크레딧이 부족해요.")
    db.commit()
    db.refresh(generation)

    prompt_for_fal = _build_prompt_for_fal(avatar, prompt)
    try:
        from .s3_utils import generate_presigned_download_url

        lora_url = avatar.lora_path
        if lora_url and "s3" in lora_url.lower() and "amazonaws" in lora_url.lower():
            lora_url = generate_presigned_download_url(lora_url, expires_in=3600)
        # negative_prompt 는 i2i 엔드포인트에 없어 fal 로 보내지 않는다 (DB 기록만).
        response_payload = run_generation_sync(
            prompt_for_fal,
            source_image_url=source_image_url,
            strength=strength,
            lora_url=lora_url,
            lora_scale=lora_scale,
            enable_safety_checker=safety_on,
            image_size=image_size,
            num_inference_steps=num_inference_steps,
            output_format=output_format,
            seed=seed,
        )
        images = response_payload.get("images") or []
        # checker 를 끈 경우 fal 이 플래그를 주더라도 결과를 폐기하지 않는다.
        is_nsfw = safety_on and any(response_payload.get("has_nsfw_concepts") or [])
        generation.nsfw_flag = is_nsfw
        generation.seed = (
            str(response_payload.get("seed"))
            if response_payload.get("seed") is not None
            else None
        )
        if is_nsfw:
            # SFW 정책: 결과가 NSFW 로 감지되면 이미지를 서빙하지 않고 실패 처리 + 쿼터 환불.
            generation.image_url = None
            generation.status = GenerationStatus.FAILED.value
            generation.fail_reason = "Blocked: generated image was flagged as NSFW."
            credits.refund(db, user_id=creator.id, reference_id=str(generation.id))
        else:
            if images:
                generation.image_url = images[0].get("url")
            generation.status = GenerationStatus.SUCCESS.value
        db.commit()
        db.refresh(generation)
    except Exception as exc:
        generation.status = GenerationStatus.FAILED.value
        generation.fail_reason = str(exc)
        # 크레딧 환불 — 실패한 생성으로 돈을 받지 않는다.
        credits.refund(db, user_id=creator.id, reference_id=str(generation.id))
        db.commit()
        db.refresh(generation)

    return generation


# ---------------------------------------------------------------------------
# 템플릿 (크리에이터)
# ---------------------------------------------------------------------------


def _owned_active_avatar(db: Session, avatar_id: int, user: User) -> Avatar:
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar or avatar.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Avatar not found.")
    if avatar.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your avatar.")
    return avatar


@router.get("/default-source-image", tags=["static"])
def get_default_source_image() -> FileResponse:
    """
    image-to-image 기본 소스 이미지 (itoi_example). 업로드하지 않았을 때 실제로 쓰이는
    이미지라, UI 에서 "이미 탑재된 원본"으로 그대로 보여준다. 공개 — 인증 불필요.
    """
    from .fal_client import DEFAULT_SOURCE_IMAGE

    if not DEFAULT_SOURCE_IMAGE.is_file():
        raise HTTPException(status_code=404, detail="기본 이미지를 찾을 수 없어요.")
    return FileResponse(
        DEFAULT_SOURCE_IMAGE,
        media_type="image/png",
        # 배포 전까지 바뀌지 않는 정적 자산이라 길게 캐시
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.post("/my/source-images", response_model=SourceImageResponse)
async def upload_source_image(
    current_user: User = Depends(get_current_user),
    image: UploadFile = File(...),
):
    """
    image-to-image 소스 이미지 업로드 (크리에이터). S3 에 저장하고 URL 을 돌려준다.
    이 URL 을 /my/generate 의 source_image_url 로 넘기면 그 이미지를 원본으로 생성한다.
    """
    from .s3_utils import to_presigned_url_if_s3
    from .storage import upload_file_for_app

    content = await image.read()
    _assert_image_upload(content, image.content_type)
    url = upload_file_for_app(
        BytesIO(content),
        image.filename or "source.png",
        folder=f"source-images/{current_user.id}",
        content_type=image.content_type or "image/png",
    )
    return SourceImageResponse(url=url, preview_url=to_presigned_url_if_s3(url) or url)


@router.post(
    "/r/{code_str}/source-images",
    response_model=SourceImageResponse,
    dependencies=[Depends(rate_limit_redeem_generate)],
)
async def upload_redeem_source_image(
    code_str: str,
    db: Session = Depends(get_db),
    image: UploadFile = File(...),
):
    """
    팬이 리딤 링크로 소스 이미지를 올린다 (비로그인). 유효한 코드일 때만 허용하고,
    생성과 동일한 레이트리밋을 건다 (업로드만 반복하는 남용 방지).
    """
    from .s3_utils import to_presigned_url_if_s3
    from .storage import upload_file_for_app

    code = _get_redeemable_code(db, code_str)

    content = await image.read()
    _assert_image_upload(content, image.content_type)
    url = upload_file_for_app(
        BytesIO(content),
        image.filename or "source.png",
        folder=f"source-images/redeem/{code.id}",
        content_type=image.content_type or "image/png",
    )
    return SourceImageResponse(url=url, preview_url=to_presigned_url_if_s3(url) or url)


# ---------------------------------------------------------------------------
# 리딤 링크 (크리에이터)
# ---------------------------------------------------------------------------


@router.get("/my/codes", response_model=List[CodeResponse])
def list_my_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CodeResponse]:
    rows = (
        db.query(RedeemCode)
        .filter(RedeemCode.creator_id == current_user.id)
        .order_by(RedeemCode.created_at.desc())
        .all()
    )
    return [CodeResponse.model_validate(c) for c in rows]


@router.post("/my/codes", response_model=List[CodeResponse], status_code=status.HTTP_201_CREATED)
def create_codes(
    payload: CodeCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CodeResponse]:
    """코드 1개 이상 발급. 팬은 이 코드로 자유롭게 프롬프트를 입력해 생성한다."""
    _owned_active_avatar(db, payload.avatar_id, current_user)

    # 동시 활성 코드 수 상한. 코드 자체는 공짜지만 사용될 때 크리에이터 크레딧이
    # 나가므로, 무한정 뿌려두고 잊는 상황을 막는 안전장치다.
    active_count = (
        db.query(RedeemCode)
        .filter(RedeemCode.creator_id == current_user.id, RedeemCode.is_active == True)  # noqa: E712
        .count()
    )
    if active_count + payload.count > settings.MAX_ACTIVE_REDEEM_CODES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"활성 코드는 최대 {settings.MAX_ACTIVE_REDEEM_CODES}개까지 둘 수 있어요 "
                f"(현재 {active_count}개)."
            ),
        )
    created: list[RedeemCode] = []
    for _ in range(payload.count):
        code = RedeemCode(
            code=_generate_unique_code(db),
            creator_id=current_user.id,
            avatar_id=payload.avatar_id,
            max_uses=payload.max_uses,
            used_count=0,
            is_active=True,
            expires_at=payload.expires_at,
        )
        db.add(code)
        created.append(code)
    db.commit()
    for c in created:
        db.refresh(c)
    return [CodeResponse.model_validate(c) for c in created]


@router.delete("/my/codes/{code_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_code(
    code_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    code = (
        db.query(RedeemCode)
        .filter(RedeemCode.id == code_id, RedeemCode.creator_id == current_user.id)
        .first()
    )
    if not code:
        raise HTTPException(status_code=404, detail="Code not found.")
    code.is_active = False
    db.commit()


# ---------------------------------------------------------------------------
# 크리에이터 본인 생성
# ---------------------------------------------------------------------------


@router.post("/my/generate")
def studio_generate(
    payload: StudioGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """크리에이터 본인이 쿼터를 써서 직접 생성 (SFW, 프롬프트 모더레이션)."""
    assert_sfw_prompt(payload.prompt)
    avatar = _owned_active_avatar(db, payload.avatar_id, current_user)
    if not avatar.lora_path:
        raise HTTPException(status_code=400, detail="This avatar has no LoRA file yet.")
    # 사전 체크는 UX용 fast-fail. 실제 차감·경합 방어는 _run_generation 안에서 한다.
    if credits.balance(db, current_user.id) <= 0:
        raise HTTPException(status_code=400, detail="크레딧이 부족해요. 충전 후 이용해 주세요.")

    generation = _run_generation(
        db,
        creator=current_user,
        avatar=avatar,
        prompt=payload.prompt,
        image_size=payload.image_size,
        num_inference_steps=payload.num_inference_steps,
        lora_scale=payload.lora_scale,
        output_format=payload.output_format,
        seed=payload.seed,
        source="self",
        buyer_id=current_user.id,
        source_image_url=payload.source_image_url,
        strength=payload.strength,
    )
    return {
        "id": generation.id,
        "status": generation.status,
        "image_url": generation.image_url,
        "fail_reason": generation.fail_reason,
    }


# ---------------------------------------------------------------------------
# 팬 리딤 (공개, 비로그인)
# ---------------------------------------------------------------------------


def _release_code_use(db: Session, code_id: int) -> None:
    """선점했던 코드 사용 1회 반납 (원자적 UPDATE). commit 은 호출자 몫."""
    db.query(RedeemCode).filter(
        RedeemCode.id == code_id, RedeemCode.used_count > 0
    ).update(
        {RedeemCode.used_count: RedeemCode.used_count - 1},
        synchronize_session=False,
    )


def _get_redeemable_code(db: Session, code_str: str) -> RedeemCode:
    code = db.query(RedeemCode).filter(RedeemCode.code == code_str.strip().upper()).first()
    if not code or not code.is_active:
        raise HTTPException(status_code=404, detail="Invalid or inactive code.")
    if code.expires_at is not None and datetime.utcnow() >= code.expires_at:
        raise HTTPException(status_code=410, detail="This code has expired.")
    if code.max_uses is not None and code.used_count >= code.max_uses:
        raise HTTPException(status_code=410, detail="This code has been fully used.")
    return code


@router.get("/r/{code_str}", response_model=RedeemInfoResponse)
def redeem_info(
    code_str: str,
    db: Session = Depends(get_db),
    _rl: None = Depends(rate_limit_redeem_info),
) -> RedeemInfoResponse:
    """팬이 코드로 진입 시 보는 정보."""
    code = _get_redeemable_code(db, code_str)
    avatar = db.query(Avatar).filter(Avatar.id == code.avatar_id).first()
    if not avatar or avatar.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Avatar not found.")
    creator = db.query(User).filter(User.id == code.creator_id).first()

    from .s3_utils import to_presigned_url_if_s3

    preview = to_presigned_url_if_s3(avatar.preview_image_url) or avatar.preview_image_url
    uses_left = None if code.max_uses is None else max(0, code.max_uses - code.used_count)

    return RedeemInfoResponse(
        code=code.code,
        creator_nickname=(creator.nickname if creator else ""),
        avatar_id=avatar.id,
        avatar_title=avatar.title,
        avatar_preview_url=preview,
        uses_left=uses_left,
    )


@router.get("/qr.svg")
def qr_svg(data: str, _rl: None = Depends(rate_limit_redeem_info)):
    """임의 문자열(주로 리딤 링크)을 QR 코드 SVG 로 변환. 공개 — 링크 자체가 공유 대상."""
    if not data or len(data) > 1024:
        raise HTTPException(status_code=400, detail="Invalid data.")
    import qrcode
    import qrcode.image.svg

    img = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2)
    buf = BytesIO()
    img.save(buf)
    return Response(
        content=buf.getvalue(),
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.post("/r/{code_str}/generate", response_model=RedeemGenerateResponse)
def redeem_generate(
    code_str: str,
    payload: RedeemGenerateRequest,
    db: Session = Depends(get_db),
    _rl: None = Depends(rate_limit_redeem_generate),
) -> RedeemGenerateResponse:
    """
    팬 생성. 프롬프트를 직접 입력한다. fal 호출 전 모더레이션을 거치며,
    크리에이터 쿼터와 코드 사용 횟수를 각각 1 차감한다.
    """
    code = _get_redeemable_code(db, code_str)

    avatar = db.query(Avatar).filter(Avatar.id == code.avatar_id).first()
    if not avatar or avatar.deleted_at is not None or not avatar.lora_path:
        raise HTTPException(status_code=400, detail="Avatar not available.")

    creator = db.query(User).filter(User.id == code.creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found.")
    # 팬이 쓰더라도 비용은 크리에이터 크레딧에서 나간다.
    if credits.balance(db, creator.id) <= 0:
        raise HTTPException(
            status_code=409, detail="크리에이터의 크레딧이 모두 소진됐어요. 나중에 다시 시도해 주세요."
        )

    assert_sfw_prompt(payload.prompt)  # 차단 시 쿼터/코드 소모 없음
    gen_prompt = payload.prompt
    gen_image_size = payload.image_size
    gen_steps = 8
    gen_lora = payload.lora_scale

    # 코드 사용 원자적 선점: 동시 요청이 max_uses 를 초과하지 못하도록
    # used_count < max_uses 조건부 UPDATE 로 먼저 1 확보. 생성 실패 시 아래에서 반납.
    reserved = (
        db.query(RedeemCode)
        .filter(
            RedeemCode.id == code.id,
            RedeemCode.is_active == True,  # noqa: E712
            or_(RedeemCode.max_uses.is_(None), RedeemCode.used_count < RedeemCode.max_uses),
        )
        .update(
            {RedeemCode.used_count: RedeemCode.used_count + 1},
            synchronize_session=False,
        )
    )
    if not reserved:
        db.rollback()
        raise HTTPException(status_code=410, detail="This code has been fully used.")
    db.commit()

    try:
        generation = _run_generation(
            db,
            creator=creator,
            avatar=avatar,
            prompt=gen_prompt,
            image_size=gen_image_size,
            num_inference_steps=gen_steps,
            lora_scale=gen_lora,
            output_format="png",
            seed=payload.seed,
            source="fan",
            buyer_id=None,
            source_image_url=payload.source_image_url,
            strength=payload.strength,
            redeem_code=code,
        )
    except HTTPException:
        # 쿼터 소진(409) 등으로 생성 자체가 시작 안 됨 → 코드 사용 반납
        _release_code_use(db, code.id)
        db.commit()
        raise

    if generation.status != GenerationStatus.SUCCESS.value:
        # 생성 실패(NSFW 차단 포함) → 코드 사용 반납 (쿼터는 _run_generation 이 환불)
        _release_code_use(db, code.id)
        db.commit()

    db.refresh(code)
    uses_left = None if code.max_uses is None else max(0, code.max_uses - code.used_count)
    return RedeemGenerateResponse(
        status=generation.status,
        image_url=generation.image_url,
        fail_reason=generation.fail_reason,
        uses_left=uses_left,
    )
