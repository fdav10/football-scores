import logging

from sqlalchemy import and_
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


def get_comp_grouped_fixtures_for_date(
        session, start_date, comp_ids=settings.COMPS, end_date=None):

    end_date = start_date if end_date is None else end_date
    cq = session.query(Competition)
    cfq = session.query(Fixture).join(Competition)
    fixtures_by_comp = []
    for id_ in comp_ids:
        competition = cq.filter(Competition.api_id == id_).one()

        fixtures = cfq.filter(and_(
            start_date <= Fixture.date,
            Fixture.date <= end_date)).filter(Competition.api_id==id_).all()

        fixtures_by_comp.append({'name': competition.name,
                                 'fixtures': fixtures,
                                 'api_id': id_,
                                 'display': True})
    return fixtures_by_comp
