"""
파일 스토리지 추상화 레이어

이 모듈은 다양한 스토리지 백엔드(S3, 로컬 파일 시스템 등)를 
통일된 인터페이스로 사용할 수 있게 해줍니다.

사용 예시:
    from app.storage import get_storage
    
    storage = get_storage()
    url = storage.upload_file(file_content, "image.jpg", "avatars/1")
"""
from .base import StorageBackend
from .factory import get_storage

__all__ = ["StorageBackend", "get_storage"]
