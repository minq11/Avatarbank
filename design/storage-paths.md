# 저장 경로 정리 (Storage Paths)

`.env`의 `STORAGE_TYPE`이 **`local`** 인지 **`s3`** 인지에 따라 파일이 저장·조회되는 위치가 달라집니다.

---

## 1. STORAGE_TYPE이 적용되는 기능

아래 기능들은 **STORAGE_TYPE** 값에 따라 **로컬** 또는 **S3**에 저장/조회됩니다.

| 기능 | API | Local 저장 경로 | S3 키(경로) | 비고 |
|------|-----|-----------------|-------------|------|
| **Training Request 생성** (preview + 훈련 사진) | `POST /my/training-requests` | `{UPLOAD_DIR}/training-requests/{request_id}/` | `training-requests/{request_id}/` | preview, front, side, fullbody, other 모두 동일 폴더 |
| **아바타 Preview Image 수정** | `PUT /my/avatars/{avatar_id}` | `{UPLOAD_DIR}/avatars/{avatar_id}/` | `avatars/{avatar_id}/` | My Avatars에서 미리보기 이미지 변경 시 |
| **Training Photos ZIP 다운로드** | `GET /admin/training-requests/{request_id}/photos.zip` | 위 `training-requests/{request_id}/` 에서 읽어서 ZIP | 위 S3 prefix에서 읽어서 ZIP | 저장소는 동일, 조회만 STORAGE_TYPE 따라감 |

- **Local일 때 URL**: `/static/{folder}/{파일명}` → 프론트에서는 `/api/static/...` 로 프록시 요청
- **S3일 때 URL**: `https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{키}`

---

## 2. 항상 S3만 사용하는 기능

아래는 **STORAGE_TYPE과 무관하게 항상 S3**에만 저장/조회합니다.

| 기능 | API | S3 키(경로) | 비고 |
|------|-----|-------------|------|
| **LoRA 파일 업로드** | `POST /admin/training-requests/{request_id}/upload-lora` | `loras/training_request_{request_id}/` | `.safetensors` 파일, DB `Avatar.lora_path`에 전체 S3 URL 저장 |
| **LoRA 파일 다운로드** | `GET /admin/training-requests/{request_id}/lora` | `Avatar.lora_path` (S3 URL) 기반 presigned URL 생성 | 로컬에는 LoRA 미저장 |

---

## 3. 경로 요약 표

| 저장 대상 | STORAGE_TYPE=local | STORAGE_TYPE=s3 |
|-----------|--------------------|------------------|
| Training Request용 이미지 (preview + 사진들) | `{UPLOAD_DIR}/training-requests/{id}/` | S3 `training-requests/{id}/` |
| 아바타 Preview Image (수정 시) | `{UPLOAD_DIR}/avatars/{avatar_id}/` | S3 `avatars/{avatar_id}/` |
| LoRA (.safetensors) | 사용 안 함 | S3 `loras/training_request_{id}/` |

---

## 4. 설정값 참고

- **UPLOAD_DIR** (로컬): 기본값 `"/app/uploads"`, 개발 시 `backend/uploads` 등으로 변경 가능. `.gitignore`에 `backend/uploads/` 포함 권장.
- **S3_BUCKET**, **AWS_REGION**: S3 사용 시 `.env`에서 설정.
- **정적 파일 서빙**: `STORAGE_TYPE=local`일 때만 FastAPI에서 `UPLOAD_DIR`를 `/static` 경로로 마운트합니다.
