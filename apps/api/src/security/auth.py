from sqlmodel import Session
from src.core.events.database import get_db_session
from src.db.users import AnonymousUser, PublicUser, User, UserRead
from src.services.users.users import security_get_user
from config.config import get_learnhouse_config
from pydantic import BaseModel
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from src.services.dev.dev import isDevModeEnabled
from src.services.users.users import security_verify_password
from src.security.security import ALGORITHM, SECRET_KEY
from authx import AuthX, AuthXConfig
from src.security.security import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


#### JWT Auth ####################################################
config = AuthXConfig()
config.JWT_SECRET_KEY = "secret" if isDevModeEnabled() else SECRET_KEY
config.JWT_TOKEN_LOCATION = ["cookies", "headers"]
config.JWT_COOKIE_CSRF_PROTECT = False
config.JWT_ACCESS_TOKEN_EXPIRES = (
    timedelta(days=365) if isDevModeEnabled() else timedelta(hours=8)
)
config.JWT_COOKIE_SAMESITE = "lax"
config.JWT_COOKIE_SECURE = True
config.JWT_COOKIE_DOMAIN = get_learnhouse_config().hosting_config.cookie_config.domain

security = AuthX(config=config)


#### JWT Auth ####################################################


#### Classes ####################################################


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


#### Classes ####################################################
async def authenticate_user(
    request: Request,
    email: str,
    password: str,
    db_session: Session,
) -> User | bool:
    user = await security_get_user(request, db_session, email)
    if not user:
        return False
    if not security_verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    # Using AuthX to create token
    # data usually contains "sub"
    uid = data.get("sub")
    if not uid:
         # Fallback if data doesn't have sub but has other things, 
         # but typically we pass sub.
         # For now, let's assume we pass sub in data or keep old manual logic if strict control needed.
         # But AuthX handles signing.
         pass
    
    # Since AuthX simplifies this, we might want to use security.create_access_token(uid=uid)
    # But checking if we need compatibility with old signature.
    # The old one took data dict.
    
    # Let's wrap standard jwt encode if we want to keep exact same signature without AuthX dependency here
    # OR better, use security.create_access_token
    # security.create_access_token(uid=...)
    
    if "sub" in data:
        return security.create_access_token(uid=data["sub"], fresh=True, headers=data, expires_delta=expires_delta)
    else:
        # If no sub, maybe this function is used generically? 
        # But old code did jwt.encode(to_encode, ...)
        # Let's reimplement similar logic using security properties if possible, or just use existing security instance.
        
        # ACTUALLY, checking imports, we have 'jwt' from 'jose'.
        # We can keep this function AS IS if we just want manual token creation, 
        # BUT we changed config to use AuthXConfig.
        # So we should probably use security.create_access_token to be consistent with config.
        pass
    
    # If we keep manual:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # Use the config from security if accessible, or global variables
    # We imported SECRET_KEY and ALGORITHM.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    request: Request,
    db_session: Session = Depends(get_db_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = None
    try:
        token = await security.get_access_token_from_request(request)
        if token:
            payload = security.verify_token(token)
            username = payload.sub
        else:
            print("DEBUG: No token extracted from request")
    except Exception as e:
        print(f"DEBUG: Token verification failed: {e}")
        pass

    if username:
        print(f"DEBUG: Token payload sub: {username}")
        user = await security_get_user(request, db_session, email=username)
        if user is None:
            print("DEBUG: User not found in DB for token")
            # Token valid but user validation failed (e.g. invalid sub or DB error)
            # Should we raise 401? Yes.
            raise credentials_exception
        print(f"DEBUG: Found user {user.username}, {user.user_uuid}")
        return PublicUser(**user.model_dump())
    else:
        print("DEBUG: No username in token or no token")
        return AnonymousUser()


async def non_public_endpoint(current_user: UserRead | AnonymousUser):
    if isinstance(current_user, AnonymousUser):
        raise HTTPException(status_code=401, detail="Not authenticated")
