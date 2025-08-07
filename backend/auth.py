import jwt
from datetime import datetime, timedelta
import os
from fastapi import HTTPException
import bcrypt

# Secret key for encoding/decoding tokens; use a secure secret in production
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(weeks=1)):
    """
    Create a JWT token with a default expiration of 1 week.
    
    IMPORTANT: The data dictionary must include a 'username' key.
    If the caller did not provide it, we raise an error so that the token payload
    is always complete.
    """
    if "username" not in data:
        raise ValueError("Token payload must include the 'username' key")
      
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """
    Decode a JWT token. Raises an exception if expired or invalid.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_token(token: str):
    """
    Verify the JWT token using decode_access_token.
    If the token is invalid, decode_access_token will raise an HTTPException.
    """
    return decode_access_token(token)


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))