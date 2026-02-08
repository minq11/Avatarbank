## AvatarBank Backend

FastAPI 백엔드. 프로젝트 루트에서 아래 명령 실행.

### 개발 (docker-compose.dev.yml)

```bash
docker-compose -f docker-compose.dev.yml up -d --build    # 시작
docker-compose -f docker-compose.dev.yml stop             # 중지
docker-compose -f docker-compose.dev.yml restart         # 재시작
docker-compose -f docker-compose.dev.yml down             # 중지 + 컨테이너 제거
```

- 백엔드: 8000, 프론트(Vite): 5173

### 운영 (docker-compose.prod.yml)

```bash
docker-compose -f docker-compose.prod.yml up -d --build   # 시작 (코드 반영 시에도 이걸로)
docker-compose -f docker-compose.prod.yml stop            # 중지
docker-compose -f docker-compose.prod.yml restart         # 재시작 (설정만 바뀐 경우)
docker-compose -f docker-compose.prod.yml down            # 중지 + 컨테이너 제거
```

- **코드 수정 후 반영**: `restart`는 안 됨. **`up -d --build`** 로 이미지 다시 빌드 후 올리기.
- 백엔드: 8000, 프론트: 80/443

### 기타

- 마이그레이션: `docker-compose -f docker-compose.prod.yml exec backend python migrations/create_tables.py` (필요 시)
- 상세: 프로젝트 루트 **DOCKER.md**
