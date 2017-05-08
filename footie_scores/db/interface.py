import json
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TypeDecorator

from footie_scores import db


logger = logging.getLogger(__name__)
Base = declarative_base()


class ClassFromDict():
    def __init__(self, dict_arg):
        self._assign_to_self(dict_arg)

    def _assign_to_self(self, dict_):
        for key, value in dict_.items():
            if isinstance(value, dict):
                self._assign_to_self(value)
            elif isinstance(value, (list, tuple)):
                pass
            else:
                setattr(self, key, value)


class JsonEncodedDict(TypeDecorator):
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
    competition_id = Column(String)
    match_id = Column(String)
    api_source = Column(String)
    data = Column(JsonEncodedDict)

    def __init__(self, db_ready_fixture):
        for k, v in db_ready_fixture.items():
            setattr(self, k, v)

    def __repr__(self):
        return "<Fixture(team_home='%s', team_away='%s', score='%s', time='%s')" %(
            self.team_home, self.team_away, self.date, self.time)


def create_tables():
    if not db.engine.table_names() == ['fixtures', ]:
        Base.metadata.create_all(db.engine)


def save_fixture_dicts_to_db(fixtures):
    for fixture in fixtures:
        save_fixture_dict_to_db(fixture)


def save_fixture_dict_to_db(fixture):
    db_fixture = Fixture(fixture)
    with db.session_scope() as session:
        id_query = session.query(Fixture.match_id)
        if not id_query.filter(Fixture.match_id == fixture['match_id']).all():
            session.add(db_fixture)
            logger.info('%s added to db', db_fixture)
        else:
            logger.info('%s not added to db because it\'s already there', db_fixture)


def get_fixture_by_id(id_):
    with db.session_scope() as session:
        fixture = session.query(Fixture).filter_by(match_id=id_)
    return [f.data for f in fixture]


def get_competition_fixtures_by_id(id_):
    with db.session_scope() as session:
        fixtures = [f for f in session.query(Fixture).filter_by(competition_id=id_).all()]
        session.flush()
    return fixtures


if __name__ == '__main__':
    pass

