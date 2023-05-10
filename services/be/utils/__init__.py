from passlib.context import CryptContext

# For Storing Hashed Passwords in database
crypt_context = CryptContext(schemes=["sha256_crypt", "md5_crypt"])


def verify_password(plain_password, hashed_password):
    """Verify Password by matching plain and hashed passwords"""
    return crypt_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return crypt_context.hash(password)
