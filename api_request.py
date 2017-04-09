#!usr/bin/env python3
''' Interfaces to football score APIs '''

from datetime import date, datetime

import requests


class FootballData():

    '''
    Calls to the football-data API

    http://api.football-data.org/index
    '''

    def __init__(self):
        self.base_url = 'http://api.football-data.org/v1/'
        self.headers = {'X-Auth-Token': '8d476a94d095407b93c0b26732a6216f'}
        self.dt_format = "%Y-%m-%dT%H:%M:%SZ"

    def get_season_fixtures(self, season_id=426):
        ''' Return all fixtures for a season '''
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
        return datetime.strptime(raw, self.dt_format)

    def _fixture_date(self, fixture):
        ''' datetime.date object for fixture '''
        f_datetime = self._fixture_datetime(fixture)
        return f_datetime.date()


class SoccerSportsOpenData():

    '''
    Calls to the Soccer-Sports Open Data API

    http://api.football-data.org/v1/
    '''

    def __init__(self):
        self.base_url = 'https://sportsop-soccer-sports-open-data-v1.p.mashape.com/v1/'
        self.headers = {
            'X-Mashape-Key': '8jU1jkN7P9mshbHyDD99iEelcw83p1028gFjsnou67N6cEMWR4',
            'Accept': 'application/json'}
        self.dt_format = '%Y-%m-%dT%H:%M:%S%z'

    def get_all_rounds_in_season(self, id_league='premier-league', id_season='16-17'):
        ''' Return all fixtures for a season '''
        fixtures_url = 'leagues/{}/seasons/{}/rounds'.format(id_league, id_season)
        request = requests.get(self.base_url+fixtures_url, headers=self.headers)
        rounds = request.json()['data']['rounds']
        return rounds

    def get_all_games_in_season(self, id_league='premier-league', id_season='16-17'):
        rounds = self.get_all_rounds_in_season(id_league, id_season)
        all_games = []
        for round_ in rounds[:5]:
            all_games += self.get_round_matches(round_['round_slug'], id_league, id_season)
        import ipdb; ipdb.set_trace()

    def get_round_matches(self, id_round, id_league='premier-league', id_season='16-17'):
        matches_url = 'leagues/{}/seasons/{}/rounds/{}/matches'.format(
            id_league, id_season, id_round)
        request = requests.get(self.base_url+matches_url, headers=self.headers)
        return request.json()['data']['matches']

    def get_todays_fixtures(self, seasons_fixtures):
        pass
        #TODO got to here

    def get_current_round(self):
        today = date.today()
        rounds = self.get_all_rounds_in_season()
        round_dates = [self._round_datetime_brackets(round_) for round_ in rounds]

    def _round_datetime_brackets(self, round):
        naives = [round['start_date'], round['end_date']]
        round_dates = []
        for naive in naives:
            round_dates.append(datetime.strptime(naive, self.dt_format).astimezone().date())

        return round_dates


if __name__ == '__main__':
    fbdata_lookup = FootballData()
    print (fbdata_lookup.get_todays_fixtures(), '\n')

    sssod = SoccerSportsOpenData()
    print (sssod.get_all_games_in_season())
