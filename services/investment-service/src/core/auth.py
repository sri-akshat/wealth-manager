# src/core/auth.py
from typing import Optional

from fastapi import HTTPException, Header
from jose import jwt, JWTError

from .config import settings


async def get_current_user_id(
        authorization: Optional[str] = Header(None, description="Bearer token")
) -> str:
    """
    Validate JWT token and extract user_id.
    Returns user_id if token is valid, raises 401 otherwise.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )