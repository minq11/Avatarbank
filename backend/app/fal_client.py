"""
fal.ai 클라이언트 — image-to-image + LoRA.

엔드포인트: fal-ai/z-image/turbo/image-to-image/lora
  prompt              (필수)
  image_url           (필수) — 공개 URL 또는 base64 data URI
  strength            0 초과 ~ 1, 기본 0.6 (낮을수록 원본 유지, 높을수록 프롬프트 반영)
  loras[]             최대 3개, {path, scale} — scale 0~4
  num_inference_steps 1~8
  image_size          auto | square_hd | square | portrait_4_3 | portrait_16_9
                      | landscape_4_3 | landscape_16_9   (auto = 입력 이미지 비율 유지)

주의: 이 엔드포인트에는 negative_prompt 파라미터가 없다. 호출부는 계속 값을 받아
DB 에 기록하되 fal 로는 보내지 않는다.

이미지 전달 방식은 data URI 기본 (로컬 개발에서도 fal 이 접근 가능해야 하므로).
"""

import base64
import mimetypes
from pathlib import Path
from typing import Any, Optional

import httpx

from .config import settings

# 기본 소스 이미지 (사용자가 업로드하지 않았을 때)
DEFAULT_SOURCE_IMAGE = Path(__file__).parent / "assets" / "itoi_example.png"

# 1.7MB 파일을 매 호출마다 읽고 base64 인코딩하지 않도록 캐시.
_default_data_uri_cache: Optional[str] = None


def to_data_uri(raw: bytes, content_type: str = "image/png") -> str:
    """바이트 → base64 data URI."""
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{content_type};base64,{encoded}"


def default_source_image_data_uri() -> str:
    """기본 소스 이미지의 data URI (프로세스 내 캐시)."""
    global _default_data_uri_cache
    if _default_data_uri_cache is None:
        if not DEFAULT_SOURCE_IMAGE.exists():
            raise RuntimeError(f"기본 소스 이미지가 없습니다: {DEFAULT_SOURCE_IMAGE}")
        content_type = mimetypes.guess_type(DEFAULT_SOURCE_IMAGE.name)[0] or "image/png"
        _default_data_uri_cache = to_data_uri(
            DEFAULT_SOURCE_IMAGE.read_bytes(), content_type
        )
    return _default_data_uri_cache


def resolve_source_image(source_image_url: Optional[str]) -> str:
    """
    생성에 쓸 image_url 을 결정한다.
      - None/빈 값        → 기본 이미지 data URI
      - 이미 data URI     → 그대로
      - S3 URL           → 바이트를 받아 data URI 로 변환 (실패 시 기본 이미지)
      - 그 외 공개 URL    → 그대로 (fal 이 직접 받아감)
    """
    if not source_image_url or not source_image_url.strip():
        return default_source_image_data_uri()

    url = source_image_url.strip()
    if url.startswith("data:"):
        return url

    if "amazonaws" in url:
        from .s3_utils import download_s3_bytes

        fetched = download_s3_bytes(url)
        if fetched is None:
            return default_source_image_data_uri()
        raw, content_type = fetched
        return to_data_uri(raw, content_type)

    return url


def _normalize_model_and_subpath() -> tuple[str, str]:
    model = settings.FAL_MODEL.strip("/")
    subpath = settings.FAL_SUBPATH.strip("/")

    if not subpath and model.endswith("/lora"):
        model = model[: -len("/lora")]
        subpath = "lora"

    return model, subpath


def _build_url(suffix: str) -> str:
    base_url = settings.FAL_API_BASE_URL.rstrip("/")
    model, _ = _normalize_model_and_subpath()
    return f"{base_url}/{model}{suffix}"


def _build_sync_url() -> str:
    base_url = settings.FAL_SYNC_BASE_URL.rstrip("/")
    model, subpath = _normalize_model_and_subpath()
    if subpath:
        return f"{base_url}/{model}/{subpath}"
    return f"{base_url}/{model}"


def _headers() -> dict[str, str]:
    if not settings.FAL_API_KEY:
        raise RuntimeError("FAL_API_KEY is not configured")
    return {
        "Authorization": f"Key {settings.FAL_API_KEY}",
        "Content-Type": "application/json",
    }


def get_status(request_id: str) -> dict[str, Any]:
    status_url = _build_url(f"/requests/{request_id}/status")
    with httpx.Client(timeout=30) as client:
        response = client.get(status_url, headers=_headers())
        if response.status_code == 405:
            raise RuntimeError(
                "fal.ai queue status endpoint returned 405. "
                "Check FAL_MODEL/FAL_SUBPATH (subpath must not be used for status). "
                f"status_url={status_url}"
            )
        response.raise_for_status()
        return response.json()


def get_result(request_id: str) -> dict[str, Any]:
    url = _build_url(f"/requests/{request_id}")
    with httpx.Client(timeout=60) as client:
        response = client.get(url, headers=_headers())
        response.raise_for_status()
        return response.json()


def run_generation_sync(
    prompt: str,
    *,
    source_image_url: str | None = None,
    strength: float = 0.6,
    lora_url: str | None = None,
    lora_scale: float = 2.0,
    enable_safety_checker: bool = True,
    image_size: str = "auto",
    num_inference_steps: int = 8,
    output_format: str = "png",
    seed: int | None = None,
) -> dict[str, Any]:
    """
    fal-ai/z-image/turbo/image-to-image/lora 동기 호출.

    source_image_url 이 비면 기본 이미지(itoi_example)를 쓴다.
    negative_prompt 는 이 엔드포인트에 없으므로 받지 않는다 (DB 기록은 호출부 담당).
    """
    payload: dict[str, Any] = {
        "prompt": prompt,
        "image_url": resolve_source_image(source_image_url),
        # 0 초과 1 이하로 강제 (fal 이 0 을 거부함)
        "strength": min(max(float(strength), 0.01), 1.0),
        "num_images": 1,
        "enable_safety_checker": enable_safety_checker,
        "image_size": image_size,
        # 이 엔드포인트의 상한은 8
        "num_inference_steps": min(max(int(num_inference_steps), 1), 8),
        "output_format": output_format,
    }
    if seed is not None:
        payload["seed"] = seed
    if lora_url:
        payload["loras"] = [{"path": lora_url, "scale": min(max(float(lora_scale), 0.0), 4.0)}]

    url = _build_sync_url()
    with httpx.Client(timeout=180) as client:
        response = client.post(url, json=payload, headers=_headers())
        if response.status_code >= 400:
            # httpx 의 raise_for_status() 는 상태코드만 알려주고 본문을 버린다.
            # fal 은 거절 사유를 본문에 담아 주므로(예: 입력 이미지 거절) 그대로 올린다.
            raise RuntimeError(
                f"fal {response.status_code} 응답: {_extract_fal_error(response)}"
            )
        return response.json()


def _extract_fal_error(response: Any) -> str:
    """fal 오류 응답에서 사람이 읽을 사유를 뽑는다. 실패하면 원문 일부를 그대로."""
    try:
        data = response.json()
    except Exception:
        return (response.text or "")[:500] or "(본문 없음)"

    detail = data.get("detail") if isinstance(data, dict) else None
    if isinstance(detail, list):
        parts = []
        for d in detail:
            if isinstance(d, dict):
                loc = ".".join(str(x) for x in (d.get("loc") or []))
                msg = d.get("msg") or d.get("type") or str(d)
                parts.append(f"{loc}: {msg}" if loc else str(msg))
            else:
                parts.append(str(d))
        return " | ".join(parts)[:500]
    if detail:
        return str(detail)[:500]
    return str(data)[:500]
