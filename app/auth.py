import os
from fastapi import Depends
from datetime import (
    datetime,
    timedelta,
    timezone
)

from jose import (
    JWTError,
    jwt
)

from passlib.context import (
    CryptContext
)

from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordBearer
)

# =====================================================
# JWT CONFIGURATION
# =====================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        60
    )
)

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "admin123"
)

# =====================================================
# PASSWORD HASHING
# =====================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# =====================================================
# HASH PASSWORD
# =====================================================

def hash_password(
    password: str
) -> str:

    return pwd_context.hash(password)

# =====================================================
# VERIFY PASSWORD
# =====================================================

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )

# =====================================================
# CREATE ACCESS TOKEN
# =====================================================

def create_access_token(
    data: dict
) -> str:

    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

# =====================================================
# OAUTH2 SCHEME
# =====================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

# =====================================================
# VERIFY CURRENT USER
# =====================================================

def get_current_user(
    token: str = Depends(
        oauth2_scheme
    )
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if not isinstance(
            username,
            str
        ):
            raise credentials_exception

        return username

    except JWTError:
        raise credentials_exception
    

def get_current_role(
    token: str = Depends(oauth2_scheme)
):
    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        role = payload.get("role")

        if role is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return role

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

def admin_required(
    role: str = Depends(get_current_role)
):

    if role != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return role


def manager_required(
    role: str = Depends(get_current_role)
):

    if role not in ["admin", "manager"]:

        raise HTTPException(
            status_code=403,
            detail="Manager access required"
        )

    return role


def viewer_required(
    role: str = Depends(get_current_role)
):

    if role not in [
        "admin",
        "manager",
        "viewer"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Viewer access required"
        )

    return role

