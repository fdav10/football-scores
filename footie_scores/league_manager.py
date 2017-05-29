'''
Module where the database and API calls are linked.
'''

import time
import logging
import datetime as dt

from footie_scores import db, settings, utils
from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.utils.scheduling import schedule_action


logger = logging.getLogger(__name__)


def refresh_and_get_todays_fixtures(session):
    comp_api = FootballAPI()
    comp_api.todays_fixtures_to_db(settings.COMPS)
    return db.queries.get_fixtures_by_date(session, utils.time.today())


def single_api_call(competitions=settings.COMPS):
    comp_api = FootballAPI()
    comp_api.todays_fixtures_to_db(competitions)


def save_competitions_to_db():
    comp_api = FootballAPI()
    comp_api.competitions_to_db()


def main():
    FixturesUpdater(StartupState())


def update_fixtures_lineups(session, fixtures):
    needs_lineups = [f for f in fixtures if not f.has_lineups()]
    logger.info('%d fixtures do not have lineups:\n%s', len(needs_lineups), needs_lineups)
    fixture_ids = [f.api_fixture_id for f in needs_lineups]
    FootballAPI().fixture_lineups_to_db(session, fixture_ids)


class FixturesUpdater():
    def __init__(self, initial_state):
        self.state = initial_state


class StartupState():
    def __init__(self):
        self.run()

    def run(self):
        logger.info('Entered startup state')
        single_api_call()
        with db.session_scope() as session:
            fixtures = db.queries.get_fixtures_by_date(session, utils.time.today())
            fixtures_active = any([f.is_active() for f in fixtures])
        if fixtures_active:
            return ActiveState()
        else:
            return IdleState()


class IdleState():
    ''' Check when next game kicks off and sleep until close to then '''
    def __init__(self):
        logger.info('Entered idle state')
        self.run()

    def run(self):
        with db.session_scope() as session:
            fixtures = db.queries.get_fixtures_by_date(session, utils.time.today())
            future_fixtures = [f for f in fixtures if f.status != 'FT']
            times_to_kickoff = [f.time_to_kickoff for f in future_fixtures]
        time_to_next_game = sorted(times_to_kickoff)[0]
        if time_to_next_game < 600:
            return ActiveState()
        elif time_to_next_game < 3600:
            return PreparationState()
        else:
            logger.info('Next game in %.1f minutes, waiting' %(time_to_next_game / 60))
            time.sleep(time_to_next_game * 0.9)
            return IdleState()


class PreparationState():
    ''' Try and get lineups in the period leading up to kick-offs '''
    def __init__(self):
        self.api = FootballAPI()
        logger.info('Entered preparation state')
        self.run()

    def run(self):
        with db.session_scope() as session:
            with db.session_scope() as session:
                fixtures = refresh_and_get_todays_fixtures(session)
                fixtures_soon = [f for f in fixtures if 0 < f.time_to_kickoff < 3600]
                update_fixtures_lineups(session, [f for f in fixtures_soon])
        logger.info('Prep state pausing for %d seconds', settings.PREP_STATE_PAUSE)
        time.sleep(settings.PREP_STATE_PAUSE)
        return IdleState()


class ActiveState():
    ''' Update fixture scores periodically when games are ongoing'''
    def __init__(self):
        self.api = FootballAPI()
        logger.info('Entered active state')
        self.run()

    def run(self):
        active_fixtures = True
        while active_fixtures:
            with db.session_scope() as session:
                fixtures = refresh_and_get_todays_fixtures(session)
                active_fixtures = [f for f in fixtures if f.is_active()]
                update_fixtures_lineups(session, active_fixtures)
            logger.info('Active state pausing for %d seconds', settings.ACTIVE_STATE_PAUSE)
            time.sleep(settings.ACTIVE_STATE_PAUSE)
        return IdleState()


if __name__ == '__main__':
    start_logging()
    FixturesUpdater(StartupState())
