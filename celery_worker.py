import asyncio
import collections
import os

from celery import Celery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import VoteModel, BestHeroesModel, PatchModel, VotingModel

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

celery.conf.update(
    # task_routes={
    #     'tasks.add': {'queue': 'hipri'},
    # },
    beat_schedule={
        'add-every-3-seconds': {
            'task': 'parse_best_heroes',
            'schedule': 3.0,
        },
    },
)
print(123123213)


@celery.task(name="parse_best_heroes")
# @periodic_task(run_every=(timedelta(seconds=5)), name='hello')
def parse_best_heroes():
    print("123123")
    session = get_session()
    asyncio.run(update_best_heroes_by_patch(session))
    session.commit()


async def update_best_heroes_by_patch(session: AsyncSession, patch) -> None:
    # patches = session.query(PatchModel.number).all()
    votings = session.query(VotingModel.number).all()
    # async for patch in patches:
    async for voting in votings:
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

    new_best_heroes = []
    for top, hero_score in enumerate(sorted(hero_score_dict.items(), key=lambda x: x[1]), start=1):
        hero, score = hero_score
        new_best_heroes.append(BestHeroesModel(top=top, hero=hero, patch=patch, voting=voting))

    session.query(BestHeroesModel).filter(BestHeroesModel.voting == voting, BestHeroesModel.patch == patch).delete()
    session.add_all(new_best_heroes)
