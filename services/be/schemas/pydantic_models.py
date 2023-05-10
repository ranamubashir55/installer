from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import timedelta


class AuthSettings(BaseModel):
    """Settings for Access Control using fastapi_jwt_auth"""
    authjwt_secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    authjwt_access_token_expires: int = 3600
    authjwt_refresh_token_expires: int = 3600
    redis_access_expires: int = timedelta(seconds=3600)
    redis_refresh_expires: int = timedelta(seconds=3600)
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}


class AccountTypeEnum(str, Enum):
    INDIVIDUAL = 'individual'
    ORGANIZATION = 'organization'


class UserCreate(BaseModel):
    name: str
    mobile: str
    company: str
    facility: str
    password: str
    email: EmailStr
    account_type: AccountTypeEnum


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPassword(BaseModel):
    token: str
    new_password: str
    confirm_new_password: str


class OptionCreate(BaseModel):
    question_id: int
    option_text: str