#!usr/bin/env python3
''' Interfaces to football score APIs '''

import logging
from datetime import date

import requests

from footie_scores.utils.cache import save_json, load_json, embed_in_dict_if_not_dict


class FootballAPICaller(object):
    '''
    Base class for classes which call specific football score APIs.

    Implements generic calls. Should not be instantiated.
    '''
    def __init__(self):
        self.base_url = None
        self.headers = None
        self.url_suffix = ""
        self.match_page_ready_map = None
        self.date_format = None
        self.time_format = None

    def check_cache_else_request(self, url, cache_expiry):
        '''
        Request a url but check local cache first.

        If a response is found in the cache then this is returned and no
        request is made to the API. If a request is made to the API
        then the response is saved in the cache.  An expiry time is
        attached to each file in the cache and cache files are checked
        to see if they've expired before they're returned.

        Some APIs return lists.  Dicts are preferable because this
        allows the expiry timestamp to be attached.  When a list is
        returned it's embedded in a dict under the key 'data'.
        '''
        request_url = self.base_url + url + self.url_suffix
        cache_filename = url.replace('/', '_')+'.json'
        try:
            local_response = load_json(cache_filename)
            response = local_response
        except FileNotFoundError:
            raw_response = requests.get(request_url, headers=self.headers)
            response = embed_in_dict_if_not_dict(raw_response.json(), key='data')
            save_json(response, cache_filename, cache_expiry)

        assert self._is_valid_response(response), "Error in request to %s\nResponse: %s" %(
            request_url, response)
        return response

    def page_ready_todays_fixtures(self):
        todays = self._todays_fixtures()
        return self._make_fixtures_page_ready(todays)

    def page_ready_finished_fixtures(self, date):
        fixtures = self._get_fixtures_for_date(date)
        return self._make_fixtures_page_ready(fixtures)

    def page_ready_active_fixtures(self):
        fixtures = self._get_active_fixtures()
        return self._make_fixtures_page_ready(fixtures)

    def page_ready_fixture_details(self, fixture_id):
        return self._get_commentary_for_fixture(fixture_id)

    def _todays_fixtures(self):
        return self._get_fixtures_for_date(date.today())

    def _get_fixtures_for_date(self, arg):
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
