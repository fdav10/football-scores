import json
import logging
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TypeDecorator, ForeignKey

from footie_scores import db


logger = logging.getLogger(__name__)
Base = declarative_base()


class _JsonEncodedDict(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


# class FixtureEvents(Base):
#     __tablename__ = 'events'

#     id = Column(Integer, primary_key=True)
#     fixture_id = Column(String, ForeignKey('fixtures.id'))

#     fixture = relationship('Fixture', back_populates='events')


class Fixture(Base):
    # TODO lineups, players, events can be stored as own table
    __tablename__ = 'fixtures'

    id = Column(Integer, primary_key=True)
    date = Column(String)
    time = Column(String)
    team_home = Column(String)
    team_away = Column(String)
    score = Column(String)
    competition_id = Column(String)
    match_id = Column(String)
    events = Column(_JsonEncodedDict)

    # events = relationship(
    #     'FixtureEvents',
    #     order_by=FixtureEvents.id,
    #     back_populates='fixture')

    def __init__(
            self, team_home, team_away, competition_id, match_id,
            score, date, time, events=None):
        self.team_home = team_home
        self.team_away = team_away
        self.competition_id = competition_id
        self.match_id = match_id
        self.score = score
        self.date = date
        self.time = time
        if events:
            self.events = events

    def __repr__(self):
        return "<Fixture(team_home='%s', team_away='%s', score='%s', time='%s')" %(
            self.team_home, self.team_away, self.date, self.time)

    @property
    def properties(self):
        return self.__dict__

def create_tables_if_not_present():
    if not db.engine.table_names() == ['fixtures', ]:
        Base.metadata.create_all(db.engine)


def clear_tables():
    Base.metadata.drop_all(db.engine)
