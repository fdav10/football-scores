''' Interfaces to football score APIs '''

import logging
from time import sleep
from datetime import date

import requests

from footie_scores.db.interface import save_fixture_dicts_to_db
from footie_scores.utils.exceptions import NoFixturesToday, NoCommentaryAvailable, AuthorisationError


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

    def request(self, url):
        request_url = self.base_url + url + self.url_suffix
        raw_response = requests.get(request_url, headers=self.headers)
        response = raw_response.json()
        try:
            assert self._is_valid_response(response), "Error in request to %s\nResponse: %s" %(
                request_url, response)
        except AuthorisationError:
            logger.info('Authorisation error. Request unsuccessful')

        return response

    def todays_fixtures_to_db(self, competitions):
        for competition in competitions:
            try:
                fixtures = self._db_ready_todays_fixtures()
                save_fixture_dicts_to_db(fixtures)
            except NoFixturesToday:
                logger.info('No fixtures for %s %s on date %s' %(
                    competition['region'], competition['name'], date.today()))

    def page_ready_fixture_details(self, fixture_id):
        return self._get_commentary_for_fixture(fixture_id)

    def get_competitions(self):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _db_ready_todays_fixtures(self ):
        fixtures = self._todays_fixtures()
        return self._make_fixtures_db_ready(fixtures)

    def _todays_fixtures(self):
        return self._get_fixtures_for_date(date.today())#, competition)

    def _get_fixtures_for_date(self, arg1):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _get_commentary_for_fixture(self, arg):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _make_fixtures_page_ready(self, arg):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _make_fixtures_db_ready(self, arg):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _is_valid_response(self, response):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")
