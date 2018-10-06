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
    occurences = session_query.filter(id_ == value).count()
    return occurences > 0


def check_rows_in_db(session, row_type, row_key, match_keys):
    session_query = session.query(row_type)
    matches = session_query.filter(row_key.in_(match_keys)).all()
    return matches


def get_competitions(session):
    comps = session.query(Competition).all()
    return comps


def get_competitions_by_id(session, ids):
    comps = session.query(Competition).filter(Competition.api_id.in_(ids)).all()
    return comps


def get_competition_by_id(session, id_):
    comp = session.query(Competition).filter(Competition.api_id == id_).one()
    return comp


def count_fixtures_for_competition(session, comp_id):
    n_fixtures = session.query(Fixture).filter(Fixture.comp_api_id == comp_id).count()
    return n_fixtures


def get_fixture_by_id(session, id_):
    fixture = session.query(Fixture).filter_by(api_fixture_id=id_).one()
    return fixture


def get_lineups_by_id(session, id_):
    lineups = session.query(Lineups).filter_by(api_fixture_id=id_).one()
    return lineups


def get_fixtures_by_date(session, dt_date):
    fq = session.query(Fixture)
    fixtures = fq.filter(Fixture.date == dt_date)\
                 .order_by(Fixture.team_home).all()
    return fixtures


def get_fixtures_by_date_and_comp(
        session, start_date, comp_id, end_date=None):

    end_date = start_date if end_date is None else end_date
    cfq = session.query(Fixture).join(Competition)

    fixtures = cfq.filter(and_(start_date <= Fixture.date,
                               Fixture.date <= end_date))\
                  .filter(Competition.api_id == comp_id)\
                  .order_by(Fixture.team_home).all()

    return fixtures
