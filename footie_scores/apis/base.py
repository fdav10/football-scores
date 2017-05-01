#!usr/bin/env python3
''' Interfaces to football score APIs '''

from datetime import date

import requests

from footie_scores.utils.cache import save_json, embed_in_dict_if_not_dict


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
        self.date_format = None
        self.time_format = None

    def request(self, url):
        request_url = self.base_url + url + self.url_suffix
        raw_response = requests.get(request_url, headers=self.headers)
        response = embed_in_dict_if_not_dict(raw_response.json(), key='data')
        assert self._is_valid_response(response), "Error in request to %s\nResponse: %s" %(
            request_url, response)
        return response

    def save_request_in_db(self, url, cache_filename):
        '''
        Request a URL and save it in the cache for retrieval by the app.
        '''
        request_url = self.base_url + url + self.url_suffix
        raw_response = requests.get(request_url, headers=self.headers)
        response = embed_in_dict_if_not_dict(raw_response.json(), key='data')
        assert self._is_valid_response(response), "Error in request to %s\nResponse: %s" %(
            request_url, response)
        save_json(response, cache_filename)

    def page_ready_todays_fixtures(self, competition):
        todays = self._todays_fixtures(competition)
        return self._make_fixtures_page_ready(todays)

    def page_ready_todays_fixtures_to_db(self, competitions):
        for competition in competitions:
            fixtures = self.page_ready_todays_fixtures(competition)
            save_json(fixtures, 'todays_fixtures_' + competition)

    def page_ready_active_fixtures(self):
        fixtures = self._get_active_fixtures()
        return self._make_fixtures_page_ready(fixtures)

    def page_ready_fixture_details(self, fixture_id):
        return self._get_commentary_for_fixture(fixture_id)

    def page_ready_fixture_details_to_db(self, competitions):
        # TODO finish this
        pass

    def _todays_fixtures(self, competition):
        return self._get_fixtures_for_date(date.today(), competition)

    def _get_fixtures_for_date(self, arg1, arg2):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _get_active_fixtures(self):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _get_commentary_for_fixture(self, arg):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _make_fixtures_page_ready(self, arg):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _is_valid_response(self, response):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")
