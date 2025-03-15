# src/core/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# JWT configuration
SECRET_KEY = "test-secret-key-for-testing-only"  # Only for testing
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=True)

def create_test_token(email: str) -> str:
    """Create a test JWT token."""
    data = {
        "sub": email,
        "exp": int(datetime.now(timezone.utc).timestamp()) + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Get the current user ID from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if not token:
            raise credentials_exception
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # Convert email to a stable integer hash for user ID
        return abs(hash(email)) % (2**31)  # Ensure it's a positive 32-bit integer
    except JWTError:
        raise credentials_exception
    except Exception:
        raise credentials_exception