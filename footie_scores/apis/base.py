''' Interfaces to football score APIs '''

import json
import logging
import datetime as dt

import requests

from footie_scores import utils
from footie_scores import settings
from footie_scores.utils.exceptions import *
from footie_scores.utils.scheduling import batch_request
from footie_scores.utils.strings import correct_unicode_to_bin

logger = logging.getLogger(__name__)


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
        self.db_date_format = settings.DB_DATEFORMAT
        self.db_time_format = settings.DB_TIMEFORMAT

    def request(self, url, correct_unicode=False):
        logger.info('Making request to %s', self.base_url + url)
        request_url = self.base_url + url + self.url_suffix
        raw_response = requests.get(request_url, headers=self.headers)
        return self._process_responses((raw_response,), correct_unicode)[0]

    def batch_request(self, urls, correct_unicode=False):
        utils.log.log_list(urls, 'Making batch request to:')
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

    def fixture_lineups(self, fixture_ids):
        lineups = self._get_lineups_for_fixtures(fixture_ids)
        return lineups

    def competitions_to_db(self):
        return self.get_competitions()

    def get_competitions(self):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def todays_fixtures(self, competitions):
        fixtures = self.get_fixtures_for_date(utils.time.today(), competitions)
        return fixtures

    def _make_date_db_ready(self, sdate):
        ''' Convert string date to date object '''
        dt_obj = dt.datetime.strptime(sdate, self.db_date_format).date()
        return dt_obj

    def _make_time_db_ready(self, stime):
        ''' Convert string time to time object '''
        dt_obj = dt.datetime.strptime(stime, self.db_time_format).time()
        return dt_obj

    def get_fixtures_for_date(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _filter_by_competition(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _get_lineups_for_fixtures(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _make_fixtures_page_ready(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _format_fixtures(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _is_valid_response(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")
