import logging

from sqlalchemy.ext.declarative import declarative_base

from footie_scores import db
from footie_scores import settings
from footie_scores.db.schema import Fixture, Competition, Lineups


logger = logging.getLogger(__name__)
Base = declarative_base()


def row_exists(session, row_class, id_, value):
    session_query = session.query(row_class, id_)
    occurences = session_query.filter(id_==value).count()
    return occurences > 0


def save_fixtures_to_db(session, fixtures):
    for fixture in fixtures:
        save_fixture_to_db(session, fixture)


def save_fixture_to_db(session, fixture):
    fq = session.query(Fixture)
    cq = session.query(Competition)
    if not row_exists(session, Fixture, Fixture.api_fixture_id, fixture.api_fixture_id):
        fixture.competition = cq.filter(Competition.api_id.is_(fixture.comp_api_id)).one()
        session.add(fixture)
        logger.info('%s added to db', fixture.api_fixture_id)
    else:
        db_fixture = fq.filter(Fixture.api_fixture_id == fixture.api_fixture_id).first()
        db_fixture.update_from_equivalent(fixture)
        logger.info('%s updated in db', db_fixture)


def save_competitions_to_db(session, competitions):
    for comp in competitions:
        if not row_exists(session, Competition, Competition.api_id, comp['id']):
            db_comp = Competition(comp['id'], comp['name'], comp['region'])
            session.add(db_comp)


def save_lineups_to_db(session, lineups):
    fq = session.query(Fixture)
    lq = session.query(Lineups)
    for lineup in lineups:
        fixture = fq.filter(Fixture.api_fixture_id.is_(lineup.api_fixture_id)).one()
        if fixture.lineups is None:
            fixture.lineups = lineup
            logger.info('%s added to db', lineup.api_fixture_id)
        else:
            fixture.lineups.update_from_equivalent(lineup)
            logger.info('%s updated in db', fixture.lineups)


def get_competitions(session):
    comps = session.query(Competition).all()
    return comps


def get_fixture_by_id(session, id_):
    fixture = session.query(Fixture).filter_by(api_fixture_id=id_).one()
    return fixture


def get_lineups_by_id(session, id_):
    lineups = session.query(Lineups).filter_by(api_fixture_id=id_).one()
    return lineups


def get_fixtures_by_date(session, dt_date):
    date_ = dt_date.strftime(settings.DB_DATEFORMAT)
    fq = session.query(Fixture)
    fixtures = fq.filter(Fixture.date==date_).all()
    return fixtures


def get_comp_grouped_fixtures_for_date(session, dt_date, comp_ids=settings.COMPS):
    date_ = dt_date.strftime(settings.DB_DATEFORMAT)
    cq = session.query(Competition)
    cfq = session.query(Fixture).join(Competition)
    fixtures_by_comp = []
    for id_ in comp_ids:
        competition = cq.filter(Competition.api_id == id_).one()
        fixtures = cfq.filter(Fixture.date==date_).filter(Competition.api_id==id_).all()
        fixtures_by_comp.append({'name': competition.name,
                                 'fixtures': fixtures,})
    return fixtures_by_comp

def fixture_has_lineups(session, fixture_id):
    pass
