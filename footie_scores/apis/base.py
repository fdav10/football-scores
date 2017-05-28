''' Interfaces to football score APIs '''

import json
import logging
import datetime as dt

import requests

from footie_scores import db
from footie_scores import settings
from footie_scores.utils.exceptions import *
from footie_scores.utils.scheduling import batch_request
from footie_scores.db.queries import save_fixtures_to_db, save_competitions_to_db, save_lineups_to_db
from footie_scores.utils.strings import correct_unicode_to_bin

logger = logging.getLogger(__name__)


DEFAULT_COMMENTARY = {
    'lineup': {
        'visitorteam': [],
        'localteam': []}
}

class FootballAPICaller(object):
    '''
    Base class for classes which call specific football score APIs.

    Implements generic calls. Should not be instantiated.
    '''

    def __init__(self):
        self.id_league = None
        self.base_url = None
        self.headers = None
        self.url_suffix = ""
        self.match_page_ready_map = None
        self.api_date_format = None
        self.api_time_format = None
        self.db_date_format =  settings.DB_DATEFORMAT
        self.db_time_format = settings.DB_TIMEFORMAT

    def request(self, url, correct_unicode=False):
        logger.info('Making request to %s', self.base_url + url)
        request_url = self.base_url + url + self.url_suffix
        raw_response = requests.get(request_url, headers=self.headers)
        return self._process_responses((raw_response,), correct_unicode)[0]

    def batch_request(self, urls, correct_unicode=False):
        logger.info('Making batch request to:')
        for url in urls:
            logger.info('\t%s', url)
        urls = [self.base_url + url + self.url_suffix for url in urls]
        responses = batch_request(urls)
        return self._process_responses(responses, correct_unicode)

    def _process_responses(self, raw_responses, correct_unicode=False):
        responses = []
        for raw_response in raw_responses:
            try:
                assert raw_response.status_code == 200
            except AssertionError:
                logger.error(raw_response.content)
            else:
                if correct_unicode:
                    response = json.loads(correct_unicode_to_bin(raw_response.content))
                else:
                    response = raw_response.json()
                responses.append(response)
        return responses

    def todays_fixtures_to_db(self, competitions):
        fixtures = self._todays_fixtures(competitions)
        fixture_ids = [f.api_fixture_id for f in fixtures]
        # lineups = self._get_lineups_for_fixtures(fixture_ids)
        with db.session_scope() as session:
            save_fixtures_to_db(session, fixtures)
            # save_lineups_to_db(session, lineups)

    def competitions_to_db(self):
        competitions = self.get_competitions()
        with db.session_scope() as session:
            save_competitions_to_db(session, competitions)

    def get_competitions(self):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _todays_fixtures(self, competitions):
        fixtures = self._get_fixtures_for_date(dt.date.today(), competitions)
        return self._make_fixtures_db_ready(fixtures)

    def _make_date_db_ready(self, sdate):
        dt_obj = dt.datetime.strptime(sdate, self.db_date_format).date()
        return dt.datetime.strftime(dt_obj, self.db_date_format)

    def _make_time_db_ready(self, stime):
        dt_obj = dt.datetime.strptime(stime, self.db_time_format).time()
        return dt.time.strftime(dt_obj, self.db_time_format)

    def _filter_by_competition(self, competitions):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _get_fixtures_for_date(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _get_lineups_for_fixtures(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _make_fixtures_page_ready(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _make_fixtures_db_ready(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _is_valid_response(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")
