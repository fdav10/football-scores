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


def single_api_call(competitions=settings.COMPS):
    comp_api = FootballAPI()
    comp_api.todays_fixtures_to_db(competitions)


def save_competitions_to_db():
    comp_api = FootballAPI()
    comp_api.competitions_to_db()
