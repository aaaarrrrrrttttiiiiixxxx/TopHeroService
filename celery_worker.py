import asyncio
import collections
import os

from celery import Celery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import generate_async_session, get_async_session
from models import VoteModel, BestHeroesModel, PatchModel, VotingModel, HeroModel

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

celery.autodiscover_tasks()

celery.conf.beat_schedule = {
    'parse_best_heroes_last_patch': {
        'task': 'parse_best_heroes_last_patch',
        'schedule': 10.0
    },
    'parse_best_heroes_prev_patch': {
        'task': f'parse_best_heroes_prev_patch',
        'schedule': 30.0
    }
}


@celery.task
def parse_best_heroes_last_patch():
    asyncio.run(update_best_heroes_last_patch())


@celery.task
def parse_best_heroes_prev_patch():
    asyncio.run(update_best_heroes_prev_patch())


async def update_best_heroes_last_patch():
    session = await get_async_session()
    query = await session.execute(select(PatchModel.number).order_by(PatchModel.date))
    patch = query.scalars().one()
    await update_best_heroes_by_patch(session, patch)
    await session.commit()


async def update_best_heroes_prev_patch():
    session = generate_async_session()
    query = await session.execute(select(PatchModel.number).order_by(PatchModel.date).offset(1))
    patch = query.scalars().one()
    await update_best_heroes_by_patch(session, patch)
    await session.commit()


async def update_best_heroes_by_patch(session: AsyncSession, patch) -> None:
    query = await session.execute(select(VotingModel.name))
    votings = query.scalars().all()
    for voting in votings:
        await update_best_heroes(session, patch, voting)


async def update_best_heroes(session: AsyncSession, patch, voting) -> None:
    votes = await session.execute(select(VoteModel)
                                  .filter(VoteModel.voting == voting,
                                          VoteModel.patch == patch))
    hero_score_dict = collections.defaultdict(int)
    for vote in votes.scalars().all():
        hero_score_dict[vote.top_hero] += 3
        hero_score_dict[vote.top_2_hero] += 2
        hero_score_dict[vote.top_3_hero] += 1
    del hero_score_dict[None]
    new_best_heroes = []
    for top, hero_score in enumerate(sorted(hero_score_dict.items(), key=lambda x: x[1]), start=1):
        hero, score = hero_score
        new_best_heroes.append(BestHeroesModel(top=top, hero=hero, patch=patch, voting=voting))
    await add_zero_votes_heroes(session, [h.hero for h in new_best_heroes], patch, voting)

    await session.execute(
        BestHeroesModel.__table__.delete().where(BestHeroesModel.voting == voting, BestHeroesModel.patch == patch))
    session.add_all(new_best_heroes)


async def add_zero_votes_heroes(session: AsyncSession, existing_heroes: list[int], patch, voting) -> None:
    query = await session.execute(select(HeroModel.id).filter(HeroModel.id.not_in(existing_heroes)))
    ids = query.scalars().all()
    existing_heroes = set(existing_heroes)
    new_best_heroes = []
    for top, hero_id in enumerate(ids, start=len(existing_heroes)):
        new_best_heroes.append(BestHeroesModel(top=top, hero=hero_id, patch=patch, voting=voting))
    session.add_all(new_best_heroes)
