from datetime import datetime, timezone
from datetime import timedelta
from typing import Annotated, Optional
from typing import List

import jwt
from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security import APIKeyCookie
from jwt import InvalidTokenError
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from database import generate_async_session, get_session
from models import BestHeroesModel
from schemas import PatchListItem, MakeVote, UserVote
from services import Service

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
DEBUG = True

app = FastAPI()

x_token_header = APIKeyCookie(name="anything-cookie", auto_error=False)

if DEBUG:
    class Token(BaseModel):
        access_token: str
        token_type: str


    def create_access_token(data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt


    @app.post("/token/", response_model=Token)
    async def token_for_debug(user_id: int) -> Token:
        access_token = create_access_token(
            data={"user_id": user_id},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=access_token, token_type="bearer")


async def get_current_user_id(token: Optional[str] = Security(x_token_header)):
    try:
        token_type, token = token.split()
        if token_type != "Bearer":
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
    except (InvalidTokenError, ValidationError, ValueError, AttributeError):
        return None
    return user_id


async def get_current_user_id_auto_error(user_id: Optional[int] = Depends(get_current_user_id)):
    if user_id is None:
        raise HTTPException(status_code=401)
    return user_id


@app.get("/patch_list/", response_model=List[PatchListItem])
async def get_patch_list(user_id: Annotated[int, Depends(get_current_user_id)],
                         session: AsyncSession = Depends(generate_async_session)):
    service = Service()
    return await service.get_patch_list(session, user_id)


@app.post("/make_vote/")
async def make_vote(data: MakeVote,
                    user_id: Annotated[int, Depends(get_current_user_id_auto_error)],
                    session: AsyncSession = Depends(generate_async_session)):
    service = Service()
    await service.make_vote(data=data, user_id=user_id, session=session)
    return {}


@app.get("/user_votes/", response_model=List[UserVote])
async def user_votes(patch_name: str,
                     user_id: Annotated[int, Depends(get_current_user_id_auto_error)],
                     session: AsyncSession = Depends(generate_async_session)):
    service = Service()
    return await service.user_votes(patch_name=patch_name, user_id=user_id, session=session)


@app.get("/tops_by_patch/", response_model=List[UserVote])
async def tops_by_patch(patch_name: str, session: AsyncSession = Depends(generate_async_session)):
    service = Service()
    return await service.get_patch_list(session, patch_name)


@app.get("/test/")
async def test():
    session = next(get_session())
    session.add(BestHeroesModel(top=1, hero=1, patch='7.36b', voting='KERRY'))
    session.commit()
    return {}
