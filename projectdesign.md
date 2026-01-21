# Avatarbank 개발 설계서

## 1. 프로젝트 개요

### 프로젝트명
Avatarbank

### 서비스 정의
Avatarbank는 인플루언서의 외형(얼굴/체형)을 기반으로 학습된 AI 아바타를 활용해  
이미지를 생성하고, 생성 1회 단위로 수익이 발생·분배되는 AI 아바타 마켓플레이스이다.

- AI 모델 자체는 판매하지 않는다
- 모든 수익은 "이미지 생성" 행위에서만 발생한다
- 크레딧 기반 내부 경제 시스템을 사용한다

---

## 2. 사용자 역할 정의

### 2.1 Influencer (모델 제공자)
- 인스타그램 공개 계정 보유
- 팔로워 1,000명 이상
- 본인 사진 업로드 및 학습 동의
- 아바타가 사용될 때마다 크레딧 수익 획득
- 크레딧을 USD로 환전 가능

### 2.2 Buyer (구매자)
- 크레딧 구매 가능
- 아바타 선택 후 이미지 생성 가능
- 생성 옵션 크레딧 설정 가능
- 환전 불가

### 2.3 Admin
- 모델 승인 및 관리
- NSFW 설정 관리
- 정산 및 환전 승인
- AI 학습 파이프라인 관리

---

## 3. 핵심 정책 (절대 변경 금지)

1. 아바타 모델은 플랫폼 자산이다
2. Influencer만 환전 가능하다
3. Buyer는 크레딧을 벌 수 있으나 현금화 불가
4. 모든 생성은 Z IMAGE TURBO + ComfyUI로만 처리
5. 모든 이미지 생성은 서버 측에서만 수행

---

## 4. 기술 스택

### AI
- Z IMAGE TURBO
- ComfyUI
- LoRA 기반 개인 모델 학습

### Backend
- FastAPI
- Celery + Redis
- Webhook Listener

### Infra
- RunPods (A40 GPU)
- AWS EC2 (API Server)
- AWS S3 (이미지 저장)
- NeonDB (PostgreSQL)
- Redis (Queue)

---

## 5. 전체 아키텍처

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

---

## 6. 크레딧 시스템

### 6.1 크레딧 가치

- 구매: 5 Credit = 1 USD
- 환전: 10 Credit = 1 USD

플랫폼은 이 차익을 통해 수익을 확보한다.

---

### 6.2 이미지 생성 시 크레딧 흐름

#### 기본 규칙
- 기본 생성 비용: 1 Credit (플랫폼 수익)
- 추가 옵션 크레딧: Buyer가 설정

#### 예시
- Buyer가 옵션 크레딧 4 설정
- 총 소모: 5 Credit
  - 1 Credit → 플랫폼
  - 4 Credit → Influencer

---

## 7. 수익 분배 로직

- Influencer는 생성 시마다 Credit을 획득
- Buyer는 Credit을 획득할 수 있으나 환전 불가
- 플랫폼은:
  - 기본 생성 비용 Credit
  - 구매/환전 비율 차익
  - 미환전 Credit 잔액

---

## 8. 모델 등록 프로세스

1. Influencer 회원가입
2. 인스타그램 계정 인증
3. 사진 업로드
   - 정면
   - 좌/우
   - 전신
4. Admin 승인
5. LoRA 학습 실행
6. 샘플 이미지 생성
7. Influencer 승인
8. 공개 상태 전환

---

## 9. AI 학습 파이프라인

### 초기
- 로컬 PC에서 LoRA 학습
- 수동 업로드

### 향후
- 학습 자동화 가능 구조로 설계
- 모델 메타데이터 DB 관리

---

## 10. 이미지 생성 파이프라인

1. Buyer 프롬프트 입력
2. Backend에서 프롬프트 검증
3. Celery 작업 생성
4. RunPods Worker 실행
5. ComfyUI Workflow 실행
6. 이미지 생성
7. S3 업로드
8. DB 기록
9. 결과 반환

---

## 11. 결제 시스템 (PayPal 기준)

### 결제 방식
- PayPal Checkout
- 결제 완료 → Webhook 수신

### Webhook 처리
1. 결제 검증
2. Credit 지급
3. Transaction 기록

---

## 12. 환전 시스템

- Influencer만 신청 가능
- 최소 환전 Credit 설정
- Admin 승인 후 처리
- PayPal Payout 사용

---

## 13. DB 주요 테이블

### users
- id
- role (buyer / influencer / admin)
- credit_balance

### avatars
- id
- influencer_id
- lora_path
- status

### generations
- id
- avatar_id
- buyer_id
- credits_used
- created_at

### transactions
- id
- user_id
- type (purchase / generation / payout)
- amount

---

## 14. 보안 및 정책

- 모든 생성은 서버에서만 수행
- Prompt 로그 저장
- NSFW 옵션은 Influencer 설정 기준으로 제한
- Seed 값은 Buyer에게만 공개

---

## 15. 확장 고려 사항

- Video Generation
- Avatar Style Pack
- Subscription Credit
- Public Gallery

---

## 16. Cursor 명령 가이드

이 문서를 기준으로:
- DB Schema 생성
- FastAPI 서버 구현
- Celery Worker 구현
- PayPal Webhook 연동
- Credit 로직 정확히 구현

추측하지 말고, 문서에 명시된 내용만 사용하여 개발할 것.
