from datetime import timedelta
from typing import Literal, Optional
from fastapi import Depends, APIRouter, HTTPException, Response, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
from src.db.users import AnonymousUser, UserRead
from src.core.events.database import get_db_session
from config.config import get_learnhouse_config
from src.security.auth import authenticate_user, get_current_user, security
from src.services.auth.utils import signWithGoogle


router = APIRouter()


@router.get("/refresh")
def refresh(response: Response, payload: dict = Depends(security.refresh_token_required)):
    """
    The jwt_refresh_token_required() function insures a valid refresh
    token is present in the request before running any code below that function.
    we can use the get_jwt_subject() function to get the subject of the refresh
    token, and use the create_access_token() function again to make a new access token
    """
    current_user = payload.sub
    new_access_token = security.create_access_token(uid=current_user)

    # set cookies using AuthX
    security.set_access_cookies(new_access_token, response)
    
    return {"access_token": new_access_token}


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: Session = Depends(get_db_session),
):
    user = await authenticate_user(
        request, form_data.username, form_data.password, db_session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(uid=form_data.username)
    refresh_token = security.create_refresh_token(uid=form_data.username)
    
    # set cookies using AuthX
    security.set_access_cookies(access_token, response)
    security.set_refresh_cookies(refresh_token, response)

    user = UserRead.model_validate(user)

    result = {
        "user": user,
        "tokens": {"access_token": access_token, "refresh_token": refresh_token},
    }
    return result


class ThirdPartyLogin(BaseModel):
    email: EmailStr
    provider: Literal["google"]
    access_token: str


@router.post("/oauth")
async def third_party_login(
    request: Request,
    response: Response,
    body: ThirdPartyLogin,
    org_id: Optional[int] = None,
    current_user: AnonymousUser = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    # Google
    if body.provider == "google":

        user = await signWithGoogle(
            request, body.access_token, body.email, org_id, current_user, db_session
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(uid=user.email)
    refresh_token = security.create_refresh_token(uid=user.email)
    
    security.set_access_cookies(access_token, response)
    security.set_refresh_cookies(refresh_token, response)

    user = UserRead.model_validate(user)

    result = {
        "user": user,
        "tokens": {"access_token": access_token, "refresh_token": refresh_token},
    }
    return result


@router.delete("/logout")
def logout(response: Response, dependencies=Depends(security.access_token_required)):
    """
    Because the JWT are stored in an httponly cookie now, we cannot
    log the user out by simply deleting the cookies in the frontend.
    We need the backend to send us a response to delete the cookies.
    """
    security.unset_access_cookies(response)
    security.unset_refresh_cookies(response)
    return {"msg": "Successfully logout"}
