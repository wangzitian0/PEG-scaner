"""
Shared Auth Utilities

For Django: Use djangorestframework-simplejwt directly.
For FastAPI: Use verify_token() which is compatible with simplejwt tokens.

Usage (FastAPI):
    from libs.auth import verify_token
    
    payload = verify_token(token)
    if payload:
        user_id = payload.get('user_id')
"""

from .token_utils import verify_token, decode_token, get_user_id_from_token

__all__ = ['verify_token', 'decode_token', 'get_user_id_from_token']
