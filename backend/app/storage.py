"""
앱 업로드: S3 전용.
"""
from typing import BinaryIO

from .s3_utils import upload_file_to_s3, upload_multiple_files_to_s3


def upload_file_for_app(
    file_content: BinaryIO,
    file_name: str,
    folder: str,
    content_type: str = "image/jpeg",
) -> str:
    """파일을 S3에 업로드하고 URL 반환."""
    return upload_file_to_s3(
        file_content,
        file_name,
        folder=folder,
        content_type=content_type,
    )


def upload_multiple_files_for_app(
    files: list[BinaryIO],
    file_names: list[str],
    folder: str,
    content_type: str = "image/jpeg",
) -> list[str]:
    """여러 파일을 S3에 업로드하고 URL 목록 반환."""
    return upload_multiple_files_to_s3(
        files,
        file_names,
        folder=folder,
        content_type=content_type,
    )
