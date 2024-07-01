from typing import Optional, List

from pydantic import BaseModel
from pydantic.v1 import validator


class Hero(BaseModel):
    name: str
    photo_url: str


class MakeVote(BaseModel):
    patch: str
    voting: str
    top_hero: Optional[int] = None
    top_2_hero: Optional[int] = None
    top_3_hero: Optional[int] = None


class VoteSchema(BaseModel):
    voting_name: str
    hero: Hero


class PatchListItem(BaseModel):
    patch_number: str
    top_heroes: List[VoteSchema]
    has_vote: bool


class UserVote(BaseModel):
    voting_name: str
    top_heroes: List[Hero]
