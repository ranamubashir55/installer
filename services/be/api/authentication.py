from redis import Redis
from fastapi import APIRouter, status, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from db.database import get_db
from schemas import pydantic_models as schemas
from utils.auth import (
    get_verify_user,
    is_valid_email,
    send_password_reset_email,
    is_valid_password_token,
    validate_change_password_token,
    validate_password,
    update_password,
)
import logging, jwt

log = logging.getLogger("omniroom-logger")
router = APIRouter()
settings = schemas.AuthSettings()


@AuthJWT.load_config
def get_config():
    """Callback to get configurations/settings for AuthJWT"""
    return settings


"""Setup our redis connection for storing the denylist tokens """
print("Connecting to rediss...")
redis_conn = Redis(host="redis", port=6379, decode_responses=True)
for key in redis_conn.scan_iter():
    print(key + " =")
    print(redis_conn.get(key))
    print(redis_conn.ttl(key))  # Number of seconds remaining to Expiry
    # r.delete(key)


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    """Create our function to check if a token has been revoked. In this simple
    case, we will just store the tokens jti (unique identifier) in redis.
    This function will return the revoked status of a token. If a token exists
    in redis and value is true, token has been revoked"""
    jti = decrypted_token["jti"]
    entry = redis_conn.get(jti)
    return entry and entry == "true"


"""Login outh2 authetication"""


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    user: schemas.UserLogin,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    user = get_verify_user(db, user.email, user.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user:
        new_access_token = Authorize.create_access_token(subject=user.email)
        new_refresh_token = Authorize.create_refresh_token(subject=user.email)
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "user_id": user.id,
        }


@router.post("/refreshToken", status_code=status.HTTP_200_OK)
def refresh_token(Authorize: AuthJWT = Depends()):
    """
    The jwt_refresh_token_required() function insures a valid refresh
    token is present in the request before running any code below that function.
    we can use the get_jwt_subject() function to get the subject of the refresh
    token, and use the create_access_token() function again to make a new access token
    """
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}


@router.delete("/logout", status_code=status.HTTP_200_OK)
def logout_and_revoke_tokens(refresh_token: str, Authorize: AuthJWT = Depends()):
    """Store both access and refresh tokens in redis with the value true for revoked.
    We also set an expires time on these tokens in redis,
    so they will get automatically removed after they expired."""
    Authorize.jwt_required()
    access_jti = Authorize.get_raw_jwt()["jti"]
    refresh_jti = Authorize.get_jti(refresh_token)
    redis_conn.setex(access_jti, settings.redis_access_expires, "true")
    redis_conn.setex(refresh_jti, settings.redis_refresh_expires, "true")
    return {"Result": "Tokens have been revoked"}


@router.post("/forgot_password", status_code=status.HTTP_200_OK)
def forgot_password(
    req: Request, email: str = Body(..., embed=True), db: Session = Depends(get_db)
):
    if is_valid_email(db, email):
        server_url = req.headers.get("origin")
        server_url = server_url.split(":")
        server_url = f"{server_url[0]}:{server_url[1]}:8080"
        token = send_password_reset_email(db, server_url, receiver_email=email)
        return {"token": token}
    raise HTTPException(status_code=400, detail="Invalid email")


@router.post("/change_password", status_code=status.HTTP_200_OK)
def change_password(user: schemas.ForgotPassword, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(user.token, settings.authjwt_secret_key)
        email = payload["sub"]
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not is_valid_email(db, email):
        raise HTTPException(status_code=400, detail="Invalid email")
    if not is_valid_password_token(db, token=user.token, email=email):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if validate_change_password_token(
        token=user.token, secret_key=settings.authjwt_secret_key
    ):
        if user.new_password != user.confirm_new_password:
            raise HTTPException(status_code=400, detail="Password mismatch")
        if not validate_password(password=user.new_password):
            raise HTTPException(
                status_code=400,
                detail="Password must contain at least 6 characters, including upper/lowercase, numbers, and special character",
            )
        if update_password(db, user, email=email):
            print("Successfully update the user password.")
            return {"message": "Password Updated for User"}
