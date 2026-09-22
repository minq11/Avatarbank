"""
프롬프트 번역 회귀 테스트.

번역은 보조 장치다. 여기서 막고 싶은 사고는 "번역기가 죽어서 이미지 생성까지
막히는 것" — 사용자는 크레딧을 쓰려고 왔는데 우리 쪽 번역 API 장애로 아무것도
못 하게 되는 상황이다. 그래서 **모든 실패는 원문 통과(fail-open)** 여야 한다.

Gemini 를 실제로 호출하지 않는다. 호출하면 테스트가 네트워크·키·할당량에
묶여서 CI 에서도 로컬에서도 못 돌린다. httpx.Client 를 가짜로 바꿔
응답 형태만 재현한다.
"""

import httpx
import pytest

from app import translate
from app.translate import contains_korean, to_english_prompt

KOREAN = "노을 지는 바닷가에서 흰 원피스 입고"


# ---------------------------------------------------------------------------
# 가짜 httpx
# ---------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, status_code: int, payload=None, text: str = ""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


def _install_fake_httpx(monkeypatch, handler):
    """
    translate 가 쓰는 httpx.Client 를 가짜로 바꾼다.
    handler(url, json, headers) 가 _FakeResponse 를 돌려주거나 예외를 던진다.
    """
    calls = []

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def post(self, url, json=None, headers=None):
            calls.append({"url": url, "json": json, "headers": headers})
            return handler(url, json, headers)

    monkeypatch.setattr(translate.httpx, "Client", _FakeClient)
    return calls


def _gemini_ok(text: str):
    def handler(url, json, headers):
        return _FakeResponse(
            200, {"candidates": [{"content": {"parts": [{"text": text}]}}]}
        )

    return handler


@pytest.fixture(autouse=True)
def _reset_cache():
    """
    lru_cache 는 프로세스 전역이다. 비우지 않으면 앞 테스트의 결과가
    뒤 테스트로 새서, 호출도 안 했는데 번역이 되는 것처럼 보인다.
    """
    translate._translate_cached.cache_clear()
    yield
    translate._translate_cached.cache_clear()


@pytest.fixture()
def gemini_on(monkeypatch):
    """번역 기능이 켜지고 키가 설정된 상태."""
    monkeypatch.setattr(translate.settings, "TRANSLATE_PROVIDER", "gemini")
    monkeypatch.setattr(translate.settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(translate.settings, "GEMINI_MODEL", "gemini-3.6-flash")


# ---------------------------------------------------------------------------
# 한글 판별 — 번역 호출 여부를 결정하므로 비용과 직결된다
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    ["여자", "해변의 금발", "beach 에서", "ㅋㅋ", "안경"],
)
def test_한글이_있으면_True(text):
    assert contains_korean(text) is True


@pytest.mark.parametrize(
    "text",
    ["a woman at the beach", "", None, "2024", "!!!", "光"],
)
def test_한글이_없으면_False(text):
    assert contains_korean(text) is False


# ---------------------------------------------------------------------------
# 호출하지 않아야 하는 경우
# ---------------------------------------------------------------------------


def test_기능이_꺼져_있으면_원문_그대로(monkeypatch):
    monkeypatch.setattr(translate.settings, "TRANSLATE_PROVIDER", "none")
    calls = _install_fake_httpx(monkeypatch, _gemini_ok("translated"))

    assert to_english_prompt(KOREAN) == KOREAN
    assert calls == []


def test_영어_입력은_호출하지_않는다(monkeypatch, gemini_on):
    calls = _install_fake_httpx(monkeypatch, _gemini_ok("translated"))
    text = "a woman wearing a white dress at the beach"

    assert to_english_prompt(text) == text
    assert calls == []


def test_키가_비어_있으면_원문_그대로(monkeypatch, gemini_on):
    """설정 실수로 서비스가 멈추면 안 된다. 경고만 남기고 통과시킨다."""
    monkeypatch.setattr(translate.settings, "GEMINI_API_KEY", "")
    calls = _install_fake_httpx(monkeypatch, _gemini_ok("translated"))

    assert to_english_prompt(KOREAN) == KOREAN
    assert calls == []


@pytest.mark.parametrize("text", ["", "   ", "\n"])
def test_빈_입력은_그대로_돌려준다(monkeypatch, gemini_on, text):
    calls = _install_fake_httpx(monkeypatch, _gemini_ok("translated"))

    assert to_english_prompt(text) == text
    assert calls == []


# ---------------------------------------------------------------------------
# 정상 경로
# ---------------------------------------------------------------------------


def test_한국어는_영어로_바뀐다(monkeypatch, gemini_on):
    _install_fake_httpx(
        monkeypatch, _gemini_ok("wearing a white dress at a beach at sunset")
    )

    assert to_english_prompt(KOREAN) == "wearing a white dress at a beach at sunset"


def test_키는_헤더로만_보낸다(monkeypatch, gemini_on):
    """쿼리스트링에 넣으면 프록시·액세스 로그에 키가 그대로 남는다."""
    calls = _install_fake_httpx(monkeypatch, _gemini_ok("translated"))
    to_english_prompt(KOREAN)

    assert calls[0]["headers"]["x-goog-api-key"] == "test-key"
    assert "test-key" not in calls[0]["url"]


def test_설정한_모델로_호출한다(monkeypatch, gemini_on):
    monkeypatch.setattr(translate.settings, "GEMINI_MODEL", "gemini-9-ultra")
    calls = _install_fake_httpx(monkeypatch, _gemini_ok("translated"))
    to_english_prompt(KOREAN)

    assert "gemini-9-ultra:generateContent" in calls[0]["url"]


def test_창작_여지를_없애려_temperature_0_으로_보낸다(monkeypatch, gemini_on):
    """직역이어야 한다. 온도가 올라가면 사용자가 쓰지 않은 말이 붙는다."""
    calls = _install_fake_httpx(monkeypatch, _gemini_ok("translated"))
    to_english_prompt(KOREAN)

    assert calls[0]["json"]["generationConfig"]["temperature"] == 0.0


@pytest.mark.parametrize(
    "raw",
    [
        "Here is the translation: a blonde woman at the beach",
        "Translation: a blonde woman at the beach",
        '"a blonde woman at the beach"',
        "  a blonde woman at the beach  ",
    ],
)
def test_모델이_붙인_군말과_인용부호를_걷어낸다(monkeypatch, gemini_on, raw):
    """
    번역 결과는 그대로 fal 프롬프트가 된다. "Here is the translation:" 이
    남으면 그 문장까지 이미지에 반영되려 한다.
    """
    _install_fake_httpx(monkeypatch, _gemini_ok(raw))

    assert to_english_prompt("해변의 금발의 여자") == "a blonde woman at the beach"


def test_같은_프롬프트는_한_번만_호출한다(monkeypatch, gemini_on):
    """리딤 링크로 배포된 같은 프롬프트를 여러 팬이 쓰는 경우를 노린 캐시."""
    calls = _install_fake_httpx(monkeypatch, _gemini_ok("translated"))

    assert to_english_prompt(KOREAN) == "translated"
    assert to_english_prompt(KOREAN) == "translated"
    assert to_english_prompt(f"  {KOREAN}  ") == "translated"

    assert len(calls) == 1


# ---------------------------------------------------------------------------
# 실패 = 원문 통과 (fail-open). 번역 장애로 생성이 막히면 안 된다
# ---------------------------------------------------------------------------


def _raising(exc):
    def handler(url, json, headers):
        raise exc

    return handler


@pytest.mark.parametrize(
    "exc",
    [
        httpx.ConnectError("connection refused"),
        httpx.ReadTimeout("timed out"),
        httpx.HTTPError("boom"),
    ],
)
def test_네트워크_실패는_원문으로_통과한다(monkeypatch, gemini_on, exc):
    _install_fake_httpx(monkeypatch, _raising(exc))

    assert to_english_prompt(KOREAN) == KOREAN


@pytest.mark.parametrize("status_code", [400, 404, 429, 500, 503])
def test_오류_응답은_원문으로_통과한다(monkeypatch, gemini_on, status_code):
    """
    404 는 실제로 겪은 경우다 — 모델 이름이 폐기되면 Gemini 가 404 를 준다.
    그때도 이미지 생성은 계속돼야 한다 (한국어가 그대로 나가 품질만 떨어진다).
    """

    def handler(url, json, headers):
        return _FakeResponse(status_code, {"error": {"message": "nope"}}, text="nope")

    _install_fake_httpx(monkeypatch, handler)

    assert to_english_prompt(KOREAN) == KOREAN


def test_안전_필터로_결과가_비면_원문으로_통과한다(monkeypatch, gemini_on):
    """Gemini 안전 필터에 걸리면 candidates 가 빈 배열로 온다."""

    def handler(url, json, headers):
        return _FakeResponse(
            200, {"candidates": [], "promptFeedback": {"blockReason": "SAFETY"}}
        )

    _install_fake_httpx(monkeypatch, handler)

    assert to_english_prompt(KOREAN) == KOREAN


@pytest.mark.parametrize(
    "payload",
    [
        {"candidates": [{"content": {"parts": [{"text": "   "}]}}]},  # 공백만
        {"candidates": [{"content": {"parts": []}}]},                 # parts 없음
        {"candidates": [{"content": {}}]},                            # content 비어 있음
        {"candidates": [{}]},                                         # 후보가 빈 객체
    ],
)
def test_빈_번역_결과는_원문으로_통과한다(monkeypatch, gemini_on, payload):
    def handler(url, json, headers):
        return _FakeResponse(200, payload)

    _install_fake_httpx(monkeypatch, handler)

    assert to_english_prompt(KOREAN) == KOREAN


def test_응답이_JSON_이_아니어도_원문으로_통과한다(monkeypatch, gemini_on):
    def handler(url, json, headers):
        return _FakeResponse(200, None, text="<html>gateway error</html>")

    _install_fake_httpx(monkeypatch, handler)

    assert to_english_prompt(KOREAN) == KOREAN
