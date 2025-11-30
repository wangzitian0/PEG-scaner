"""
FastAPI Dependencies

Verifies JWT tokens issued by Django (simplejwt).
"""

import sys
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, Request

# Ensure libs is in path
libs_path = Path(__file__).resolve().parent.parent.parent / 'libs'
if str(libs_path.parent) not in sys.path:
    sys.path.insert(0, str(libs_path.parent))

from libs.auth import verify_token, get_user_id_from_token


def get_token_from_request(request: Request) -> Optional[str]:
    """Extract Bearer token from request header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1]


def get_current_user_id(request: Request) -> Optional[int]:
    """
    Extract user ID from JWT token.
    
    Returns None if not authenticated.
    """
    token = get_token_from_request(request)
    if not token:
        return None
    return get_user_id_from_token(token)


def require_auth(request: Request) -> int:
    """
    Require valid authentication.
    
    Raises HTTPException if not authenticated.
    """
    user_id = get_current_user_id(request)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id
