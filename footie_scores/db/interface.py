import logging

from sqlalchemy.ext.declarative import declarative_base

from footie_scores import db
from footie_scores import settings
from footie_scores.db.schema import Fixture, Competition


logger = logging.getLogger(__name__)
Base = declarative_base()


def save_fixture_dicts_to_db(fixtures):
    for fixture in fixtures:
        save_fixture_dict_to_db(fixture)


def row_exists(row_class, id_, value):
    with db.session_scope() as session:
        session_query = session.query(row_class, id_)
        occurences = session_query.filter(id_==value).count()
        logger.info('%s occurences of %s with id %s', occurences, id_, value)
    return occurences > 1


def save_fixture_dict_to_db(fixture):
    with db.session_scope() as session:
        fixture_query_by_id = session.query(Fixture)
        db_fixture = fixture_query_by_id.filter(Fixture.match_id == fixture.match_id).first()
        if not db_fixture:
            session.add(fixture)
            logger.info('%s added to db', fixture.match_id)
        else:
            # TODO as noted in class definition non_orm_attrs method is unreliable
            for k, v in fixture.non_orm_attrs.items():
                setattr(db_fixture, k, v)
            logger.info('%s updated in db', db_fixture)


def save_competitions_to_db(competitions):
    for comp in competitions:
        with db.session_scope() as session:
            if not row_exists(Competition, Competition.api_id, comp['id']):
                db_comp = Competition(comp['id'], comp['name'], comp['region'])
                session.add(db_comp)

def get_competitions():
    with db.session_scope() as session:
        db_comps = session.query(Competition).all()
        comps = [dbc.dict_clone() for dbc in db_comps]
    return comps


def get_fixture_by_id(id_):
    with db.session_scope() as session:
        fixture = session.query(Fixture).filter_by(match_id=id_).one().non_orm_attrs
    return fixture


def get_fixtures_by_date(date_, comp_ids=settings.LIMITED_COMPS):
    with db.session_scope() as session:
        comp_fixtures = session.query(Fixture).filter(
            Fixture.competition_id.in_(comp_ids), Fixture.date.is_(date_)).all()
        fixtures = [f.non_orm_attrs for f in comp_fixtures]
    return fixtures


if __name__ == '__main__':
    pass

