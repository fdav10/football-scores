'''
Takes data returned by FootballAPICaller derived objects,
converts to db objects and adds them to the db.

Should be the single link between API and db.
'''

import logging

from footie_scores import db
from footie_scores.apis.football_api import FootballAPI
from footie_scores.db.schema import Fixture, Competition, Lineups
from footie_scores.db.queries import row_exists

logger = logging.getLogger(__name__)


def save_fixtures(session, api_fixtures):
    for fixture in api_fixtures:
        save_fixture(session, fixture)


def save_fixture(session, api_fixture):
    db_fixture = db.schema.Fixture(**api_fixture)
    fq = session.query(Fixture)
    cq = session.query(Competition)
    if not row_exists(session, Fixture, Fixture.api_fixture_id, db_fixture.api_fixture_id):
        db_fixture.competition = cq.filter(Competition.api_id == db_fixture.comp_api_id).one()
        session.add(db_fixture)
        logger.info('%s added to db', db_fixture)
    else:
        existing_db_fixture = fq.filter(Fixture.api_fixture_id == db_fixture.api_fixture_id).first()
        if existing_db_fixture.update_from_equivalent(db_fixture):
            logger.info('%s updated in db', db_fixture)


def save_lineups(session, api_lineups):
    fq = session.query(Fixture)
    for api_lineup in api_lineups:
        db_lineup = Lineups(**api_lineup)
        fixture = fq.filter(Fixture.api_fixture_id == db_lineup.api_fixture_id).one()
        if fixture.lineups is None:
            fixture.lineups = db_lineup
            logger.info('%s added to db', db_lineup.api_fixture_id)
        else:
            fixture.lineups.update_from_equivalent(db_lineup)
            logger.info('%s updated in db', fixture.lineups)


def save_competitions():
    api = FootballAPI()
    api_competitions = api.competitions_to_db()
    with db.session_scope() as session:
        for comp in api_competitions:
            if not row_exists(session, Competition, Competition.api_id, comp['api_id']):
                db_comp = Competition(**comp)
                session.add(db_comp)
