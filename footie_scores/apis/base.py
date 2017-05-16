''' Interfaces to football score APIs '''

import json
import logging
from datetime import date

import requests

from footie_scores.utils.exceptions import *
from footie_scores.db.interface import save_fixture_dicts_to_db
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

    date_format = None
    time_format = None

    def __init__(self):
        self.id_league = None
        self.base_url = None
        self.headers = None
        self.url_suffix = ""
        self.match_page_ready_map = None
        self.date_format = None
        self.time_format = None

    def request(self, url, correct_unicode=False):
        request_url = self.base_url + url + self.url_suffix
        raw_response = requests.get(request_url, headers=self.headers)
        if correct_unicode:
            response = json.loads(correct_unicode_to_bin(raw_response.content))
        else:
            response = raw_response.json()
        assert self._is_valid_response(response), "Error in request to %s\nResponse: %s" %(
            request_url, response)
        return response

    def todays_fixtures_to_db(self, competitions):
        fixtures = self._todays_fixtures(competitions)
        save_fixture_dicts_to_db(fixtures)

    def page_ready_fixture_details(self, fixture_id):
        return self._get_commentary_for_fixture(fixture_id)

    def get_competitions(self):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _todays_fixtures(self, competitions):
        fixtures = self._get_fixtures_for_date(date.today(), competitions)
        # from datetime import timedelta
        # yesterday = date.today() - timedelta(days=1)
        # fixtures = self._get_fixtures_for_date(yesterday, competitions)
        return self._make_fixtures_db_ready(fixtures)

    def _filter_by_competition(self, competitions):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _get_fixtures_for_date(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _get_commentary_for_fixture(self, *args):
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
