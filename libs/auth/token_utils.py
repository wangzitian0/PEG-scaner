"""
Token Utilities for FastAPI

Verifies JWT tokens issued by djangorestframework-simplejwt.
Compatible with SIMPLE_JWT settings in Django.
"""

from typing import Any, Dict, Optional

import jwt

from libs.config import settings


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT token.
    
    Compatible with djangorestframework-simplejwt tokens.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload dict, or None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify token and return payload.
    
    Alias for decode_token() for backward compatibility.
    """
    return decode_token(token)


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    Extract user ID from token.
    
    Args:
        token: JWT token string
    
    Returns:
        User ID or None
    """
    payload = decode_token(token)
    if not payload:
        return None
    
    # simplejwt uses 'user_id' claim by default
    user_id = payload.get('user_id')
    if user_id is not None:
        return int(user_id)
    return None

