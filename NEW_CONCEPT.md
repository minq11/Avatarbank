# AvatarBank → Creator Studio (피벗 설계서)

> 이 문서는 기존 "인플루언서 아바타 마켓플레이스"에서 **"크리에이터 구독형 AI 얼굴 스튜디오 + 팬 리딤 코드"** 로의
> 전환 설계를 정리한 것입니다. 작업 브랜치: `claude/bold-goldberg-ch5bxp`.

---

## 1. 새 컨셉 한 줄 정의

**크리에이터(인플루언서)가 본인 얼굴을 학습시킨 AI 모델로 콘텐츠를 만들고, 그 생성권을 팬에게 코드로 나눠주는 B2B 구독 SaaS.**

- 고객 = **크리에이터** (당신에게 **월 구독료**를 냄)
- 구독 요금제(Plan) → **월 생성 쿼터**(이미지 장수) 지급
- 크리에이터는 쿼터를:
  1. **본인이 직접** 콘텐츠 생성에 사용하거나
  2. **팬에게 일회용/다회용 코드**로 배포 (팬은 코드로 생성 → 결과물 공유 → 바이럴)
- **NSFW는 전면 비활성 (SFW only).** 모델/DB에 토글은 남기되 강제 OFF.
  - 이유: 결제사 통과, 앱스토어, 한국 딥페이크 법 리스크 회피. (자세한 건 대화 기록 참고)
- **팬은 자유 프롬프트 불가.** 크리에이터가 만든 **템플릿(승인된 프리셋)** 안에서만 생성 →
  크리에이터가 자기 얼굴이 어떻게 쓰일지 100% 통제. (딥페이크/오용 차단의 핵심)

## 2. 왜 이 구조인가 (요약)

- **분배 문제 해결**: 크리에이터가 자기 팬을 데려옴 → 우리는 트래픽 0이어도 됨.
- **반복 매출**: 구독.
- **기존 코드 80% 재사용**: 학습/생성/크레딧 트랜잭션/갤러리 그대로.
- **법적 안전**: SFW + 본인 동의 + 템플릿 통제.

## 3. 도메인 모델 변화

### 유지 (재사용)
- `User` — 크리에이터 = 유저. (role: `influencer` = 크리에이터)
- `Avatar` — **크리에이터의 얼굴(LoRA) 모델**. (의미만 재해석)
- `TrainingRequest` — 얼굴 학습 요청 파이프라인.
- `Generation` — 생성 기록 (컬럼 추가).
- `Transaction` — 정산/쿼터 변동 기록.

### 신규 테이블
| 테이블 | 역할 |
|---|---|
| `plans` | 구독 요금제 (코드/이름/월 쿼터/가격/아바타·코드 한도/NSFW허용) |
| `subscriptions` | 크리에이터의 구독 상태 + 남은 쿼터 + 갱신일 |
| `redeem_codes` | 팬 배포용 코드 (1회/다회/무제한, 만료, 사용 횟수, 연결된 아바타·템플릿) |
| `generation_templates` | 크리에이터가 승인한 생성 프리셋 (프롬프트 고정) — 팬은 이 안에서만 |

### `generations` 컬럼 추가 (nullable, 기존 무영향)
- `creator_id` — 생성 귀속 크리에이터 (쿼터 소유자)
- `redeem_code_id` — 팬 코드로 생성된 경우
- `template_id` — 사용된 템플릿
- `source` — `"self"`(크리에이터 직접) | `"fan"`(코드 리딤)

> `buyer_id` 는 nullable 로 완화 (팬 생성은 회원 아님).

## 4. SFW 강제

- `fal_client.run_generation_sync` 는 항상 `enable_safety_checker=True` 로 호출.
- 신규 생성 경로(studio)는 클라이언트가 보낸 NSFW 관련 값을 **무시**하고 안전장치 강제.
- `Plan.allow_nsfw` 는 미래 확장용으로 두되 현재 전부 `False`, 코드 레벨에서도 OFF.

## 5. 신규 API (라우터: `app/studio.py`, prefix 없음)

### 요금제 / 구독 (크리에이터)
- `GET  /plans` — 요금제 목록 (공개)
- `GET  /my/subscription` — 내 구독 + 남은 쿼터
- `POST /my/subscription` — 구독/요금제 변경 *(결제 미연동 스텁: 즉시 활성 + 쿼터 충전)*

### 템플릿 (크리에이터)
- `GET    /my/templates`
- `POST   /my/templates` — 아바타+이름+프롬프트로 프리셋 생성
- `DELETE /my/templates/{id}`

### 리딤 코드 (크리에이터)
- `GET    /my/codes`
- `POST   /my/codes` — 코드 발급 (아바타, 템플릿?, 최대횟수, 개수, 만료)
- `DELETE /my/codes/{id}` — 비활성화

### 생성
- `POST /my/generate` — 크리에이터 본인 생성 (쿼터 차감, SFW)
- `GET  /r/{code}` — (공개) 코드 정보 + 사용 가능 템플릿 미리보기
- `POST /r/{code}/generate` — (공개) 팬이 템플릿으로 생성 (크리에이터 쿼터 + 코드 사용 차감, SFW)

## 6. 프론트 변화
- `App.vue` — 네비게이션: 크리에이터용 **Studio** 진입, 브랜드 카피 SFW/크리에이터 톤으로.
- 신규 페이지:
  - `CreatorStudioPage.vue` (`/studio`) — 구독/쿼터, 템플릿 관리, 코드 발급/목록.
  - `RedeemPage.vue` (`/r/:code`) — 팬이 코드로 들어와 템플릿 고르고 생성/다운로드. (비로그인)
- `services/api.ts` — `plansApi`, `subscriptionApi`, `templatesApi`, `codesApi`, `redeemApi` 추가.

## 7. 남은 일 (사람 결정 필요)
- 실제 **결제 연동**(Stripe 등) — 구독 POST 는 현재 스텁.
- 요금제 가격/쿼터 수치 확정 (현재 임시값: Free 10 / Starter 300 / Pro 1000 / Studio 3000).
- 마이그레이션 적용: `python migrations/add_studio_tables.py` (신규).
- 기존 공개 마켓(`/avatars`, `/gallery`)을 유지할지/숨길지 — 현재는 유지(재사용 가능).
- 프론트 신규 페이지는 **런타임 검증 전** (DB/빌드 환경 없음). 리뷰 후 `npm run dev` 로 확인 필요.
