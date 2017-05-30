#!/usr/bin/env python

'''
Module where the database and API calls are linked.
'''

import time
import logging
import datetime as dt

from footie_scores import db, settings, utils
from footie_scores.utils.log import start_logging, log_list, log_time_util_next_fixture
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
    db.schema.drop_tables()
    db.schema.create_tables_if_not_present()
    save_competitions_to_db()
    FixturesUpdater(StartupState())


def update_fixtures_lineups(session, fixtures):
    needs_lineups = [f for f in fixtures if not f.has_lineups()]
    logger.info('%d fixtures kicking off soon do not have lineups:\n%s', len(needs_lineups), needs_lineups)
    fixture_ids = [f.api_fixture_id for f in needs_lineups]
    FootballAPI().fixture_lineups_to_db(session, fixture_ids)


def time_to_next_kickoff(fixtures):
    times_to_kickoff = [f.time_to_kickoff for f in fixtures]
    return sorted(times_to_kickoff)[0]


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
    ''' Check when next game kicks off and sleep until closer to then '''
    def __init__(self):
        logger.info('Entered idle state')
        self.run()

    def run(self):
        with db.session_scope() as session:
            fixtures_today = db.queries.get_fixtures_by_date(session, utils.time.today())
            update_fixtures_lineups(session, fixtures_today)
            future_fixtures = [f for f in fixtures_today if f.status != 'FT']
            if not future_fixtures:
                logger.info('No games today, sleeping for 3 hours')
                time.sleep(settings.NO_GAMES_SLEEP)
                return IdleState()
            else:
                log_list(fixtures_today, intro='Todays fixtures:')
                time_to_next_game = time_to_next_kickoff(future_fixtures)
                if time_to_next_game < settings.PRE_GAME_ACTIVE_PERIOD:
                    return ActiveState()
                elif time_to_next_game < settings.PRE_GAME_PREP_PERIOD:
                    return PreparationState()
                else:
                    sleeptime = time_to_next_game - settings.PRE_GAME_PREP_PERIOD
                    log_time_util_next_fixture(time_to_next_game, sleeptime)
                    time.sleep(sleeptime)
                    return PreparationState()


class PreparationState():
    ''' Try and get lineups in the period leading up to kick-offs '''
    def __init__(self):
        logger.info('Entered preparation state')
        self.run()

    def run(self):
        active_fixtures = False
        with db.session_scope() as session:
            fixtures_today = refresh_and_get_todays_fixtures(session)
            while not active_fixtures:
                active_fixtures = [f for f in fixtures_today if f.is_active()]
                fixtures_soon = [f for f in fixtures_today if 0 < f.time_to_kickoff < settings.PRE_GAME_PREP_PERIOD]
                needs_lineups = [f for f in fixtures_soon if not f.has_lineups()]
                if not needs_lineups:
                    time_to_next_game = time_to_next_kickoff(fixtures_soon)
                    log_time_util_next_fixture(time_to_next_game, time_to_next_game)
                    time.sleep(time_to_next_game)
                    return ActiveState()
                else:
                    update_fixtures_lineups(session, needs_lineups)
                    logger.info('Prep state pausing for %d seconds', settings.PREP_STATE_PAUSE)
                    time.sleep(settings.PREP_STATE_PAUSE)
        return ActiveState()


class ActiveState():
    ''' Update fixture scores periodically when games are ongoing'''
    def __init__(self):
        logger.info('Entered active state')
        self.run()

    def run(self):
        active_fixtures = True
        while active_fixtures:
            with db.session_scope() as session:
                fixtures = refresh_and_get_todays_fixtures(session)
                active_fixtures = [f for f in fixtures if f.is_active()]
                fixtures_soon = [f for f in fixtures if 0 < f.time_to_kickoff < settings.PRE_GAME_PREP_PERIOD]
                needs_lineups = [f for f in fixtures_soon if not f.has_lineups()]
                if needs_lineups:
                    update_fixtures_lineups(session, needs_lineups)
            logger.info('Active state pausing for %d seconds', settings.ACTIVE_STATE_PAUSE)
            time.sleep(settings.ACTIVE_STATE_PAUSE)
        return IdleState()


if __name__ == '__main__':
    start_logging()
    main()
