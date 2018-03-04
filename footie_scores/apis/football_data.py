#!usr/bin/env python3
''' Interfaces to football score APIs '''

import os, logging
from datetime import date, datetime

from footie_scores.utils.log import start_logging
from footie_scores.apis.base import FootballAPICaller

logger = logging.getLogger(__name__)


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

    def get_competitions(self):
        comps_url = 'competitions'
        competitions = self.request(comps_url)
        logger.info('Competitions retrieved from football-data API')
        return _format_competitions(competitions)

    def get_competition_teams(self):
        comp_teams_url = 'competitions/445/teams'
        teams = self.request(comp_teams_url)
        logger.info('Teams for competition id %d retrieved from football-data API',
                    445)
        return _format_teams(teams['teams'])

    def _get_season_fixtures(self, season_id=426):
        '''
        Return all fixtures for a season. This is an expensive
        call so don't do often
        '''
        raise NotImplementedError
        fixtures_url = 'competitions/{id}/fixtures'.format(id=season_id)
        fixtures = None
        return fixtures

    def _get_fixtures_for_date(self, date_):
        ''' Return list of today's fixtures '''
        raise NotImplementedError
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


def _format_teams(raw_teams):
    formatted_teams = [{
        'team_name': team['name'],
        'short_name': team['code'],
        'api_id': _team_id_from_url(team['_links']['self']['href']),
    } for team in raw_teams]
    return formatted_teams


def _format_competitions(raw_comps):
    comp = raw_comps[0]
    ckeys = comp.keys()
    formatted_comps = [{
        'football-data_api_id': int(c['id']),
        'name': comp_remove_formatting(c['caption']),
        'short_name': c['league'],
        'n_teams': c['numberOfTeams'],
        'n_fixtures': c['numberOfGames'],
        'n_matchdays': c['numberOfMatchdays'],
    } for c in raw_comps]
    return formatted_comps


def _team_id_from_url(team_url):
    return team_url.split('/')[-1]


def comp_remove_formatting(string):
    def not_punc(char):
        o = ord(char)
        if 58 <= o <= 64:
            return False
        if 91 <= o <= 96:
            return False
        if 123 <= o <= 127:
            return False
        return True
    no_punct = ''.join([c for c in string if not_punc(c)])
    no_date = no_punct[:len(no_punct)-no_punct[::-1].find(' ')-1]
    return no_date


if __name__ == '__main__':
    start_logging()
    fd = FootballData()
    print(fd.page_ready_todays_fixtures())
