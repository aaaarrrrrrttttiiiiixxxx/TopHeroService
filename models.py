from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from database import Base


class HeroModel(Base):
    __tablename__ = 'hero'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    photo_url = Column(String)


class PatchModel(Base):
    __tablename__ = 'patch'

    number = Column(String, primary_key=True)
    date = Column(DateTime)


class VotingModel(Base):
    __tablename__ = 'voting'

    name = Column(String, primary_key=True)
    order = Column(Integer, unique=True)


class VoteModel(Base):
    __tablename__ = 'vote'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    top_hero = Column(Integer, ForeignKey('hero.id'))
    top_2_hero = Column(Integer, ForeignKey('hero.id'))
    top_3_hero = Column(Integer, ForeignKey('hero.id'))
    patch = Column(String, ForeignKey('patch.number'))
    voting = Column(String, ForeignKey('voting.name'))


class VoteWithHeroesModel(VoteModel):
    top_hero_model = relationship('HeroModel', lazy='joined', primaryjoin=VoteModel.top_hero == HeroModel.id)
    top_hero_2_model = relationship('HeroModel', lazy='joined', primaryjoin=VoteModel.top_2_hero == HeroModel.id)
    top_hero_3_model = relationship('HeroModel', lazy='joined', primaryjoin=VoteModel.top_3_hero == HeroModel.id)


class BestHeroesModel(Base):
    __tablename__ = 'best_horoes'

    id = Column(Integer, primary_key=True)
    top = Column(Integer)
    hero = Column(Integer, ForeignKey('hero.id'))
    patch = Column(String, ForeignKey('patch.number'))
    voting = Column(String, ForeignKey('voting.name'))

    __table_args__ = (
        # UniqueConstraint(('patch', 'voting'))
        Index('patch_voting_index', 'patch', 'voting', unique=True),
    )


class BestHeroesJoinedModel(BestHeroesModel):
    top_hero_model = relationship('HeroModel', lazy='joined', primaryjoin=BestHeroesModel.hero == HeroModel.id)
