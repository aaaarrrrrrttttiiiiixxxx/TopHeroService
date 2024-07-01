from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from database import engine
from models import Vote
from schemas import MakeVote


class Service:
    async def make_vote(self, data: MakeVote, user_id: int) -> None:
        with Session(engine) as session:
            try:
                existing_vote = session.query(Vote).filter(Vote.user_id == user_id,
                                                           Vote.patch == data.patch,
                                                           Vote.voting == data.voting).one()
                if not self.check_same_hero([data.top_hero or existing_vote.top_hero,
                                             data.top_2_hero or existing_vote.top_2_hero,
                                             data.top_3_hero or existing_vote.top_3_hero]):
                    raise HTTPException(status_code=400, detail="All heroes should be different.")
                existing_vote.top_hero = data.top_hero
                existing_vote.top_2_hero = data.top_2_hero
                existing_vote.top_3_hero = data.top_3_hero
            except NoResultFound:
                new_vote = Vote(**data.dict(), user_id=user_id)
                session.add(new_vote)
            session.commit()

    def check_same_hero(self, hero_ids: List[Optional[int]]) -> bool:
        hero_ids = list(filter(lambda hero: hero is not None, hero_ids))
        return len(hero_ids) == len(set(hero_ids))
