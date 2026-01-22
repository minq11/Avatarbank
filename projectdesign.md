# Avatarbank 개발 설계서

---

## 1. 프로젝트 개요

### 1.1 프로젝트명

**Avatarbank**

### 1.2 서비스 정의

Avatarbank는 **인플루언서의 외형(얼굴/체형)을 기반으로 학습된 AI 아바타**를 활용해 이미지를 생성하고,  
**이미지 1회 생성 단위로 수익이 발생·분배되는 AI 아바타 마켓플레이스**이다.

- **AI 모델 자체는 판매하지 않는다**
- **모든 수익은 "이미지 생성" 행위에서만 발생한다**
- **크레딧 기반 내부 경제 시스템**을 사용한다

---

## 2. 사용자 역할 정의

### 2.1 Influencer (모델 제공자)

- 인스타그램 **공개 계정** 보유
- 팔로워 **1,000명 이상**
- 본인 사진 업로드 및 **학습 동의**
- 아바타가 사용될 때마다 **크레딧 수익 획득**
- 크레딧을 **USD로 환전 가능**

### 2.2 Buyer (구매자)

- 플랫폼 내 **크레딧 구매 가능**
- 아바타 선택 후 **이미지 생성 가능**
- **생성 옵션 크레딧(추가 금액)** 설정 가능
- **환전 불가(현금화 불가)**

### 2.3 Admin

- 모델 **승인 및 관리**
- **NSFW 설정** 관리
- 정산 및 **환전 승인**
- **AI 학습 파이프라인 관리**

---

## 3. 핵심 정책 (절대 변경 금지)

1. **아바타 모델은 플랫폼 자산이다.**
2. **Influencer만 환전 가능하다.**
3. **Buyer는 크레딧을 벌 수 있으나 현금화는 불가하다.**
4. **모든 생성은 Z IMAGE TURBO + ComfyUI로만 처리한다.**
5. **모든 이미지 생성은 서버 측에서만 수행한다.**

---

## 4. 기술 스택

### 4.0 Frontend

- **언어**: TypeScript
- **프레임워크**: **Vue 3**
  - (선택) **Nuxt 3**: 마켓/갤러리 페이지의 SEO 및 초기 로딩 최적화를 위해 SSR/SSG 활용
  - (대안) Vite 기반 SPA: MVP 속도 우선 시 선택
- **라우팅**
  - Nuxt 사용 시: 파일 기반 라우팅
  - Vue SPA 사용 시: Vue Router
- **상태 관리**
  - 전역 상태: **Pinia**
  - 서버 상태(아바타 목록/생성 상태 등): TanStack Query(Vue) 또는 Pinia + Axios 패턴 중 택1
- **스타일링**: (선택) TailwindCSS 또는 CSS Modules/SCSS
- **i18n(다국어)**: EN 기본 + KO/JA 지원 (16장 정책 준수)
  - `vue-i18n` 기반, 키 리소스(`en.json`, `ko.json`, `ja.json`)로 UI 텍스트 분리
  - 헤더 중앙 내비게이션에 **언어 콤보박스(EN/KO/JA)** 제공
- **Backend 연동**: HTTPS REST API(JSON)
  - 생성 요청/상태 조회는 폴링(기본) 또는 SSE/WebSocket(향후)

### 4.1 AI

- **Z IMAGE TURBO**
- **ComfyUI**
- **LoRA 기반 개인 모델 학습**

### 4.2 Backend

- **언어**: Python 3.x
- **웹 프레임워크**: **FastAPI**
  - REST API 제공 (JSON)
  - 인증/인가 및 정책 검증(프롬프트 필터 등)
- **비동기 작업 큐**: **Celery**
  - 이미지 생성/학습 요청을 비동기 태스크로 처리
- **Queue/브로커**: **Redis**
  - Celery broker/결과 백엔드(운영 선택)
- **Webhook Listener**: **PayPal Webhook** 수신/검증 엔드포인트
  - 결제 완료 이벤트 → 크레딧 지급/트랜잭션 기록

> 구현 언어를 Python으로 통일하여, Backend/Celery Worker/RunPods Worker(요청/결과 처리)까지 동일한 개발 경험을 유지한다.

### 4.3 Infra

- **API Server**: **AWS EC2**
  - FastAPI 운영 (HTTPS)
- **DB**: **NeonDB (PostgreSQL)**
  - 사용자/아바타/생성/트랜잭션/태스크/로그 테이블 저장
- **오브젝트 스토리지**: **AWS S3**
  - 생성 이미지 및 학습 산출물(로그/모델 경로 등) 저장
- **GPU Worker**: **RunPods (A40 GPU)**
  - ComfyUI + Z IMAGE TURBO 실행 환경
- **Queue**: **Redis**
  - Celery broker/결과 저장 및 캐시(운영 선택)

---

## 5. 전체 아키텍처

```text
[Frontend]
  ↓
[FastAPI Backend]
  ↓
[Celery Queue]
  ↓
[RunPods GPU Worker]
  ↓
[ComfyUI + Z IMAGE TURBO]
  ↓
[S3 저장]
  ↓
[결과 반환]
```

---

### 5.1 프론트엔드 구현(권장)

- **언어**: TypeScript
- **프레임워크**: React 기반(예: Next.js)
  - SSR/SEO(마켓/갤러리) 및 빠른 UX 제공
- **i18n(다국어)**: EN 기본 + KO/JA 지원 (16장 정책 준수)

### 5.2 백엔드/워커 연동 방식(구체)

- **Frontend ↔ Backend**
  - 프로토콜: HTTPS
  - 방식: REST API(JSON)
  - 인증: 로그인 후 토큰 기반(JWT 등) 또는 세션 기반(선택)
  - 주요 흐름:
    - 아바타 목록/상세 조회
    - 이미지 생성 요청 생성
    - 생성 상태 조회(폴링) 또는 알림(향후 WebSocket/SSE)

- **Backend ↔ Celery**
  - 방식: Celery task publish (Redis broker)
  - Backend는 요청 검증/크레딧 처리 후 태스크를 큐에 넣고 즉시 응답(비동기)

- **Celery Worker ↔ RunPods GPU Worker**
  - 방식: RunPods 환경에서 **ComfyUI API** 호출(HTTP, 필요 시 WebSocket)
  - 태스크 내용:
    - 워크플로우 템플릿에 prompt/seed/옵션을 주입
    - ComfyUI에 job 제출 → 완료 확인(폴링/WS) → 산출물(이미지) 처리 → S3 업로드/DB 반영

- **GPU Worker ↔ ComfyUI**
  - 방식: ComfyUI의 API를 사용해 워크플로우를 실행한다.
    - HTTP: 워크플로우 제출(예: `/prompt`) + 결과 폴링(예: `/history/{id}`)
    - (선택) WebSocket: 실행 진행/완료 이벤트 수신
  - 결과:
    - ComfyUI는 일반적으로 워커 로컬에 이미지를 저장하고(예: output 디렉토리), API로 결과 메타데이터를 제공한다.
    - 최종 산출물은 **S3에 업로드**되어 Frontend에 URL로 제공된다.

- **S3 저장 및 결과 반영**
  - **업로드 방식은 A안을 기본(초기 필수)으로 구현한다.**
  - **A안(기본/필수): RunPods(GPU) → S3 Presigned URL로 직접 업로드**
    - **Presigned PUT URL 발급 주체**: **FastAPI(API Server)**가 발급
    - Celery Worker가 ComfyUI 실행 전에 FastAPI를 호출해 Presigned URL을 받음
    - RunPods GPU Worker가 ComfyUI 산출물(이미지 파일)을 Presigned URL로 직접 업로드
    - **업로드 완료 검증**: RunPods가 HMAC 서명된 콜백을 Backend로 전송 → Worker가 콜백 수신 시 성공 처리
    - **폴백**: 콜백 실패/타임아웃 시 Worker가 S3에 HEAD 요청으로 파일 존재 확인
    - 업로드 완료 후 Celery Worker가 `generations.image_url` 및 상태를 업데이트
    - 장점: 대용량 이미지/배치 업로드에 유리, EC2로 이미지가 역전송되지 않음
  - **B안(후순위 대안): RunPods → Celery Worker → S3 업로드**
    - Celery Worker가 ComfyUI API로 산출물(파일/바이너리)을 가져온 뒤(bulk 다운로드),
      boto3 등으로 S3에 업로드한다.
    - 장점: AWS 자격 증명/업로드 로직을 EC2에만 둠
    - 단점: RunPods→EC2→S3로 데이터가 1번 더 이동(트래픽/시간 증가)
  - 업로드 후 공통 처리:
    - `tasks.status` / `generations.status`를 `success` 또는 `failed`로 업데이트
    - 성공 시 `generations.image_url` 업데이트
    - 실패 시 `generations.fail_reason` 및 `error_logs` 기록
    - 필요 시 `transactions` 기록(이미 처리된 경우 생략)

### 5.3 책임 분리(역할)

- **Frontend**
  - 화면/UX, 다국어, 요청 상태 표시, 결과 갤러리/공유 UI
- **FastAPI Backend**
  - 인증/인가, 정책/프롬프트 검증, 크레딧 차감/분배, 결제/환전 처리, 작업 생성/상태 제공
- **Celery/Worker**
  - 장시간 작업(생성/학습) 처리, 재시도/에러 로그 기록
- **GPU Worker(ComfyUI)**
  - 실제 이미지 생성 실행, 생성 산출물 수집/전달

---

### 5.4 배포 토폴로지(서버 구성) 및 “몇 대가 필요한가?”

#### 5.4.1 초창기(최소 구성) — “일단 돌아가게”

> 목표: **비용/운영 복잡도 최소화**. 이중화 없이 단일 구성으로 시작.

**서버 “대수” 관점(초창기 최소)**

- **EC2 1대**: FastAPI + Celery Worker(동일 머신)
- **RunPods GPU 1대**: ComfyUI + Z IMAGE TURBO
- **Redis 1개**, **PostgreSQL(NeonDB) 1개**, **S3 1개**
- Frontend는 정적 호스팅/서버리스(선택) 또는 동일 도메인에서 제공

**필요 서버/서비스(초창기 최소)**

| 구분 | 역할 | 권장 대수(초기) | 비고 |
|------|------|------------------|------|
| Frontend | 웹 앱 제공 | 1 | 정적 호스팅/서버리스 권장(선택) |
| App Server(EC2) | FastAPI + Celery Worker | **1대** | 단일 머신에 합쳐 운영 |
| Redis | Celery broker/캐시 | **1개** | 관리형 또는 단일 Redis |
| PostgreSQL(NeonDB) | DB | **1개** | 관리형(Neon) |
| S3 | 이미지/산출물 저장 | **1개** | 오브젝트 스토리지 |
| RunPods GPU Worker | 이미지 생성 실행 | **GPU 1대** | ComfyUI + Z IMAGE TURBO |

**도식(초창기 최소)**

```text
            ┌──────────────────────────────┐
            │          Users (Web)         │
            └──────────────┬───────────────┘
                           │ HTTPS
                           ▼
                 ┌───────────────────┐
                 │ Frontend (Vue/Nuxt│
                 │  Static/SSR Host) │
                 └─────────┬─────────┘
                           │ HTTPS (REST/JSON)
                           ▼
        ┌────────────────────────────────────────┐
        │             App Server (EC2)            │
        │  Nginx + FastAPI + Celery Worker(같이)  │
        └───────────┬───────────────┬────────────┘
                    │ SQL           │ Publish/Consume (Redis)
                    ▼               ▼
          ┌────────────────┐   ┌────────────────┐
          │ PostgreSQL      │   │ Redis (Broker) │
          │ NeonDB (Managed)│   │ (Managed/EC2)  │
          └────────────────┘   └────────┬───────┘
                                        │ HTTP (ComfyUI API)
                                        ▼
                        ┌──────────────────────────┐
                        │ RunPods GPU Worker (A40) │
                        │  ComfyUI + Z IMAGE TURBO │
                        └───────────┬──────────────┘
                                    │ Upload
                                    ▼
                             ┌────────────┐
                             │   AWS S3    │
                             └────────────┘
```

#### 5.4.2 이후 구성(분리/확장) — “병목 분리 + 스케일링”

> 목표: **오케스트레이션(큐/워커)과 API를 분리**하고, 부하에 따라 각각 수평 확장.

**서버 “대수” 관점(이후 권장)**

- **EC2 2대**: API Server 1대 + Worker Server 1대 (둘 다 단일로 시작)
- **RunPods GPU 1대**에서 시작 → 수요에 따라 **N대로 수평 확장**
- 나머지(Redis/DB/S3)는 그대로 유지

**필요 서버/서비스(이후 분리/확장)**

| 구분 | 역할 | 권장 대수(시작) | 확장 방향 |
|------|------|------------------|----------|
| Frontend | 웹 앱 제공 | 1 | CDN/SSR 최적화 |
| API Server(EC2) | FastAPI | **1대** | 필요 시 2대+ |
| Worker Server(EC2) | Celery Worker | **1대** | 2대+ |
| Redis | Celery broker/캐시 | 1 | 관리형/성능 확장 |
| PostgreSQL(NeonDB) | DB | 1 | 관리형/성능 확장 |
| S3 | 이미지/산출물 저장 | 1 | 그대로 |
| RunPods GPU Worker | 이미지 생성 실행 | 1 | **N대로 수평 확장** |

**도식(이후 분리/확장)**

```text
            ┌──────────────────────────────┐
            │          Users (Web)         │
            └──────────────┬───────────────┘
                           │ HTTPS
                           ▼
                 ┌───────────────────┐
                 │ Frontend (Vue/Nuxt│
                 │  Static/SSR Host) │
                 └─────────┬─────────┘
                           │ HTTPS (REST/JSON)
                           ▼
        ┌───────────────────────────────┐
        │         API Server (EC2)       │
        │   FastAPI + Auth/Policy/Credit │
        └───────────┬───────────┬────────┘
                    │           │ Publish Task (Redis)
                    │ SQL       ▼
                    ▼     ┌────────────────┐
          ┌────────────────┐│ Redis (Broker)│
          │ PostgreSQL      ││ (Managed/EC2) │
          │ NeonDB (Managed)│└───────┬──────┘
          └────────────────┘        │ Consume Task
                                    ▼
                         ┌────────────────────────┐
                         │  Worker Server (EC2)    │
                         │     Celery Worker       │
                         └───────────┬────────────┘
                                     │ HTTP (ComfyUI API)
                                     ▼
                        ┌──────────────────────────┐
                        │ RunPods GPU Worker (A40) │
                        │  ComfyUI + Z IMAGE TURBO │
                        └───────────┬──────────────┘
                                    │ Upload
                                    ▼
                             ┌────────────┐
                             │   AWS S3    │
                             └────────────┘
```

#### 5.4.3 확장 규칙(핵심만)

- **API 병목**: API 응답 지연/CPU 상승 시 → API Server 수평 확장(2→N) + 로드밸런서
- **큐 지연 증가**: `tasks`가 queued에 오래 머무르면 → Celery Worker 수평 확장(1→N)
- **GPU 병목**: 생성 대기시간 증가 시 → RunPods GPU Worker 수평 확장(1→N)


## 6. 크레딧 시스템

### 6.1 크레딧 가치

| 구분   | 비율              |
|--------|-------------------|
| 구매   | **5 Credit = 1 USD**  |
| 환전   | **10 Credit = 1 USD** |

플랫폼은 **구매/환전 비율 차익**을 통해 수익을 확보한다.

---

### 6.2 이미지 생성 시 크레딧 흐름

#### 6.2.1 기본 규칙

- **기본 생성 비용**: 1 Credit (**플랫폼 수익**)
- **추가 옵션 크레딧**: Buyer가 설정 (전액 **Influencer 몫**)

#### 6.2.2 예시

- Buyer가 옵션 크레딧 **4**를 설정한 경우:
  - **총 소모**: 5 Credit
    - **1 Credit → 플랫폼**
    - **4 Credit → Influencer**

---

## 7. 수익 분배 로직

- **Influencer**
  - 자신의 아바타로 이미지가 생성될 때마다 **Credit을 획득**
- **Buyer**
  - 이벤트/프로모션 등을 통해 **Credit을 획득할 수 있으나, 환전(현금화)은 불가**
- **플랫폼**
  - **기본 생성 비용 Credit**
  - **구매/환전 비율 차익**
  - **미환전 Credit 잔액**

---

## 8. 모델 등록 프로세스

1. **Influencer 회원가입**
2. **인스타그램 계정 인증**
3. **사진 업로드**
   - 정면
   - 좌/우
   - 전신
4. **Admin 승인**
5. **LoRA 학습 실행**
6. **샘플 이미지 생성**
7. **Influencer 최종 승인**
8. **공개 상태 전환(마켓에 노출)**

---

## 9. AI 학습 파이프라인

### 9.1 초기 단계

- **로컬 PC에서 LoRA 학습**
- 학습 완료된 모델을 **수동 업로드**

### 9.2 향후 확장

- **학습 자동화 가능 구조로 설계**
- **모델 메타데이터를 DB로 관리**

---

## 10. 이미지 생성 파이프라인

### 10.1 전체 플로우(상세)

1. **Buyer 프롬프트 입력** (Frontend)
   - 프롬프트, 옵션 크레딧, 스타일/해상도 등 입력
   - `idempotency_key` 생성(UUID)

2. **Backend에서 프롬프트 검증 및 정책 필터링** (FastAPI)
   - 프롬프트 정책 검증(NSFW/혐오 표현 등)
   - 크레딧 잔액 확인
   - **Idempotency 체크**: 동일 `idempotency_key` 요청 무시

3. **크레딧 선차감** (FastAPI + DB 트랜잭션)
   - `users.credit_balance` 차감(기본 1C + 옵션 크레딧)
   - `transactions` 기록(`type=generation`, `amount=-총크레딧`)
   - `generations` 레코드 생성(`status=pending`)

4. **Celery 작업 생성 (Queue에 등록)** (FastAPI → Redis)
   - `tasks` 레코드 생성(`status=queued`)
   - Celery task publish(Redis broker)
   - **Backend는 즉시 응답** (비동기 처리)

5. **Celery Worker가 작업 수신** (Celery Worker)
   - Redis에서 task consume
   - `tasks.status` → `running`
   - `generations.status` → `processing`
   - **S3 Presigned PUT URL 발급 요청** (FastAPI 호출)

6. **S3 Presigned URL 발급** (FastAPI)
   - boto3로 Presigned PUT URL 생성(만료: 30분)
   - URL을 Celery Worker에 반환

7. **ComfyUI Workflow 실행** (Celery Worker → RunPods)
   - ComfyUI API에 워크플로우 제출(프롬프트/시드/옵션 주입)
   - **HTTP 폴링**으로 완료 대기(최대 10분 타임아웃)
   - 완료 시 이미지 파일 경로 수신

8. **S3 업로드** (RunPods GPU Worker)
   - 생성된 이미지 파일을 **Presigned URL로 직접 업로드**
   - 업로드 완료 후 **HMAC 서명된 콜백**을 Backend로 전송

9. **업로드 완료 검증** (Celery Worker)
   - 콜백 수신 시 `generations.status` → `success`
   - 콜백 실패/타임아웃 시 **S3 HEAD 요청으로 폴백 검증**

10. **DB 기록 및 결과 반환** (Celery Worker)
    - `generations.image_url` 업데이트(S3 경로)
    - `tasks.status` → `success`
    - 필요 시 `transactions` 기록(이미 처리된 경우 생략)

11. **Frontend 결과 수신** (Frontend)
    - 생성 상태 조회 API 폴링 또는 WebSocket/SSE(향후)
    - 성공 시 이미지 URL 및 메타데이터 표시

### 10.2 실패 처리 플로우

- **타임아웃(10분 초과)**:
  - `generations.status` → `failed`
  - `tasks.status` → `failed`
  - **크레딧 전액 환불** (14.3.2 정책)

- **정책 위반(프롬프트 필터링 실패)**:
  - 즉시 `failed` 처리(재시도 없음)
  - 크레딧 환불 없음

- **네트워크/일시 장애**:
  - 최대 2회 재시도(지수 백오프)
  - 재시도 실패 시 `failed` + 전액 환불

---

## 11. 결제 시스템 (PayPal 기준)

### 11.1 결제 방식

- **PayPal Checkout 사용**
- 결제 완료 후 **Webhook 수신**

### 11.2 Webhook 처리 플로우

1. **Webhook 수신 및 검증**
   - PayPal 서명 검증(위조 방지)
   - `payment_webhooks` 테이블에 원본 payload 저장(`status=received`)

2. **중복 방지 체크**
   - PayPal `event_id` 기준으로 중복 확인
   - 이미 처리된 `event_id`면 무시(`status=ignored`)

3. **결제 검증 (금액·상태·중복 여부 체크)**
   - 금액 일치 확인
   - 결제 상태 확인(`COMPLETED`만 처리)

4. **Credit 지급 (트랜잭션 격리 수준으로 원자성 보장)**
   - `transactions` 기록(`type=purchase`, `amount=+크레딧`)
   - `users.credit_balance` 업데이트
   - `payment_webhooks.status` → `processed`

5. **실패 처리**
   - 처리 실패 시 `payment_webhooks.status` → `failed`
   - `error_logs` 기록
   - 재처리 가능하도록 설계(수동 또는 자동)

---

## 12. 환전 시스템

- **Influencer만 신청 가능**
- **최소 환전 Credit** 기준 설정
- **Admin 승인 후 처리**
- **PayPal Payout 사용** (Influencer에게 USD 송금)

---

## 13. DB 주요 테이블

DB는 크게 **핵심 도메인 테이블**, **태스크/파이프라인 관리 테이블**, **로그/감사 테이블**, **공유/소셜 기능 테이블**, **결제/환전 운영 테이블**로 나눈다.

---

### 13.1 핵심 도메인 테이블

#### 13.1.1 users
| 컬럼            | 설명 / 용도                                             | 비고 예시                            |
|-----------------|---------------------------------------------------------|--------------------------------------|
| `id`            | 사용자 고유 ID (PK)                                     | 자동 증가 정수                       |
| `role`          | 사용자 역할                                             | buyer / influencer / admin           |
| `credit_balance`| 현재 보유 크레딧                                       | 이미지 생성/결제/환전 시 증감        |
| `status`        | 계정 상태                                              | active / suspended / deleted 등      |
| `locale`        | 선호 언어(다국어 설정)                                 | en / ko / ja (기본값: en)            |
| `created_at`    | 계정 생성 시각                                         |                                      |
| `updated_at`    | 계정 정보 마지막 수정 시각                             |                                      |
| `last_login_at` | 마지막 로그인 시각                                     | 활동 분석, 보안 모니터링에 사용      |

#### 13.1.2 avatars
| 컬럼              | 설명 / 용도                                                | 비고 예시                                 |
|-------------------|------------------------------------------------------------|-------------------------------------------|
| `id`              | 아바타 고유 ID (PK)                                       |                                           |
| `influencer_id`   | 아바타 소유 인플루언서 사용자 ID (FK → users.id)          |                                           |
| `title`           | 아바타 이름                                               | 마켓/리스트에서 표시                      |
| `description`     | 아바타 설명                                               | 컨셉, 사용 가이드 등                      |
| `nationality`     | 국적                                                       | ISO 3166-1 alpha-2 코드 (예: US, KR, JP) |
| `gender`          | 성별                                                       | male / female / other / unspecified       |
| `height`          | 키 (cm)                                                    | nullable, 숫자형                          |
| `weight`          | 몸무게 (kg)                                                | nullable, 숫자형                          |
| `special_notes`   | 특이사항                                                   | nullable, 텍스트 필드 (외모 특징, 스타일 등) |
| `lora_path`       | LoRA 모델 파일 경로                                      | S3 경로 또는 스토리지 키                  |
| `nsfw_allowed`    | NSFW 생성 허용 여부                                       | true 시 NSFW 프롬프트 일부 허용           |
| `is_public`       | 마켓/갤러리 노출 여부                                     | false 시 비공개 아바타                    |
| `preview_image_url`| 대표 프리뷰 이미지 URL                                   | 리스트/상세 화면 썸네일                   |
| `status`          | 아바타 상태                                               | pending / active / rejected / hidden 등   |
| `created_at`      | 아바타 등록 시각                                          |                                           |
| `updated_at`      | 아바타 정보 마지막 수정 시각                              |                                           |

#### 13.1.3 generations
| 컬럼         | 설명 / 용도                                                         | 비고 예시                                  |
|--------------|---------------------------------------------------------------------|--------------------------------------------|
| `id`         | 이미지 생성 기록 ID (PK)                                           |                                            |
| `avatar_id`  | 사용된 아바타 ID (FK → avatars.id)                                 | 어떤 인플루언서 아바타인지 추적            |
| `buyer_id`   | 이미지를 생성한 Buyer ID (FK → users.id)                           |                                            |
| `credits_used`| 해당 생성에 사용된 총 크레딧                                      | 1(플랫폼 기본) + 옵션 크레딧               |
| `prompt`     | Buyer가 입력한 프롬프트                                            | 정책/품질 분석용                            |
| `seed`       | 생성에 사용된 시드값                                               | 재생성/재현을 위해 Buyer에게만 공개        |
| `image_url`  | 생성된 이미지 파일 URL                                             | S3 경로                                    |
| `status`     | 생성 작업 상태                                                     | pending / processing / success / failed    |
| `fail_reason`| 실패 시 사유(메시지)                                               | nullable                                   |
| `nsfw_flag`  | NSFW 판정 여부                                                     | true 시 일부 UI/공유 제한                   |
| `created_at` | 생성 요청/완료 시각                                                |                                            |

#### 13.1.4 transactions
| 컬럼           | 설명 / 용도                                                             | 비고 예시                                       |
|----------------|-------------------------------------------------------------------------|-------------------------------------------------|
| `id`           | 트랜잭션 ID (PK)                                                       |                                                 |
| `user_id`      | 해당 트랜잭션의 대상 사용자 ID (FK → users.id)                         |                                                 |
| `type`         | 트랜잭션 유형                                                          | purchase / generation / payout                  |
| `amount`       | 크레딧 단위 금액                                                       | +면 증가, -면 감소                              |
| `currency`     | 통화 단위                                                              | 주로 USD                                        |
| `credit_before`| 트랜잭션 전 크레딧 잔액                                                |                                                 |
| `credit_after` | 트랜잭션 후 크레딧 잔액                                                |                                                 |
| `reference_id` | 관련 엔티티 ID 또는 외부 트랜잭션 ID                                   | PayPal 주문 ID, generations.id, payout.id 등    |
| `created_at`   | 트랜잭션 생성 시각                                                     | 회계/정산 정렬 기준                             |

---

### 13.2 태스크 / 파이프라인 관리 테이블

#### 13.2.1 tasks (이미지 생성 등 작업 단위)
| 컬럼              | 설명 / 용도                                                      | 비고 예시                                        |
|-------------------|------------------------------------------------------------------|--------------------------------------------------|
| `id`              | 태스크 ID (PK)                                                  |                                                  |
| `generation_id`   | 연결된 이미지 생성 ID (FK → generations.id)                     |                                                  |
| `task_type`       | 태스크 종류                                                      | generation / lora_training 등                     |
| `status`          | 태스크 상태                                                      | queued / running / success / failed / canceled   |
| `worker_id`       | 작업을 처리한 워커 식별자                                       | RunPods 인스턴스 ID 등                            |
| `started_at`      | 태스크 시작 시각                                                 |                                                  |
| `finished_at`     | 태스크 종료 시각                                                 |                                                  |
| `retry_count`     | 재시도 횟수                                                      | 장애/안정성 분석용                                |
| `last_error_message`| 마지막 에러 메시지 (실패 시)                                   | nullable                                         |

#### 13.2.2 training_jobs (LoRA 학습 작업)
| 컬럼           | 설명 / 용도                                        | 비고 예시                              |
|----------------|----------------------------------------------------|----------------------------------------|
| `id`           | 학습 작업 ID (PK)                                 |                                        |
| `avatar_id`    | 학습 대상 아바타 ID (FK → avatars.id)             |                                        |
| `status`       | 학습 상태                                         | pending / running / success / failed   |
| `started_at`   | 학습 시작 시각                                    |                                        |
| `finished_at`  | 학습 종료 시각                                    |                                        |
| `log_url`      | 학습 로그 파일/콘솔 로그 위치                     | S3 경로 등                             |
| `error_message`| 실패 시 에러 메시지                               | nullable                               |

---

### 13.3 로그 / 감사 테이블

#### 13.3.1 error_logs (시스템 에러 로그)
| 컬럼             | 설명 / 용도                                             | 비고 예시                             |
|------------------|---------------------------------------------------------|---------------------------------------|
| `id`             | 에러 로그 ID (PK)                                      |                                       |
| `source`         | 에러 발생 소스                                         | backend / worker / webhook / payout 등|
| `level`          | 로그 레벨                                              | error / warning / info                |
| `message`        | 에러 메시지 요약                                       |                                       |
| `stack_trace`    | 스택 트레이스(상세 에러 정보)                          | nullable                              |
| `related_user_id`| 관련 사용자 ID                                         | nullable                              |
| `related_task_id`| 관련 태스크 ID                                         | nullable                              |
| `created_at`     | 로그 생성 시각                                         |                                       |

#### 13.3.2 audit_logs (감사/이벤트 로그)
| 컬럼        | 설명 / 용도                                                        | 비고 예시                                         |
|-------------|--------------------------------------------------------------------|---------------------------------------------------|
| `id`        | 감사/이벤트 로그 ID (PK)                                          |                                                   |
| `user_id`   | 액션을 발생시킨 사용자 ID (시스템 이벤트일 경우 null)             | nullable                                          |
| `action`    | 수행된 액션 종류                                                   | login / logout / avatar_approved / payout_approved 등 |
| `target_type`| 액션 대상 엔티티 종류                                            | avatar / user / payout / generation 등            |
| `target_id` | 액션 대상 엔티티 ID                                               | nullable                                          |
| `metadata`  | 추가 정보(JSONB)                                                  | IP, UA, 변경 전/후 값 등                          |
| `created_at`| 로그 생성 시각                                                     |                                                   |

---

### 13.4 공유 / 소셜 기능 테이블

#### 13.4.1 shared_generations (공유/공개 설정)
| 컬럼          | 설명 / 용도                                         | 비고 예시                                  |
|---------------|-----------------------------------------------------|--------------------------------------------|
| `id`          | 공유 설정 ID (PK)                                  |                                            |
| `generation_id`| 공유 대상 이미지 생성 ID (FK → generations.id)    |                                            |
| `share_token` | 공유 URL용 토큰                                    | 비로그인 공유 링크에 사용                  |
| `is_public`   | 공개 갤러리 노출 여부                              | true 시 Public Gallery에 노출              |
| `created_at`  | 공유 설정 생성 시각                                |                                            |
| `expired_at`  | 공유 만료 시각                                     | nullable, 기간 제한 공유에 사용            |

#### 13.4.2 likes (좋아요)
| 컬럼         | 설명 / 용도                                   | 비고 예시                       |
|--------------|-----------------------------------------------|---------------------------------|
| `id`         | 좋아요 ID (PK)                               |                                 |
| `user_id`    | 좋아요를 누른 사용자 ID (FK → users.id)      |                                 |
| `generation_id`| 좋아요 대상 이미지 생성 ID (FK → generations.id)|                             |
| `created_at` | 좋아요 생성 시각                             |                                 |

#### 13.4.3 bookmarks (북마크)
| 컬럼         | 설명 / 용도                                     | 비고 예시                       |
|--------------|-------------------------------------------------|---------------------------------|
| `id`         | 북마크 ID (PK)                                 |                                 |
| `user_id`    | 북마크한 사용자 ID (FK → users.id)             |                                 |
| `generation_id`| 북마크 대상 이미지 생성 ID (FK → generations.id)|                              |
| `created_at` | 북마크 생성 시각                               |                                 |

---

### 13.5 결제 / 환전 운영 테이블

#### 13.5.1 payment_webhooks (결제 Webhook 로그)
| 컬럼          | 설명 / 용도                                                | 비고 예시                                  |
|---------------|------------------------------------------------------------|--------------------------------------------|
| `id`          | Webhook 로그 ID (PK)                                      |                                            |
| `provider`    | 결제 제공자                                               | paypal 등                                  |
| `event_id`    | 외부 이벤트 ID                                            | PayPal 이벤트 ID                           |
| `payload`     | Webhook 원본 데이터(JSONB)                                | 감사/재처리용                              |
| `status`      | 처리 상태                                                 | received / processed / failed / ignored    |
| `error_message`| 처리 실패 시 에러 메시지                                 | nullable                                   |
| `created_at`  | Webhook 수신 시각                                         |                                            |
| `processed_at`| Webhook 처리 완료 시각                                    | nullable                                   |

#### 13.5.2 payout_requests (환전 요청)
| 컬럼             | 설명 / 용도                                                   | 비고 예시                                      |
|------------------|---------------------------------------------------------------|------------------------------------------------|
| `id`             | 환전 요청 ID (PK)                                            |                                                |
| `user_id`        | 환전을 요청한 Influencer ID (FK → users.id)                 |                                                |
| `credits_requested`| 환전 신청 크레딧 수량                                      | 최소 환전 크레딧 이상인지 검증                 |
| `usd_amount`     | 환전될 USD 금액                                              | 환전 비율(10 Credit = 1 USD)에 따라 계산       |
| `status`         | 환전 요청 상태                                               | pending / approved / rejected / paid / failed  |
| `admin_id`       | 승인/거절 처리한 Admin ID                                    | nullable                                       |
| `reason`         | 거절 사유 또는 기타 메모                                     | nullable                                       |
| `created_at`     | 환전 요청 생성 시각                                          |                                                |
| `updated_at`     | 환전 요청 상태 마지막 수정 시각                              |                                                |
| `payout_tx_id`   | PayPal Payout 트랜잭션 ID                                    | 실제 송금 건과 매핑                            |

---

## 14. 보안 및 정책

### 14.1 기본 정책

- 모든 이미지는 **서버에서만 생성** (클라이언트 측 생성 금지)
- **Prompt 로그 저장** (정책 위반 추적 및 운영용)
- **NSFW 옵션**은 Influencer 설정 기준으로 제한
- **Seed 값은 Buyer에게만 공개**

### 14.2 인증/세션 정책

#### 14.2.1 프론트엔드 ↔ Backend 인증

- **방식**: **JWT (Access Token + Refresh Token)**
- **Access Token 만료**: **1시간**
- **Refresh Token 만료**: **7일**
- Access Token은 HTTP-only 쿠키 또는 Authorization 헤더로 전달
- Refresh Token은 HTTP-only 쿠키로만 전달(보안 강화)

#### 14.2.2 RunPods ↔ Backend 통신 보안

- **RunPods가 Backend로 콜백(업로드 완료/실패) 보낼 때**: **HMAC 서명(공유 시크릿)** 사용
  - Backend가 RunPods에 공유 시크릿을 사전 전달(환경변수/시크릿 매니저)
  - RunPods가 콜백 요청 시 `X-Signature` 헤더에 HMAC-SHA256 서명 포함
  - Backend가 서명 검증 후 처리(위조/재전송 공격 방지)
- **RunPods의 ComfyUI 접근 방식**: **외부 공개 + 접근제어(토큰/Basic Auth) + IP 제한(가능하면)**
  - ComfyUI API는 인증 토큰 또는 Basic Auth로 보호
  - EC2 Worker의 IP만 허용하도록 방화벽 규칙 설정(가능한 경우)

### 14.3 크레딧 처리 규칙(원자성/중복 방지)

#### 14.3.1 크레딧 차감 시점

- **방식**: **요청 시 선차감** (악용 방지 우선)
- 생성 요청 시 즉시 크레딧 차감 → 실패/타임아웃 시 환불 규칙 적용

#### 14.3.2 실패/타임아웃 환불 정책

- **기본 규칙**: **전액 환불(기본 1C 포함)**
- 예외 케이스:
  - 정책 위반(프롬프트 필터링 실패) → 환불 없음(크레딧 소모)
  - 유저 취소 → 케이스별 판단(기본 1C는 플랫폼 유지 가능)

#### 14.3.3 Idempotency(중복 방지)

- **적용 범위**: **생성 요청 + 결제 웹훅 둘 다**
- **생성 요청**: 클라이언트가 `idempotency_key`(UUID)를 헤더에 포함 → Backend가 중복 요청 무시
- **결제 웹훅**: PayPal `event_id` 기준으로 1회만 처리(중복 이벤트 무시)

### 14.4 상태머신 정의

#### 14.4.1 `generations.status` 전이 규칙

- **상태값**: `pending` → `processing` → `success` / `failed` / `canceled`
- **전이 규칙**:
  - `pending`: 생성 요청 직후(크레딧 차감 완료, 큐 대기)
  - `processing`: Celery Worker가 ComfyUI에 작업 제출 후
  - `success`: S3 업로드 완료 + DB 업데이트 완료
  - `failed`: 생성 실패/타임아웃/정책 위반 등
  - `canceled`: 유저/Admin이 수동 취소

#### 14.4.2 `tasks.status` 전이 규칙

- **상태값**: `queued` → `running` → `success` / `failed` / `canceled`
- **전이 규칙**:
  - `queued`: Redis 큐에 등록됨
  - `running`: Celery Worker가 작업 시작
  - `success`: ComfyUI 실행 완료 + S3 업로드 완료
  - `failed`: 네트워크/실행 실패(재시도 가능) 또는 정책 위반(재시도 불가)
  - `canceled`: 수동 취소 또는 타임아웃

#### 14.4.3 재시도 정책

- **네트워크/일시 장애만 최대 2회 재시도**
- **정책 위반/프롬프트 필터링 실패는 재시도 없음** (즉시 `failed`)
- 재시도 간격: 지수 백오프(예: 5초 → 10초 → 20초)

### 14.5 ComfyUI 연동 세부사항

#### 14.5.1 완료 확인 방식

- **방식**: **HTTP 폴링(기본)** + 타임아웃/재시도 로직
- Celery Worker가 ComfyUI API의 `/history/{prompt_id}` 엔드포인트를 주기적으로 폴링(예: 2초 간격)
- **타임아웃**: **10분** (10분 내 완료 안 되면 `failed` 처리)

#### 14.5.2 S3 업로드 완료 검증

- **방식**: **RunPods 콜백 + Worker의 S3 HEAD 폴백**
  1. RunPods가 S3 업로드 완료 후 Backend로 HMAC 서명된 콜백 전송
  2. Worker가 콜백 수신 시 `generations.status`를 `success`로 업데이트
  3. 콜백 실패/타임아웃 시 Worker가 S3에 HEAD 요청으로 파일 존재 확인(폴백)

#### 14.5.3 이미지 포맷

- **기본 포맷**: **PNG**
- **다른 포맷 지원**: WEBP, JPEG 등도 가능(ComfyUI 출력 설정에 따라)
- S3 Key 확장자는 실제 포맷에 맞춰 저장

#### 14.5.4 S3/배포 공개 정책

- **S3 버킷**: **비공개(Private)**
- **이미지 제공**: **CloudFront(또는 S3) 서명 URL로만 제공**
- 서명 URL 만료 시간: 1시간(기본) 또는 설정 가능

### 14.6 결제 웹훅 처리

#### 14.6.1 중복 방지

- **기준**: **PayPal `event_id` 기준으로 1회만 처리**
- `payment_webhooks` 테이블에 `event_id`로 중복 체크 → 이미 처리된 이벤트는 무시

#### 14.6.2 크레딧 지급 처리

- **방식**: **Webhook 수신 즉시 DB 반영(트랜잭션 + idempotency 필수)**
- Webhook 검증(금액/상태) → `transactions` 기록 → `users.credit_balance` 업데이트
- 트랜잭션 격리 수준으로 중복 지급 방지

---

## 15. 확장 고려 사항

- **Video Generation**
- **Avatar Style Pack**
- **Subscription Credit (정기 구독형 크레딧)**
- **Public Gallery (공개 갤러리)**

---

## 16. 국제화 / 다국어(i18n) 정책

- **기본 타깃 사용자는 영어권**으로 가정한다.
- 서비스는 **영어를 기본 언어(Default Locale)**로 사용한다.
- UI 텍스트 및 주요 시스템 메시지는 **영어/한국어/일본어 3개 언어 지원**을 목표로 한다.
- 프론트엔드는 **언어 토글(EN / KO / JA)**을 제공하고, 브라우저/계정 설정에 따라 초기 언어를 결정한다.
- Backend는 다음을 지원해야 한다.
  - 사용자별 **선호 언어(locale)** 필드 (`users` 또는 별도 프로필에 저장)
  - 이메일/알림 등 시스템 메시지를 **선호 언어 기준으로 발송**할 수 있는 구조
- 프롬프트/콘텐츠 관련 정책:
  - Buyer 프롬프트는 **임의 언어로 입력 가능**하되,  
    안전/정책 필터링은 주로 **영어 기준(또는 멀티랭)** 필터를 통과하도록 설계한다.
  - Public Gallery, 마켓 설명 등은 **기본은 영어로 작성**하고, 필요 시 한/일 번역본을 추가하는 방향으로 운영한다.

---

## 17. Cursor 명령 가이드

이 문서를 기준으로:

- **DB Schema 생성**
- **FastAPI 서버 구현**
- **Celery Worker 구현**
- **PayPal Webhook 연동**
- **Credit 로직 정확히 구현**

> **주의:** 추측하지 말고, **문서에 명시된 내용만** 사용하여 개발할 것.
