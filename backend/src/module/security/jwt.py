from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt


def generate_key():
    import secrets

    return secrets.token_urlsafe(32)


app_pwd_key = generate_key()
app_pwd_algorithm = "HS256"


# 创建 JWT Token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, app_pwd_key, algorithm=app_pwd_algorithm)
    return encoded_jwt


# 解码 Token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, app_pwd_key, algorithms=[app_pwd_algorithm])
        username = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None


def verify_token(token: str):
    token_data = decode_token(token)
    if token_data is None:
        return None
    expires = token_data.get("exp")
    if datetime.utcnow() >= datetime.fromtimestamp(expires):
        raise JWTError("Token expired")
    return token_data


# 密码加密&验证
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
