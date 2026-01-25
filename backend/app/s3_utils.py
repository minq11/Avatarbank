"""
S3 업로드 유틸리티
"""
import uuid
from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from .config import settings


def get_s3_client():
    """S3 클라이언트 생성"""
    client_config = {
        "service_name": "s3",
        "region_name": settings.AWS_REGION,
    }
    
    # AWS 자격 증명이 있으면 사용
    if hasattr(settings, "AWS_ACCESS_KEY_ID") and settings.AWS_ACCESS_KEY_ID:
        client_config["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
    if hasattr(settings, "AWS_SECRET_ACCESS_KEY") and settings.AWS_SECRET_ACCESS_KEY:
        client_config["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    
    return boto3.client(**client_config)


def upload_file_to_s3(
    file_content: BinaryIO,
    file_name: str,
    folder: str = "training",
    content_type: str = "image/jpeg",
) -> str:
    """
    파일을 S3에 업로드하고 URL 반환
    
    Args:
        file_content: 파일 내용 (BinaryIO)
        file_name: 원본 파일명
        folder: S3 폴더 경로 (예: "training", "avatars")
        content_type: 파일 MIME 타입
    
    Returns:
        S3 URL (https://...)
    """
    s3_client = get_s3_client()
    
    # 고유한 파일명 생성
    file_ext = Path(file_name).suffix or ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    s3_key = f"{folder}/{unique_filename}"
    
    try:
        # 파일을 처음으로 되돌림 (읽기 후 위치 초기화)
        file_content.seek(0)
        
        # S3에 업로드
        s3_client.upload_fileobj(
            file_content,
            settings.S3_BUCKET,
            s3_key,
            ExtraArgs={"ContentType": content_type},
        )
        
        # S3 URL 생성
        s3_url = f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        return s3_url
        
    except ClientError as e:
        raise Exception(f"Failed to upload file to S3: {str(e)}")


def upload_multiple_files_to_s3(
    files: list[BinaryIO],
    file_names: list[str],
    folder: str = "training",
    content_type: str = "image/jpeg",
) -> list[str]:
    """
    여러 파일을 S3에 업로드하고 URL 리스트 반환
    
    Args:
        files: 파일 내용 리스트
        file_names: 원본 파일명 리스트
        folder: S3 폴더 경로
        content_type: 파일 MIME 타입
    
    Returns:
        S3 URL 리스트
    """
    urls = []
    for file_content, file_name in zip(files, file_names):
        url = upload_file_to_s3(file_content, file_name, folder, content_type)
        urls.append(url)
    return urls
