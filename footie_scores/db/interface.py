import logging

from sqlalchemy.ext.declarative import declarative_base

from footie_scores import db
from footie_scores import settings
from footie_scores.db.schema import Fixture, Competition


logger = logging.getLogger(__name__)
Base = declarative_base()


def row_exists(session, row_class, id_, value):
    session_query = session.query(row_class, id_)
    occurences = session_query.filter(id_==value).count()
    logger.info('%s occurences of %s with id %s', occurences, id_, value)
    return occurences > 0


def save_fixture_dicts_to_db(session, fixtures):
    for fixture in fixtures:
        save_fixture_dict_to_db(session, fixture)


def save_fixture_dict_to_db(session, fixture):
    fq = session.query(Fixture)
    cq = session.query(Competition)
    if not row_exists(session, Fixture, Fixture.match_id, fixture.match_id):
        fixture.competition = cq.filter(Competition.api_id.is_(fixture.comp_api_id)).one()
        session.add(fixture)
        logger.info('%s added to db', fixture.match_id)
    else:
        db_fixture = fq.filter(Fixture.match_id == fixture.match_id).first()
        db_fixture.update_from_equivalent(fixture)
        logger.info('%s updated in db', db_fixture)


def save_competitions_to_db(session, competitions):
    for comp in competitions:
        if not row_exists(session, Competition, Competition.api_id, comp['id']):
            db_comp = Competition(comp['id'], comp['name'], comp['region'])
            session.add(db_comp)


def get_competitions(session):
    comps = session.query(Competition).all()
    return comps


def get_fixture_by_id(session, id_):
    fixture = session.query(Fixture).filter_by(match_id=id_).one()
    return fixture


def get_fixtures_by_date(session, date_, comp_ids=settings.COMPS):
    cq = session.query(Competition)
    cfq = session.query(Fixture).join(Competition)
    fixtures_by_comp = []
    for id_ in comp_ids:
        competition = cq.filter(Competition.api_id == id_).one()
        fixtures = cfq.filter(Fixture.date==date_).filter(Competition.api_id==id_).all()
        fixtures_by_comp.append({'name': competition.name,
                                 'fixtures': fixtures,})
    return fixtures_by_comp
