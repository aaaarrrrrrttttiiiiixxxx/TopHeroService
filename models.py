from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from database import Base
from enum import Enum


class HeroPositionsEnum(Enum):
    KERRY = 'KERRY'
    MIDLANER = 'MIDLANER'
    OFFLANER = 'OFFLANER'
    SEMI_SUPPORT = 'SEMI_SUPPORT'
    HARD_SUPPORT = 'HARD_SUPPORT'


class Hero(Base):
    __tablename__ = "hero"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    photo_url = Column(String)


class Patch(Base):
    __tablename__ = "patch"

    number = Column(String, primary_key=True)
    date = Column(DateTime)


class Voting(Base):
    __tablename__ = "voting"

    name = Column(String, primary_key=True)
    order = Column(Integer, unique=True)


class Vote(Base):
    __tablename__ = "vote"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    top_hero = Column(Integer, ForeignKey('hero.id'))
    top_2_hero = Column(Integer, ForeignKey('hero.id'))
    top_3_hero = Column(Integer, ForeignKey('hero.id'))
    patch = Column(String, ForeignKey('patch.number'))
    voting = Column(String, ForeignKey('voting.name'))
