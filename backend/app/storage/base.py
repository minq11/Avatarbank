"""
스토리지 백엔드 추상화 인터페이스

모든 스토리지 구현체는 이 인터페이스를 구현해야 합니다.
"""
from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageBackend(ABC):
    """
    스토리지 백엔드 추상 클래스
    
    모든 스토리지 구현체(S3, 로컬 파일 시스템 등)는 
    이 클래스를 상속받아 구현해야 합니다.
    """
    
    @abstractmethod
    def upload_file(
        self,
        file_content: BinaryIO,
        file_name: str,
        folder: str = "",
        content_type: str = "image/jpeg",
    ) -> str:
        """
        파일을 업로드하고 접근 가능한 URL을 반환합니다.
        
        Args:
            file_content: 파일 내용 (BinaryIO)
            file_name: 원본 파일명
            folder: 저장할 폴더 경로 (예: "avatars/1", "training-requests/5")
            content_type: 파일 MIME 타입
        
        Returns:
            파일에 접근 가능한 URL (예: "https://...", "/static/...")
        
        Raises:
            Exception: 업로드 실패 시
        """
        pass
    
    @abstractmethod
    def upload_multiple_files(
        self,
        files: list[BinaryIO],
        file_names: list[str],
        folder: str = "",
        content_type: str = "image/jpeg",
    ) -> list[str]:
        """
        여러 파일을 업로드하고 URL 리스트를 반환합니다.
        
        Args:
            files: 파일 내용 리스트
            file_names: 원본 파일명 리스트
            folder: 저장할 폴더 경로
            content_type: 파일 MIME 타입
        
        Returns:
            파일 URL 리스트
        
        Raises:
            Exception: 업로드 실패 시
        """
        pass
    
    @abstractmethod
    def delete_file(self, file_url: str) -> bool:
        """
        파일을 삭제합니다.
        
        Args:
            file_url: 삭제할 파일의 URL
        
        Returns:
            삭제 성공 여부
        
        Raises:
            Exception: 삭제 실패 시
        """
        pass
    
    @abstractmethod
    def file_exists(self, file_url: str) -> bool:
        """
        파일이 존재하는지 확인합니다.
        
        Args:
            file_url: 확인할 파일의 URL
        
        Returns:
            파일 존재 여부
        """
        pass
