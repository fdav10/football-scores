import json
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TypeDecorator

from footie_scores import db


logger = logging.getLogger(__name__)
Base = declarative_base()


class _JsonEncodedDict(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


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

    def __init__(self, team_home, team_away, competition_id, match_id, score, date, time):
        self.team_home = team_home
        self.team_away = team_away
        self.competition_id = competition_id
        self.match_id = match_id
        self.score = score
        self.date = date
        self.time = time

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
