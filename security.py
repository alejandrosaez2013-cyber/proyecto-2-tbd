from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from config import settings
from pwdlib import PasswordHash

# Este es el mismo archi entregado en clases.

pwd_context = PasswordHash.recommended()

def crear_hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password: str, hashed_password:str) -> bool:
    return pwd_context.verify(password, hashed_password)

def crear_access_token(data:dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy() 
    print(settings.SECRET_KEY)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else: 
        expire = datetime.now(timezone.utc) + timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTOS)
        
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORTHM)

def verificar_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORTHM])
        return payload
    except jwt.InvalidTokenError:
        return None
    