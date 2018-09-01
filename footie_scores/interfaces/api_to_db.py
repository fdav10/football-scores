'''
Takes data returned by FootballAPICaller derived objects,
converts to db objects and adds them to the db.

Should be the single link between API and db.
'''

import logging

from footie_scores import db
from footie_scores.apis import response_merges
from footie_scores.maps import competition_map
from footie_scores.apis.football_api import FootballAPI
from footie_scores.apis.football_data import FootballData
from footie_scores.db.schema import Fixture, Competition, Lineups, Team
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
        else:
            logger.info('%s already up to date in db', db_fixture)


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


def save_competitions():
    fapi_comps = FootballAPI().get_competitions()
    fdata_comps = FootballData().get_competitions()
    competitions = response_merges.merge_two_lists(
        fapi_comps,
        fdata_comps,
        id_map=competition_map['football-api_to_football-data'],
        consistent_keys=True)
    with db.session_scope() as session:
        for comp in competitions:
            if not row_exists(session, Competition, Competition.api_id, comp['api_id']):
                db_comp = Competition(**comp)
                session.add(db_comp)


def save_teams():
    api = FootballData()
    api_teams = api.get_competition_teams()
    with db.session_scope() as session:
        for team in api_teams:
            db_team = Team(**team)
            session.add(db_team)
            print('{} saved in db'.format(team['team_name']))
