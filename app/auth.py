import os, time
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from .models import Token, User, TokenData
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_fake_hash = pwd_context.hash("changeme")
_DEMO = {"demo":{"username":"demo","hashed_password":_fake_hash,"disabled":False}}
SECRET_KEY = os.getenv("SECRET_KEY","dev-insecure-secret-change-me"); ALGO="HS256"; EXPIRE=43200
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
def verify(p, h): return pwd_context.verify(p, h)
def get_user(db, u:str)->Optional[User]:
    d=db.get(u); return User(username=d["username"], disabled=d.get("disabled",False)) if d else None
def authenticate_user(u,p):
    r=_DEMO.get(u); 
    return None if (not r or not verify(p,r["hashed_password"])) else User(username=u, disabled=r.get("disabled",False))
def create_token(data:dict, expires:Optional[int]=None):
    o=data.copy(); o.update({"exp": int(time.time()) + int(expires or EXPIRE)}); return jwt.encode(o, SECRET_KEY, algorithm=ALGO)
async def get_current_user(token:str=Depends(oauth2_scheme))->User:
    cred = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGO]); u=payload.get("sub"); 
        if u is None: raise cred
    except JWTError: raise cred
    user=get_user(_DEMO, u)
    if user is None or user.disabled: raise cred
    return user
async def issue_token(form_data: OAuth2PasswordRequestForm = Depends())->Token:
    u=authenticate_user(form_data.username, form_data.password)
    if not u: raise HTTPException(status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate":"Bearer"})
    return Token(access_token=create_token({"sub":u.username}))
