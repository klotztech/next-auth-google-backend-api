from os import environ
from datetime import datetime, timedelta
from typing import Union
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from typing_extensions import Annotated
from dotenv import load_dotenv

from google.oauth2 import id_token
from google.auth.transport import requests

load_dotenv()
GOOGLE_CLIENT_ID = environ.get("GOOGLE_CLIENT_ID")

# to get a string like this run:
# openssl rand -hex 32
JWT_ISSUER = "fast-api.local"
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def main():
    return {"message": "Hello World"}
    
class TokenRequest(BaseModel):
    id_token: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str
    given_name: str
    family_name: str
    username: str
    email: str

jwt_bearer_scheme = HTTPBearer()

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(authorization: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Check token validity and issuer
        payload = jwt.decode(token=authorization.credentials, 
                             key=SECRET_KEY, 
                             algorithms=[ALGORITHM], 
                             issuer=[JWT_ISSUER])
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(
            user_id=user_id, 
            username=payload.get("name"),
            given_name=payload.get("given_name"),
            family_name=payload.get("family_name"),
            email=payload.get("email"),
        )
    except JWTError:
        raise credentials_exception
    # user = get_user(fake_users_db, username=token_data.username)
    # if user is None:
    #     raise credentials_exception
    return token_data


async def get_current_active_user(
    current_user: Annotated[TokenData, Depends(get_current_user)]
):
    # TODO: Make additional checks here if req
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token, 
          description="Retrieve API Access Token using Google id_token")
async def login_for_access_token(
    tokenReq: TokenRequest
):
    try:
        idinfo = id_token.verify_oauth2_token(tokenReq.id_token, requests.Request(), GOOGLE_CLIENT_ID)
        print(idinfo)

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        subject = idinfo['sub']
        email = idinfo['email']
        name = idinfo['name']
        given_name = idinfo['given_name']
        family_name = idinfo['family_name']
        
        # TODO: Verify that the ID token has an hd claim that matches your G Suite domain name.
        # domain = idinfo['hd']
         
        issued_at = idinfo["iat"]
        expires_at = idinfo["exp"]

        payload = {
            "iss": JWT_ISSUER,
            "sub": subject,
            "email": email,
            "name": name,
            "given_name": given_name,
            "family_name": family_name,
            "iat": issued_at,
            "exp": expires_at,
        }
        encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {"access_token": encoded_jwt, "token_type": "bearer"}

    except ValueError as e:
        raise HTTPException(status_code=403, detail=f"{e}")


@app.get("/me", response_model=TokenData)
async def read_users_me(
    current_user: Annotated[TokenData, Depends(get_current_active_user)]
):
    # Do something that only authenticated users can do
    return current_user