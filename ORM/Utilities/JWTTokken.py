"""
JWT token creation and verification.

Flow:
  1. User logs in → create_access_token() signs a JWT with the user's id as `sub`
  2. Protected routes depend on verify_access_token() to decode and validate the token

Token header format (custom header name, not Authorization):
  token: Bearer <jwt>
"""

import jwt
import os
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Header
from Models.databaseModel import User
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


def create_access_token(user: User) -> str:
    """Create a signed JWT for the given user. Expires in 30 minutes."""
    payload = {
        "sub": str(user.id),  # must be a string — PyJWT rejects integer subjects
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_access_token(token: str = Header(..., description="Bearer token")) -> dict:
    """
    FastAPI dependency — extracts and decodes the JWT from the `token` request header.

    Expects:  token: Bearer <jwt>
    Returns:  decoded payload dict (e.g. {"sub": "1", "exp": ...})

    Use as:   current_user: dict = Depends(verify_access_token)
    """
    try:
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        # Strip the "Bearer " prefix to get the raw JWT string
        token = token.split(" ")[1]
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
