'''
Module where the database and API calls are linked.
'''

import time
import logging
import datetime as dt

from footie_scores import db
from footie_scores import settings
from footie_scores import constants
from footie_scores.apis.football_api import FootballAPI
from footie_scores.utils.scheduling import start_periodic_calls, schedule_action
from footie_scores.utils.log import start_logging


logger = logging.getLogger(__name__)


def refresh_and_get_todays_fixtures(session):
    comp_api = FootballAPI()
    comp_api.todays_fixtures_to_db(settings.COMPS)
    return db.queries.get_fixtures_by_date(session, settings.TODAY)


def single_api_call(competitions=settings.COMPS):
    comp_api = FootballAPI()
    comp_api.todays_fixtures_to_db(competitions)


def save_competitions_to_db():
    comp_api = FootballAPI()
    comp_api.competitions_to_db()


def update_fixtures_schedule(fixtures):
    fixtures_active = any([f.is_active() for f in fixtures])
    if fixtures_active:
        schedule_action(single_api_call, 30)
    else:
        schedule_action(single_api_call, 120)


def main():
    pass

class FixturesUpdater():

    def __init__(self, initial_state):
        self.state = initial_state


class StartupState():
    def __init__(self):
        self.run()

    def run(self):
        print('Entered startup state')
        single_api_call()
        with db.session_scope() as session:
            fixtures = db.queries.get_fixtures_by_date(session, settings.TODAY)
            fixtures_active = any([f.is_active() for f in fixtures])
        if fixtures_active:
            return ActiveState()
        else:
            return IdleState()


class IdleState():
    def __init__(self):
        print('Entered idle state')
        self.run()

    def run(self):
        with db.session_scope() as session:
            fixtures = db.queries.get_fixtures_by_date(session, settings.TODAY)
            future_fixtures = [f for f in fixtures if f.status != 'FT']
            dtformat = settings.DB_DATETIMEFORMAT
            ko_times = [dt.datetime.strptime(f.date+'-'+f.time, dtformat) for f in future_fixtures]
            next_game_start = sorted(ko_times)[0]
            time_to_next_game = (next_game_start - dt.datetime.now()).total_seconds()
            if time_to_next_game < 600:
                return ActiveState()
            else:
                logger.info('Next game in %.1f minutes, waiting' %(time_to_next_game / 60))
                time.sleep(time_to_next_game * 0.9)
                return IdleState()


class ActiveState():
    def __init__(self):
        self.api = FootballAPI()
        print('Entered active state')
        self.run()

    def run(self):
        fixtures_active = True
        while fixtures_active:
            with db.session_scope() as session:
                fixtures = refresh_and_get_todays_fixtures(session)
                fixtures_active = any([f.is_active() for f in fixtures])
            logger.info('Pausing for 30 seconds')
            time.sleep(30)
        return IdleState()


if __name__ == '__main__':
    start_logging()
    FixturesUpdater(StartupState())
