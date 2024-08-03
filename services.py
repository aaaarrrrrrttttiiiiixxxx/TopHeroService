import collections
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from models import VoteModel, HeroModel, VoteWithHeroesModel
from schemas import MakeVote, UserVote


class Service:
    async def make_vote(self, session: AsyncSession, data: MakeVote, user_id: int) -> None:
        try:
            result = await session.execute(select(VoteModel).filter(VoteModel.user_id == user_id,
                                                                    VoteModel.patch == data.patch,
                                                                    VoteModel.voting == data.voting))
            existing_vote = result.one()[0]
            if not self.check_same_hero([data.top_hero or existing_vote.top_hero,
                                         data.top_2_hero or existing_vote.top_2_hero,
                                         data.top_3_hero or existing_vote.top_3_hero]):
                raise HTTPException(status_code=400, detail="All heroes should be different.")
            existing_vote.top_hero = data.top_hero
            existing_vote.top_2_hero = data.top_2_hero
            existing_vote.top_3_hero = data.top_3_hero
        except NoResultFound:
            new_vote = VoteModel(**data.dict(), user_id=user_id)
            session.add(new_vote)
        await session.commit()

    def check_same_hero(self, hero_ids: List[Optional[int]]) -> bool:
        hero_ids = list(filter(lambda hero: hero is not None, hero_ids))
        return len(hero_ids) == len(set(hero_ids))

    async def user_votes(self, session: AsyncSession, patch_name: str, user_id: int):
        votes = await session.execute(select(VoteWithHeroesModel)
                                      .filter(VoteWithHeroesModel.user_id == user_id,
                                              VoteWithHeroesModel.patch == patch_name))
        res = []
        for vote in votes.scalars().all():
            res.append({'voting': vote.voting,
                        'top_heroes': filter(lambda h: h is not None,
                                             [vote.top_hero_model, vote.top_hero_2_model, vote.top_hero_3_model])})
        return res

    async def get_patch_list(self, session: AsyncSession, user_id):
        pass

    async def tops_by_patch(self, session: AsyncSession, patch):
        pass
