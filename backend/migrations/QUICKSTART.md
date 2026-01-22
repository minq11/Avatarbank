# 빠른 시작 가이드

## 🚀 3단계로 시작하기

### 1단계: 환경 변수 설정

프로젝트 루트에 `.env` 파일 생성:

```env
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
```

### 2단계: 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

### 3단계: 테이블 생성

```bash
cd backend
python migrations/create_tables.py
```

**완료!** 🎉

## 📋 생성되는 테이블

- `users` - 사용자
- `avatars` - 아바타  
- `generations` - 이미지 생성 기록
- `tasks` - 작업 관리
- `transactions` - 트랜잭션
- `error_logs` - 에러 로그
- `payment_webhooks` - 결제 웹훅
- `training_jobs` - 학습 작업
- `audit_logs` - 감사 로그
- `shared_generations` - 공유 생성
- `likes` - 좋아요
- `bookmarks` - 북마크
- `payout_requests` - 환전 요청

## ❓ 문제가 생겼다면?

자세한 가이드는 [README.md](README.md)를 참고하세요.