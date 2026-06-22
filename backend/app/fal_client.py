from typing import Any

import httpx

from .config import settings


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


def submit_generation(prompt: str) -> str:
    payload = {
        "prompt": prompt,
        "num_images": 1,
        "enable_safety_checker": True,
    }

    _, subpath = _normalize_model_and_subpath()
    url = _build_url(f"/{subpath}") if subpath else _build_url("")
    with httpx.Client(timeout=30) as client:
        response = client.post(url, json=payload, headers=_headers())
        response.raise_for_status()
        data = response.json()

    request_id = data.get("request_id") or data.get("requestId")
    if not request_id:
        raise RuntimeError("fal.ai queue response missing request_id")
    return request_id


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
    lora_url: str | None = None,
    lora_scale: float = 1.6,
    negative_prompt: str | None = None,
    enable_safety_checker: bool = True,
    image_size: str = "landscape_4_3",
    num_inference_steps: int = 8,
    output_format: str = "png",
    seed: int | None = None,
) -> dict[str, Any]:
    """
    fal-ai/z-image/turbo/lora 동기 호출.
    lora_url이 있으면 해당 LoRA를 적용 (scale 0~4, 기본 1).
    """
    # SFW 전용 정책: NSFW 비활성. 호출자가 무엇을 보내든 항상 safety checker ON.
    # (Creator Studio 피벗 — 결제사/앱스토어/딥페이크 법 리스크 회피)
    payload: dict[str, Any] = {
        "prompt": prompt,
        "num_images": 1,
        "enable_safety_checker": True,
        "image_size": image_size,
        "num_inference_steps": num_inference_steps,
        "output_format": output_format,
    }
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    if seed is not None:
        payload["seed"] = seed
    if lora_url:
        payload["loras"] = [{"path": lora_url, "scale": lora_scale}]
    url = _build_sync_url()
    with httpx.Client(timeout=120) as client:
        response = client.post(url, json=payload, headers=_headers())
        response.raise_for_status()
        return response.json()
