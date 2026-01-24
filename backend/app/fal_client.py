from typing import Any

import httpx

from .config import settings


def _build_url(suffix: str) -> str:
    base_url = settings.FAL_API_BASE_URL.rstrip("/")
    model = settings.FAL_MODEL.strip("/")
    return f"{base_url}/{model}{suffix}"


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

    url = _build_url("/queue")
    with httpx.Client(timeout=30) as client:
        response = client.post(url, json=payload, headers=_headers())
        response.raise_for_status()
        data = response.json()

    request_id = data.get("request_id") or data.get("requestId")
    if not request_id:
        raise RuntimeError("fal.ai queue response missing request_id")
    return request_id


def get_status(request_id: str) -> dict[str, Any]:
    url = _build_url(f"/queue/{request_id}")
    with httpx.Client(timeout=30) as client:
        response = client.get(url, headers=_headers())
        response.raise_for_status()
        return response.json()


def get_result(request_id: str) -> dict[str, Any]:
    url = _build_url(f"/queue/{request_id}/result")
    with httpx.Client(timeout=60) as client:
        response = client.get(url, headers=_headers())
        response.raise_for_status()
        return response.json()
