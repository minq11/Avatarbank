"""
FastAPI 의존성 함수들
인증, 권한 체크 등
"""

from typing import Optional

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .auth import verify_token
from .config import settings
from .db import get_db
from .models import User

security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """현재 로그인한 사용자 조회 (JWT Access Token 검증)"""
    token = credentials.credentials
    if token:
        logger.warning("Received access token length=%s", len(token))
    payload = verify_token(token, token_type="access")
    if payload is None:
        logger.warning("Access token verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning("User not found for token subject")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """현재 활성 사용자 조회 (별칭)"""
    return current_user


def require_role(required_role: str):
    """특정 역할이 필요한 의존성 팩토리"""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role}",
            )
        return current_user

    return role_checker
