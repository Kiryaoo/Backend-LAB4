from datetime import datetime, timedelta
from typing import Optional

import jwt
from jwt import PyJWTError
from passlib.hash import pbkdf2_sha256

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import jwt as _jwt_lib


# Custom exceptions for FastAPI exception handlers
class JWTExpiredError(Exception):
    pass


class JWTInvalidError(Exception):
    pass


class JWTMissingError(Exception):
    pass
from fastapi import Request, HTTPException, status, Depends
from database import get_db
from sqlalchemy.orm import Session
from db_models import UserORM


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return pbkdf2_sha256.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except _jwt_lib.ExpiredSignatureError:
        # token expired
        raise JWTExpiredError()
    except (_jwt_lib.InvalidSignatureError, _jwt_lib.DecodeError, PyJWTError):
        # invalid token / signature verification failed
        raise JWTInvalidError()


def jwt_required(request: Request, db: Session = Depends(get_db)) -> UserORM:
    """FastAPI dependency that validates a Bearer JWT and returns the authenticated UserORM.

    Usage in endpoints: current_user: UserORM = Depends(jwt_required)
    """
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        # signal missing token to be handled by centralized handler
        raise JWTMissingError()
    token = auth_header.split()[1]
    payload = decode_access_token(token)
    # decode_access_token will raise JWTExpiredError or JWTInvalidError on problems
    user_id = payload.get("sub")
    if not user_id:
        raise JWTInvalidError()
    user = db.query(UserORM).filter(UserORM.id == int(user_id)).first()
    if not user:
        raise JWTInvalidError()
    return user
