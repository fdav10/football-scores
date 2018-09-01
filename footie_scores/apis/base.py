''' Interfaces to football score APIs '''

import os
import json
import logging
import datetime as dt
import asyncio

import aiohttp

from footie_scores import utils
from footie_scores.utils.log import log_list
from footie_scores import settings
from footie_scores import REPO_ROOT
from footie_scores.utils.exceptions import *
from footie_scores.utils.generic import correct_unicode_to_bin

logger = logging.getLogger(__name__)


def log_request(f, *args, **kwargs):
    log_file_name = os.path.join(REPO_ROOT, 'logs', 'hourly_requests.log')
    def requests_wrapper(instance, *urls, **kwargs):
        log_urls = (urls,) if not isinstance(urls, (list, tuple)) else urls
        with open(log_file_name, 'a') as log_file:
            for url in log_urls:
                log_file.write('{}\t{}\n'.format(instance.base_url + url, utils.time.now()))
        output = f(instance, *urls, **kwargs)
        return output
    return requests_wrapper


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

    @log_request
    def request(self, *urls, correct_unicode=False):

        async def fetch(url):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    try:
                        assert response.status == 200
                    except AssertionError:
                        logger.info('%s: %s', url[:url.find(self.url_suffix)],
                                    await response.content.read())
                    else:
                        return await response.content.read()

        log_list(urls, logger, 'Making async batch request to:')

        urls = [self.base_url + url + self.url_suffix for url in urls]
        event_loop = asyncio.get_event_loop()
        coros = [fetch(url) for url in urls]
        future = asyncio.gather(*coros)

        event_loop.run_until_complete(future)

        responses = future.result()
        logger.info('Done.')

        return self._process_responses(responses, correct_unicode)

    def _process_responses(self, raw_responses, correct_unicode=False):
        responses = []
        for raw_response in raw_responses:
            if raw_response and correct_unicode:
                response = json.loads(correct_unicode_to_bin(raw_response))
            else:
                response = json.loads(raw_response)
            responses.append(response)
        return responses

    def get_lineups_for_fixtures(self, fixture_ids):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

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

    def _make_fixtures_page_ready(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _format_fixtures(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")

    def _is_valid_response(self, *args):
        raise NotImplementedError(
            "Implemented in child classes - base class should not be instantiated")
