#!usr/bin/env python3
''' Interfaces to football score APIs '''

import logging
from datetime import date

import requests

from footie_scores.utils.cache import save_json, load_json, embed_in_dict_if_not_dict


class FootballAPICaller():
    '''
    Base class for classes which call specific football score APIs.

    Implements generic calls. Should not be instantiated.
    '''
    def __init__(self):
        self.base_url = None
        self.headers = None
        self.url_suffix = None
        self.match_page_ready_map = None

    def check_cache_else_request(self, url, cache_expiry):
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

    def _make_fixtures_page_ready(self, fixtures):
        page_ready_fixtures = [
            {y: f[z] for y, z in self.match_page_ready_map.items()}
            for f in fixtures]
        return page_ready_fixtures

    def _todays_fixtures(self):
        return self._get_fixtures_for_date(date.today())

    def _get_fixtures_for_date(self, arg):
        raise NotImplementedError

    def _is_valid_response(self, response):
        raise NotImplementedError
