"""
Creator Studio 피벗 라우터.

- 크리에이터: 구독(쿼터) / 생성 템플릿 / 팬 배포용 리딤 코드 / 본인 생성
- 팬(비회원): 코드로 진입 → 템플릿 선택 → 생성

정책: SFW 전용. 모든 생성은 enable_safety_checker 강제 ON (fal_client 에서도 강제).
팬은 자유 프롬프트 불가 — 크리에이터가 만든 템플릿 프롬프트만 사용.
"""

from datetime import datetime, timedelta
import secrets
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .dependencies import get_current_user
from .fal_client import run_generation_sync
from .models import (
    Avatar,
    AvatarStatus,
    Generation,
    GenerationStatus,
    GenerationTemplate,
    Plan,
    RedeemCode,
    Subscription,
    SubscriptionStatus,
    Transaction,
    User,
)
from .schemas import (
    CodeCreateRequest,
    CodeResponse,
    PlanResponse,
    RedeemGenerateRequest,
    RedeemGenerateResponse,
    RedeemInfoResponse,
    StudioGenerateRequest,
    SubscribeRequest,
    SubscriptionResponse,
    TemplateCreateRequest,
    TemplateResponse,
)

router = APIRouter(tags=["studio"])

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

# 기본 요금제 (마이그레이션/스타트업 시 시드). 수치는 임시값.
DEFAULT_PLANS = [
    {"code": "free", "name": "Free", "monthly_quota": 10, "price_usd": 0,
     "max_avatars": 1, "max_active_codes": 3, "sort_order": 0},
    {"code": "starter", "name": "Starter", "monthly_quota": 300, "price_usd": 19,
     "max_avatars": 1, "max_active_codes": 50, "sort_order": 1},
    {"code": "pro", "name": "Pro", "monthly_quota": 1000, "price_usd": 49,
     "max_avatars": 3, "max_active_codes": 500, "sort_order": 2},
    {"code": "studio", "name": "Studio", "monthly_quota": 3000, "price_usd": 129,
     "max_avatars": 10, "max_active_codes": 5000, "sort_order": 3},
]


def seed_plans(db: Session) -> None:
    """기본 요금제가 없으면 생성. 멱등."""
    for p in DEFAULT_PLANS:
        existing = db.query(Plan).filter(Plan.code == p["code"]).first()
        if existing:
            continue
        db.add(Plan(
            code=p["code"], name=p["name"], monthly_quota=p["monthly_quota"],
            price_usd=p["price_usd"], max_avatars=p["max_avatars"],
            max_active_codes=p["max_active_codes"], allow_nsfw=False,
            is_active=True, sort_order=p["sort_order"],
        ))
    db.commit()


def _generate_unique_code(db: Session, length: int = 8) -> str:
    """DB에 없는 유니크 코드 생성 (XXXX-XXXX 형태)."""
    for _ in range(20):
        raw = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(length))
        code = f"{raw[:4]}-{raw[4:]}"
        if not db.query(RedeemCode).filter(RedeemCode.code == code).first():
            return code
    raise HTTPException(status_code=500, detail="Failed to generate unique code.")


def _get_subscription(db: Session, user: User) -> Optional[Subscription]:
    """구독 조회 + 주기 만료 시 쿼터 리셋 (lazy)."""
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub:
        return None
    now = datetime.utcnow()
    if (
        sub.status == SubscriptionStatus.ACTIVE.value
        and sub.current_period_end is not None
        and now >= sub.current_period_end
    ):
        plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
        if plan:
            sub.quota_remaining = plan.monthly_quota
            sub.current_period_start = now
            sub.current_period_end = now + timedelta(days=30)
            db.commit()
            db.refresh(sub)
    return sub


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
    negative_prompt: Optional[str],
    image_size: str,
    num_inference_steps: int,
    lora_scale: float,
    output_format: str,
    seed: Optional[int],
    source: str,
    buyer_id: Optional[int],
    redeem_code: Optional[RedeemCode] = None,
    template: Optional[GenerationTemplate] = None,
) -> Generation:
    """
    쿼터 1 차감 → fal 호출(SFW 강제) → 성공/실패 기록.
    호출 전 쿼터(quota_remaining>0)·avatar.lora_path 는 검증되어 있어야 함.
    실패 시 쿼터 환불.
    """
    sub = _get_subscription(db, creator)

    parts = [avatar.negative_prompt, negative_prompt]
    combined_negative = ", ".join(p.strip() for p in parts if p and p.strip()) or None

    generation = Generation(
        avatar_id=avatar.id,
        buyer_id=buyer_id,
        creator_id=creator.id,
        redeem_code_id=redeem_code.id if redeem_code else None,
        template_id=template.id if template else None,
        source=source,
        credits_used=1,
        prompt=prompt,
        negative_prompt=combined_negative,
        image_size=image_size,
        num_inference_steps=num_inference_steps,
        enable_safety_checker=True,  # SFW 강제
        lora_scale=lora_scale,
        status=GenerationStatus.PENDING.value,
    )
    db.add(generation)

    # 쿼터 선차감
    if sub is not None:
        sub.quota_remaining = max(0, sub.quota_remaining - 1)
    db.commit()
    db.refresh(generation)

    prompt_for_fal = _build_prompt_for_fal(avatar, prompt)
    try:
        from .s3_utils import generate_presigned_download_url

        lora_url = avatar.lora_path
        if lora_url and "s3" in lora_url.lower() and "amazonaws" in lora_url.lower():
            lora_url = generate_presigned_download_url(lora_url, expires_in=3600)
        response_payload = run_generation_sync(
            prompt_for_fal,
            lora_url=lora_url,
            lora_scale=lora_scale,
            negative_prompt=combined_negative,
            enable_safety_checker=True,  # SFW 강제
            image_size=image_size,
            num_inference_steps=num_inference_steps,
            output_format=output_format,
            seed=seed,
        )
        images = response_payload.get("images") or []
        if images:
            generation.image_url = images[0].get("url")
        generation.seed = (
            str(response_payload.get("seed"))
            if response_payload.get("seed") is not None
            else None
        )
        generation.nsfw_flag = any(response_payload.get("has_nsfw_concepts") or [])
        generation.status = GenerationStatus.SUCCESS.value
        db.commit()
        db.refresh(generation)
    except Exception as exc:
        generation.status = GenerationStatus.FAILED.value
        generation.fail_reason = str(exc)
        # 쿼터 환불
        if sub is not None:
            sub.quota_remaining += 1
        db.commit()
        db.refresh(generation)

    return generation


# ---------------------------------------------------------------------------
# 요금제 / 구독
# ---------------------------------------------------------------------------


@router.get("/plans", response_model=List[PlanResponse])
def list_plans(db: Session = Depends(get_db)) -> List[PlanResponse]:
    """공개 요금제 목록."""
    plans = (
        db.query(Plan)
        .filter(Plan.is_active == True)  # noqa: E712
        .order_by(Plan.sort_order.asc())
        .all()
    )
    return [PlanResponse.model_validate(p) for p in plans]


@router.get("/my/subscription", response_model=Optional[SubscriptionResponse])
def get_my_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Optional[SubscriptionResponse]:
    """내 구독 상태 + 남은 쿼터. 미구독이면 null."""
    sub = _get_subscription(db, current_user)
    if not sub:
        return None
    plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
    return SubscriptionResponse(
        plan_code=plan.code if plan else "",
        plan_name=plan.name if plan else "",
        status=sub.status,
        quota_remaining=sub.quota_remaining,
        monthly_quota=plan.monthly_quota if plan else 0,
        current_period_end=sub.current_period_end,
    )


@router.post("/my/subscription", response_model=SubscriptionResponse)
def subscribe(
    payload: SubscribeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubscriptionResponse:
    """
    구독/요금제 변경. *결제 미연동 스텁* — 즉시 활성 + 쿼터 충전.
    실제 서비스에서는 Stripe 등 결제 성공 웹훅 후 호출되어야 함.
    """
    plan = db.query(Plan).filter(Plan.code == payload.plan_code, Plan.is_active == True).first()  # noqa: E712
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found.")

    now = datetime.utcnow()
    sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if sub:
        sub.plan_id = plan.id
        sub.status = SubscriptionStatus.ACTIVE.value
        sub.quota_remaining = plan.monthly_quota
        sub.current_period_start = now
        sub.current_period_end = now + timedelta(days=30)
    else:
        sub = Subscription(
            user_id=current_user.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE.value,
            quota_remaining=plan.monthly_quota,
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
        )
        db.add(sub)
    db.commit()
    db.refresh(sub)
    return SubscriptionResponse(
        plan_code=plan.code,
        plan_name=plan.name,
        status=sub.status,
        quota_remaining=sub.quota_remaining,
        monthly_quota=plan.monthly_quota,
        current_period_end=sub.current_period_end,
    )


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


@router.get("/my/templates", response_model=List[TemplateResponse])
def list_my_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[TemplateResponse]:
    rows = (
        db.query(GenerationTemplate)
        .filter(
            GenerationTemplate.creator_id == current_user.id,
            GenerationTemplate.deleted_at.is_(None),
        )
        .order_by(GenerationTemplate.created_at.desc())
        .all()
    )
    return [TemplateResponse.model_validate(t) for t in rows]


@router.post("/my/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: TemplateCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TemplateResponse:
    _owned_active_avatar(db, payload.avatar_id, current_user)
    template = GenerationTemplate(
        creator_id=current_user.id,
        avatar_id=payload.avatar_id,
        name=payload.name.strip(),
        prompt=payload.prompt.strip(),
        negative_prompt=payload.negative_prompt,
        image_size=payload.image_size,
        num_inference_steps=payload.num_inference_steps,
        lora_scale=payload.lora_scale,
        is_active=True,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return TemplateResponse.model_validate(template)


@router.delete("/my/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    template = (
        db.query(GenerationTemplate)
        .filter(
            GenerationTemplate.id == template_id,
            GenerationTemplate.creator_id == current_user.id,
            GenerationTemplate.deleted_at.is_(None),
        )
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found.")
    template.deleted_at = datetime.utcnow()
    template.is_active = False
    db.commit()


# ---------------------------------------------------------------------------
# 리딤 코드 (크리에이터)
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
    """코드 1개 이상 발급. template_id 지정 시 팬은 그 템플릿만 사용 가능."""
    _owned_active_avatar(db, payload.avatar_id, current_user)
    if payload.template_id is not None:
        tpl = (
            db.query(GenerationTemplate)
            .filter(
                GenerationTemplate.id == payload.template_id,
                GenerationTemplate.creator_id == current_user.id,
                GenerationTemplate.avatar_id == payload.avatar_id,
                GenerationTemplate.deleted_at.is_(None),
            )
            .first()
        )
        if not tpl:
            raise HTTPException(status_code=404, detail="Template not found for this avatar.")

    created: list[RedeemCode] = []
    for _ in range(payload.count):
        code = RedeemCode(
            code=_generate_unique_code(db),
            creator_id=current_user.id,
            avatar_id=payload.avatar_id,
            template_id=payload.template_id,
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
    """크리에이터 본인이 쿼터를 써서 직접 생성 (SFW)."""
    avatar = _owned_active_avatar(db, payload.avatar_id, current_user)
    if not avatar.lora_path:
        raise HTTPException(status_code=400, detail="This avatar has no LoRA file yet.")
    sub = _get_subscription(db, current_user)
    if not sub or sub.status != SubscriptionStatus.ACTIVE.value:
        raise HTTPException(status_code=403, detail="Active subscription required.")
    if sub.quota_remaining <= 0:
        raise HTTPException(status_code=400, detail="No generation quota left this period.")

    generation = _run_generation(
        db,
        creator=current_user,
        avatar=avatar,
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
        image_size=payload.image_size,
        num_inference_steps=payload.num_inference_steps,
        lora_scale=payload.lora_scale,
        output_format=payload.output_format,
        seed=payload.seed,
        source="self",
        buyer_id=current_user.id,
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
def redeem_info(code_str: str, db: Session = Depends(get_db)) -> RedeemInfoResponse:
    """팬이 코드로 진입 시 보는 정보 + 사용 가능한 템플릿."""
    code = _get_redeemable_code(db, code_str)
    avatar = db.query(Avatar).filter(Avatar.id == code.avatar_id).first()
    if not avatar or avatar.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Avatar not found.")
    creator = db.query(User).filter(User.id == code.creator_id).first()

    # 사용 가능한 템플릿: 코드에 묶인 게 있으면 그것만, 없으면 해당 아바타의 활성 템플릿 전부
    tq = db.query(GenerationTemplate).filter(
        GenerationTemplate.creator_id == code.creator_id,
        GenerationTemplate.avatar_id == code.avatar_id,
        GenerationTemplate.deleted_at.is_(None),
        GenerationTemplate.is_active == True,  # noqa: E712
    )
    if code.template_id is not None:
        tq = tq.filter(GenerationTemplate.id == code.template_id)
    templates = tq.order_by(GenerationTemplate.created_at.desc()).all()

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
        templates=[TemplateResponse.model_validate(t) for t in templates],
    )


@router.post("/r/{code_str}/generate", response_model=RedeemGenerateResponse)
def redeem_generate(
    code_str: str,
    payload: RedeemGenerateRequest,
    db: Session = Depends(get_db),
) -> RedeemGenerateResponse:
    """팬이 템플릿을 골라 생성. 자유 프롬프트 불가. 크리에이터 쿼터 + 코드 사용 차감."""
    code = _get_redeemable_code(db, code_str)

    template = (
        db.query(GenerationTemplate)
        .filter(
            GenerationTemplate.id == payload.template_id,
            GenerationTemplate.creator_id == code.creator_id,
            GenerationTemplate.avatar_id == code.avatar_id,
            GenerationTemplate.deleted_at.is_(None),
            GenerationTemplate.is_active == True,  # noqa: E712
        )
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not available for this code.")
    if code.template_id is not None and code.template_id != template.id:
        raise HTTPException(status_code=403, detail="This code is restricted to a specific template.")

    avatar = db.query(Avatar).filter(Avatar.id == code.avatar_id).first()
    if not avatar or avatar.deleted_at is not None or not avatar.lora_path:
        raise HTTPException(status_code=400, detail="Avatar not available.")

    creator = db.query(User).filter(User.id == code.creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found.")
    sub = _get_subscription(db, creator)
    if not sub or sub.status != SubscriptionStatus.ACTIVE.value or sub.quota_remaining <= 0:
        raise HTTPException(status_code=409, detail="Creator has no quota left. Please try later.")

    generation = _run_generation(
        db,
        creator=creator,
        avatar=avatar,
        prompt=template.prompt,
        negative_prompt=template.negative_prompt,
        image_size=template.image_size or "portrait_4_3",
        num_inference_steps=template.num_inference_steps or 8,
        lora_scale=template.lora_scale if template.lora_scale is not None else 1.6,
        output_format="png",
        seed=payload.seed,
        source="fan",
        buyer_id=None,
        redeem_code=code,
        template=template,
    )

    if generation.status == GenerationStatus.SUCCESS.value:
        code.used_count += 1
        db.commit()
        db.refresh(code)

    uses_left = None if code.max_uses is None else max(0, code.max_uses - code.used_count)
    return RedeemGenerateResponse(
        status=generation.status,
        image_url=generation.image_url,
        fail_reason=generation.fail_reason,
        uses_left=uses_left,
    )
