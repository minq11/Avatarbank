"""
로컬 파일 스토리지 유틸리티

서버의 로컬 디스크에 파일을 저장합니다.
로컬 테스트 환경에서 빠른 업로드 속도를 위해 사용합니다.
"""
import uuid
import os
from pathlib import Path
from typing import BinaryIO

from .config import settings


def get_upload_dir() -> Path:
    """업로드 디렉토리 경로 반환"""
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def upload_file_to_local(
    file_content: BinaryIO,
    file_name: str,
    folder: str = "training",
    content_type: str = "image/jpeg",
) -> str:
    """
    파일을 로컬 디스크에 저장하고 URL 반환
    
    Args:
        file_content: 파일 내용 (BinaryIO)
        file_name: 원본 파일명
        folder: 저장할 폴더 경로 (예: "training-requests/1", "avatars/1")
        content_type: 파일 MIME 타입
    
    Returns:
        파일 URL (예: "/static/training-requests/1/preview.jpg")
    """
    upload_dir = get_upload_dir()
    
    # 고유한 파일명 생성
    file_ext = Path(file_name).suffix or ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # 전체 경로 생성
    folder_path = upload_dir / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    
    file_path = folder_path / unique_filename
    
    try:
        # 파일을 처음으로 되돌림 (읽기 후 위치 초기화)
        file_content.seek(0)
        
        # 파일 저장
        with open(file_path, "wb") as f:
            f.write(file_content.read())
        
        # URL 생성 (정적 파일 서빙 경로)
        # 예: /static/training-requests/1/preview.jpg
        static_url = f"/static/{folder}/{unique_filename}"
        return static_url
        
    except Exception as e:
        raise Exception(f"Failed to upload file to local storage: {str(e)}")


def upload_multiple_files_to_local(
    files: list[BinaryIO],
    file_names: list[str],
    folder: str = "training",
    content_type: str = "image/jpeg",
) -> list[str]:
    """
    여러 파일을 로컬 디스크에 저장하고 URL 리스트 반환
    
    Args:
        files: 파일 내용 리스트
        file_names: 원본 파일명 리스트
        folder: 저장할 폴더 경로
        content_type: 파일 MIME 타입
    
    Returns:
        파일 URL 리스트
    """
    urls = []
    for file_content, file_name in zip(files, file_names):
        url = upload_file_to_local(file_content, file_name, folder, content_type)
        urls.append(url)
    return urls
