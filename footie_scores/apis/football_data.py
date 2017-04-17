#!usr/bin/env python3
''' Interfaces to football score APIs '''

import os
from datetime import date, datetime

from footie_scores.utils.log import start_logging
from footie_scores.apis.base import FootballAPICaller


class FootballData(FootballAPICaller):
    '''
    Calls to the football-data API

    http://api.football-data.org/index
    '''

    def __init__(self, id_league='426', id_season=''):
        super().__init__()
        self.id_league = id_league
        self.id_season = id_season
        self.base_url = 'http://api.football-data.org/v1/'
        self.key = os.environ['football_data_key']
        self.headers = {'X-Auth-Token': self.key}
        self.datetime_format = "%Y-%m-%dT%H:%M:%SZ"
        self.match_page_ready_map = {
            'team_home': 'homeTeamName',
            'team_away': 'awayTeamName',
            'score_home': 'result',
            'score_away': 'result',
            'time_kick_off': 'date',
            'time_elapsed': 'status',
        }

    def _get_season_fixtures(self, season_id=426):
        '''
        Return all fixtures for a season. This is an expensive
        call so don't do often
        '''
        minutes_to_cache_expiry = 0.2
        fixtures_url = 'competitions/{id}/fixtures'.format(id=season_id)
        fixtures = self.check_cache_else_request(
            fixtures_url,
            minutes_to_cache_expiry,
        )
        return fixtures

    def _get_fixtures_for_date(self, date_):
        ''' Return list of today's fixtures '''
        fixtures = self._get_season_fixtures()['fixtures']
        dates = [self._fixture_date(fix) for fix in fixtures]
        todays_fixtures = [f for f, fdate_ in zip(fixtures, dates) if fdate_ == date_]
        return todays_fixtures

    def _make_fixtures_page_ready(self, fixtures):

        page_ready_fixtures = [
            {
            'team_home': f['homeTeamName'],
            'team_away': f['awayTeamName'],
            'score_home': f['result']['goalsHomeTeam'],
            'score_away': f['result']['goalsAwayTeam'],
            'time_kick_off': self._fixture_kickoff_time(f),
            'time_elapsed': 'TODO',
            }
            for f in fixtures]
        return page_ready_fixtures

    def _fixture_datetime(self, fixture):
        ''' datetime.datetime object for fixture '''
        raw = fixture['date']
        return datetime.strptime(raw, self.datetime_format)

    def _fixture_date(self, fixture):
        ''' datetime.date object for fixture '''
        f_datetime = self._fixture_datetime(fixture)
        return f_datetime.date()

    def _fixture_kickoff_time(self, fixture):
        return self._fixture_datetime(fixture).strftime("%H:%M")

    def _is_valid_response(self, response):
        return 'error' not in response.keys()


if __name__ == '__main__':
    start_logging()
    fd = FootballData()
    print (fd.page_ready_todays_fixtures())
