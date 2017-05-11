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
        id_query = session.query(Fixture.match_id)
        already_in_db = bool(id_query.filter(Fixture.match_id == fixture.match_id).all())
        if not already_in_db:
            session.add(fixture)
            logger.info('%s added to db', fixture)
        else:
            logger.info('%s not added to db because it\'s already there', fixture)


def get_fixture_by_id(id_):
    with db.session_scope() as session:
        fixture = session.query(Fixture).filter_by(match_id=id_).one().properties
    return fixture


def get_fixture_details_by_id(id_):
    pass


def get_competition_fixtures_by_id(id_):
    with db.session_scope() as session:
        fixtures = [f.properties for f in session.query(Fixture).filter_by(competition_id=id_).all()]
    return fixtures


if __name__ == '__main__':
    pass

