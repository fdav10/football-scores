import logging

from sqlalchemy.ext.declarative import declarative_base

from footie_scores import db
from footie_scores.db.schema import Fixture


logger = logging.getLogger(__name__)
Base = declarative_base()


def save_fixture_dicts_to_db(fixtures):
    for fixture in fixtures:
        save_fixture_dict_to_db(fixture)


def save_fixture_dict_to_db(fixture):
    with db.session_scope() as session:
        fixture_query_by_id = session.query(Fixture, Fixture.match_id)
        db_fixture = fixture_query_by_id.filter(Fixture.match_id == fixture.match_id).one()[0]
        if not db_fixture:
            session.add(fixture)
            logger.info('%s added to db', fixture.match_id)
        else:
            for k, v in fixture.__dict__.items():
                setattr(db_fixture, k, v)
            logger.info('%s updated in db', db_fixture)



def get_fixture_by_id(id_):
    with db.session_scope() as session:
        fixture = session.query(Fixture).filter_by(match_id=id_).one().properties
    return fixture


def get_competition_fixtures_by_id(id_):
    with db.session_scope() as session:
        comp_fixtures = session.query(Fixture).filter_by(competition_id=id_).all()
        fixtures = [f.properties for f in comp_fixtures]
    return fixtures


if __name__ == '__main__':
    pass

