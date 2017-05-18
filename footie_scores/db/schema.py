import json
import logging
import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base

from footie_scores import db


logger = logging.getLogger(__name__)
Base = declarative_base()


class _JsonEncodedDict(sqla.TypeDecorator):
    impl = sqla.String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


# class FixtureEvents(Base):
#     __tablename__ = 'events'

#     id = sqla.Column(sqla.Integer, primary_key=True)
#     fixture_id = sqla.Column(sqla.String, sqla.ForeignKey('fixtures.id'))

#     fixture = relationship('Fixture', back_populates='events')

class Competition(Base):
    __tablename__ = 'competitions'

    id = sqla.Column(sqla.Integer, primary_key=True)
    api_id = sqla.Column(sqla.String)
    name = sqla.Column(sqla.String)
    region = sqla.Column(sqla.String)

    def __init__(self, api_id, name, region):
        self.api_id = api_id
        self.name = name
        self.region = region

    def dict_clone(self):
        return {
            'api_id': self.api_id,
            'name': self.name,
            'region': self.region
            }


class Fixture(Base):
    # TODO lineups, players, events can be stored as own table
    __tablename__ = 'fixtures'

    id = sqla.Column(sqla.Integer, primary_key=True)
    date = sqla.Column(sqla.String)
    time = sqla.Column(sqla.String)
    team_home = sqla.Column(sqla.String)
    team_away = sqla.Column(sqla.String)
    score = sqla.Column(sqla.String)
    competition_id = sqla.Column(sqla.String)
    match_id = sqla.Column(sqla.String)
    events = sqla.Column(_JsonEncodedDict)
    lineups = sqla.Column(_JsonEncodedDict)

    # events = relationship(
    #     'FixtureEvents',
    #     order_by=FixtureEvents.id,
    #     back_populates='fixture')

    def __init__(
            self, team_home, team_away, competition_id, match_id,
            score, date, time, lineups, events=None):

        self.team_home = team_home
        self.team_away = team_away
        self.competition_id = competition_id
        self.match_id = match_id
        self.score = score
        self.date = date
        self.time = time
        self.lineups = lineups
        if events:
            self.events = events

        self.date_format = db.date_format
        self.time_format = db.time_format

    def __repr__(self):
        return "<Fixture(%s vs %s on %s at %s)>" %(
            self.team_home, self.team_away, self.date, self.time)

    @property
    def non_orm_attrs(self):
        # TODO this is dodgy - assuming inherited attributes / sqla attributes will always start with _
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


def create_tables_if_not_present():
    if not db.engine.table_names() == ['fixtures', 'competitions']:
        Base.metadata.create_all(db.engine)


def clear_tables():
    Base.metadata.drop_all(db.engine)


def clear_table(table):
    table.__table__.drop(db.engine)
