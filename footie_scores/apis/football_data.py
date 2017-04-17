#!usr/bin/env python3
''' Interfaces to football score APIs '''

import os
from datetime import date, datetime

import requests


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
