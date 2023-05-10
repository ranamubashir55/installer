from passlib.context import CryptContext
from db import crud
from fastapi import HTTPException, Depends
from fastapi_jwt_auth.exceptions import JWTDecodeError
import re, os, ssl, jwt
from fastapi_jwt_auth import AuthJWT
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import codecs
import smtplib

# For Storing Hashed Passwords in database
crypt_context = CryptContext(schemes=["sha256_crypt", "md5_crypt"])


def authenticate(Authorize: AuthJWT = Depends()):
    """Dependency for API endpoints to Authroize access_token and return current user"""
    try:
        Authorize.jwt_required()
    except JWTDecodeError as e:
        raise HTTPException(status_code=401, detail="Token is expired")
    current_user = Authorize.get_jwt_subject()
    return current_user


def verify_password(plain_password, hashed_password):
    """Verify Password by matching plain and hashed passwords"""
    return crypt_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return crypt_context.hash(password)


def get_verify_user(db_session, email, password):
    user = crud.get_user_by_email(db_session, email)
    if user:
        password_match = verify_password(password, user.password)
        if password_match:
            return user
        else:
            return None
    else:
        return None


def is_valid_email(db_session, email: str):
    """Validate user email"""
    regex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    user = crud.get_user_by_email(db_session, email)
    if (re.search(regex, email)) and user:
        return True
    else:
        return False


def validate_password(password):
    r_p = re.compile(
        r"^(?=\S{6,20}$)(?=.*?\d)(?=.*?[a-z])" r"(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])"
    )
    if r_p.match(password):
        return True
    return False


def is_valid_password_token(db_session, token: str, email: str):
    """Validate change password token"""
    user = crud.get_user_by_email(db_session, email)
    if user and str(user.password_change_token) == str(token):
        return True
    return False


def validate_change_password_token(token: str, secret_key):
    """Decode change password token"""
    try:
        payload = jwt.decode(token, secret_key)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        print(f"Token is valid")
        return True
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")


def update_password(db_session, user, email):
    """Update user password with new hashed password"""
    try:
        hash_password = get_password_hash(user.new_password)
        crud.change_password(db_session, email, hash_password)
        # again set the password_change_token to Null
        crud.set_password_change_token(db_session, email, None)
        return True
    except Exception:
        raise HTTPException(status_code=400, detail="Bad request")


def send_password_reset_email(db_session, server_url, receiver_email: str):
    """Send email to user for password reset link"""
    port = os.getenv('SMTP_PORT', default=465)
    smtp_server = str(os.getenv('SMTP_SERVER', default="smtp.gmail.com"))
    sender_email = str(os.getenv('SENDER_EMAIL', default="noreply@darvis.com"))
    password = str(os.getenv('SENDER_PASSWORD', default="xehjrdnjemrwxxfi"))
    token = AuthJWT().create_access_token(subject=receiver_email)
    message = MIMEMultipart("alternative")
    message["Subject"] = "Change password"
    message["From"] = sender_email
    message["To"] = receiver_email
    html = codecs.open("template/email.html", "r", "utf-8").read() % (server_url, token)
    # Create the plain-text and HTML version of message
    # Turn these into plain/html MIMEText objects
    mimetext = MIMEText(html, "html")
    message.attach(mimetext)
    crud.set_password_change_token(db_session, receiver_email, token)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    return token
