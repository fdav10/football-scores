#!usr/bin/env python3
''' Interfaces to football score APIs '''

import os
import logging
from datetime import date, datetime

import requests

from footie_scores.utils.log import start_logging
from footie_scores.utils.time import datetime_string_make_aware
from footie_scores.utils.cache import save_json, load_json, embed_in_dict_if_not_dict


logger = logging.getLogger(__name__)


class FootballAPICaller():
    def __init__(self):
        self.base_url = None
        self.headers = None
        self.url_suffix = None
        self.match_page_ready_map = None

    def check_cache_else_request(self, url, cache_expiry):
        request_url = self.base_url + url + self.url_suffix
        try:
            local_response = load_json(url.replace('/', '_')+'.json')
            response = local_response
        except FileNotFoundError:
            raw_response = requests.get(request_url, headers=self.headers)
            response = embed_in_dict_if_not_dict(raw_response.json(), key='data')
            save_json(response, url.replace('/', '_')+'.json', cache_expiry)

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
        raise NotImplementedError

    def _is_valid_response(self, response):
        raise NotImplementedError

class FootballData():
    '''
    Calls to the football-data API

    http://api.football-data.org/index
    '''

    def __init__(self):
        self.base_url = 'http://api.football-data.org/v1/'
        self.headers = {'X-Auth-Token': os.environ['football_data_key']}
        self.datetime_format = "%Y-%m-%dT%H:%M:%SZ"

    def get_season_fixtures(self, season_id=426):
        '''
        Return all fixtures for a season. This is an expensive
        call so don't do often
        '''
        fixtures_url = 'competitions/{id}/fixtures'.format(id=season_id)
        request = requests.get(self.base_url+fixtures_url, headers=self.headers)
        fixtures = request.json()['fixtures']
        return fixtures

    def get_todays_fixtures(self):
        ''' Return list of today's fixtures '''
        today = date.today()
        fixtures = self.get_season_fixtures()
        dates = [self._fixture_date(fix) for fix in fixtures]
        todays_fixtures = [f for f, date_ in zip(fixtures, dates) if date_ == today]
        return todays_fixtures

    def _fixture_datetime(self, fixture):
        ''' datetime.datetime object for fixture '''
        raw = fixture['date']
        return datetime.strptime(raw, self.datetime_format)

    def _fixture_date(self, fixture):
        ''' datetime.date object for fixture '''
        f_datetime = self._fixture_datetime(fixture)
        return f_datetime.date()


class SoccerSportsOpenData(FootballAPICaller):
    '''
    Calls to the Soccer-Sports Open Data API

    http://api.football-data.org/v1/
    
    get prefix indicates an API call
    '''

    def __init__(self, id_league, id_season):
        self.id_league = id_league
        self.id_season = id_season
        self.base_url = 'https://sportsop-soccer-sports-open-data-v1.p.mashape.com/v1/'
        self.headers = {
            'X-Mashape-Key': os.environ['ssod_key'],
            'Accept': 'application/json'}
        self.date_format = '%Y-%m-%dT%H:%M:%S%z'
        self.dt_format = '%Y-%m-%dT%H:%M:%S%z'
        self.match_page_ready_map = {
            'team_home': ('home', 'team'),
            'team_away': ('away', 'team'),
            'score_home': ('home', 'goals'),
            'score_away': ('away', 'goals'),
            'time_kick_off': ('TODO',),
            'time_elapsed': ('TODO',),
            }

    def check_cache_else_request(self, url, cache_expiry=0, description=None):
        try:
            local_request = load_json(url.replace('/', '_')+'.json')
            return local_request
        except FileNotFoundError:
            request = requests.get(self.base_url+url, headers=self.headers).json()
            save_json(request, url.replace('/', '_')+'.json', cache_expiry)
            return request

    def _todays_fixtures(self):
        today = date.today()
        active_rounds = self._active_rounds()
        id_rounds = [round_['round_slug'] for round_ in active_rounds]

        active_fixtures = []
        for id_ in id_rounds:
            active_fixtures += self._get_matches_in_round(id_)

        todays_fixtures = [f for f in active_fixtures if f['date_match'].date() == today]
        return todays_fixtures

    def _active_rounds(self):
        ''' Return rounds which include today's date '''
        logger.info('Getting active rounds')

        today = date.today()
        rounds = self._get_rounds_in_season()
        round_dates = [[r['start_date'].date(), r['end_date'].date()] for r in rounds]
        active_rounds = [
            r for r, d in zip(rounds, round_dates) if d[0] <= today <= d[1]]

        return active_rounds

    def _get_matches_in_round(self, id_round):

        minutes_to_cache_expire = 0.1
        matches_url = 'leagues/{}/seasons/{}/rounds/{}/matches'.format(
            self.id_league, self.id_season, id_round)
        matches = self.check_cache_else_request(
            matches_url, minutes_to_cache_expire, id_round)['data']['matches']

        for match in matches:
            match.update(self._get_match_details(id_round, match['match_slug']))

        return self._make_dates_aware(matches, date_keys=('date_match',))

    def _get_match_details(self, id_round, id_match):

        minutes_to_cache_expire = 0.1
        match_url = 'leagues/{}/seasons/{}/rounds/{}/matches/{}'.format(
            self.id_league, self.id_season, id_round, id_match)
        match_details = self.check_cache_else_request(
            match_url, minutes_to_cache_expire, id_round)

        return match_details

    def _get_rounds_in_season(self):
        ''' Return all fixtures for a season. '''
        minutes_to_cache_expire = 5
        fixtures_url = 'leagues/{}/seasons/{}/rounds'.format(self.id_league, self.id_season)
        rounds = self.check_cache_else_request(
            fixtures_url, minutes_to_cache_expire, self.id_season)['data']['rounds']

        return self._make_dates_aware(rounds, date_keys=('start_date', 'end_date'))

    def _make_dates_aware(self, list_with_dates, date_keys):
        ''' Convert date-time strings into Python datetime objects '''

        for dict_ in list_with_dates:
            for key in date_keys:
                date = dict_[key]
                dict_[key] = datetime_string_make_aware(date, self.dt_format)

        return list_with_dates

class Heisenbug(FootballAPICaller):
    '''
    Calls to the Premier League High Scores API

    https://market.mashape.com/heisenbug/premier-league-live-scores/overview
    '''

    def __init__(self, id_league='premierleague', id_season='2016-17'):
        self.id_league = id_league
        self.id_season = id_season
        self.base_url = 'https://heisenbug-premier-league-live-scores-v1.p.mashape.com/api/'
        self.headers = {
            'X-Mashape-Key': os.environ['heisenbug_key'],
            'Accept': 'application/json'}

    def get_season_fixtures(self):
        minutes_to_cache_expiry = 60 * 24
        fixtures = []

        for match_day in range(38):
            fixtures_url = self.base_url + '{}?matchday={}&season={}'.format(
                self.id_league, match_day+1, self.id_season)
            fixture = self.check_cache_else_request(fixtures_url, minutes_to_cache_expiry)
            fixtures += fixture


class FootballAPI(FootballAPICaller):
    '''
    Calls to the Football-API API

    https://football-api.com/
    '''

    def __init__(self, id_league='1204', id_season=''):
        self.id_league = id_league
        self.id_season = id_season
        self.base_url = 'http://api.football-api.com/2.0/'
        self.headers = None
        self.key = os.environ['football_api_key']
        self.url_suffix = 'Authorization=' + self.key
        self.date_format = '%d.%m.%Y'
        self.match_page_ready_map = {
            'team_home': 'localteam_name',
            'team_away': 'visitorteam_name',
            'score_home': 'localteam_score',
            'score_away': 'visitorteam_score',
            'time_kick_off': 'time',
            'time_elapsed': 'timer',
        }

    def get_competitions(self):
        minutes_to_cache_expiry = 60 * 24
        competitions_url = 'competitions?'
        return self.check_cache_else_request(
            competitions_url,
            minutes_to_cache_expiry,
        )

    def _todays_fixtures(self):
        return self._get_fixtures_for_date(date.today())

    def _get_fixtures_for_date(self, date_):
        minutes_to_cache_expiry = 0.2
        today = date_.strftime(self.date_format)
        fixtures_url = 'matches?comp_id={}&match_date={}&'.format(
            self.id_league, today)
        todays_fixtures = self.check_cache_else_request(
            fixtures_url,
            minutes_to_cache_expiry,
        )['data']

        return self._this_league_only(self.id_league, todays_fixtures)

    def _get_active_fixtures(self):
        minutes_to_cache_expiry = 0.2
        fixtures_url = 'matches?'
        active_fixtures = self.check_cache_else_request(
            fixtures_url,
            minutes_to_cache_expiry,
        )['data']

        return self._this_league_only(self.id_league, active_fixtures)

    def _this_league_only(self, league_id, matches):
        return [m for m in matches if m['comp_id'] == league_id]

    def _is_valid_response(self, response):
        try:
            assert isinstance(response, dict) and response['status'] == 'error'
            return False
        except (AssertionError, KeyError):
            return True


if __name__ == '__main__':
    start_logging()

    #sssod = SoccerSportsOpenData(id_league='premier-league', id_season='16-17')
    #print (sssod.page_ready_todays_fixtures())

    PL = FootballAPI()
    print (PL.page_ready_todays_fixtures())
    import ipdb; ipdb.set_trace()

