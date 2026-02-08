"""
앱 업로드 공통 로직.
STORAGE_TYPE이 local일 때: 로컬에 저장(DB URL) + S3 백업은 백그라운드 스레드로 실행.
STORAGE_TYPE이 s3일 때: S3만 업로드.
"""
import logging
import threading
from io import BytesIO
from typing import BinaryIO

from .config import settings

logger = logging.getLogger(__name__)


def _s3_backup_single(
    content: bytes,
    file_name: str,
    folder: str,
    content_type: str,
) -> None:
    """백그라운드에서 S3 백업 업로드 (단일 파일)."""
    try:
        from .s3_utils import upload_file_to_s3

        upload_file_to_s3(
            BytesIO(content),
            file_name,
            folder=folder,
            content_type=content_type,
        )
    except Exception as e:
        logger.warning("S3 backup upload failed (folder=%s): %s", folder, e)


def _s3_backup_multiple(
    contents: list[bytes],
    file_names: list[str],
    folder: str,
    content_type: str,
) -> None:
    """백그라운드에서 S3 백업 업로드 (여러 파일)."""
    from .s3_utils import upload_file_to_s3

    for content, name in zip(contents, file_names):
        try:
            upload_file_to_s3(
                BytesIO(content),
                name,
                folder=folder,
                content_type=content_type,
            )
        except Exception as e:
            logger.warning("S3 backup upload failed (folder=%s): %s", folder, e)


def upload_file_for_app(
    file_content: BinaryIO,
    file_name: str,
    folder: str,
    content_type: str = "image/jpeg",
) -> str:
    """
    파일 업로드. DB에 저장할 URL을 반환.
    - local: 로컬 저장 후 S3 백업은 백그라운드 스레드로 실행 (응답 지연 없음).
    - s3: S3만 업로드.
    """
    if settings.STORAGE_TYPE == "local":
        from .local_storage import upload_file_to_local

        file_content.seek(0)
        content = file_content.read()
        url = upload_file_to_local(
            BytesIO(content),
            file_name,
            folder,
            content_type,
        )
        threading.Thread(
            target=_s3_backup_single,
            args=(content, file_name, folder, content_type),
            daemon=True,
        ).start()
        return url
    else:
        from .s3_utils import upload_file_to_s3

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
    """
    여러 파일 업로드. DB에 저장할 URL 목록 반환.
    local일 때 로컬 저장 후 S3 백업은 백그라운드 스레드로 실행.
    """
    if settings.STORAGE_TYPE == "local":
        from .local_storage import upload_multiple_files_to_local

        contents = [f.read() for f in files]
        urls = upload_multiple_files_to_local(
            [BytesIO(c) for c in contents],
            file_names,
            folder,
            content_type,
        )
        threading.Thread(
            target=_s3_backup_multiple,
            args=(contents, file_names, folder, content_type),
            daemon=True,
        ).start()
        return urls
    else:
        from .s3_utils import upload_multiple_files_to_s3

        return upload_multiple_files_to_s3(
            files,
            file_names,
            folder=folder,
            content_type=content_type,
        )
