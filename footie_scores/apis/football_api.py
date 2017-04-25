#!usr/bin/env python3
''' Interfaces to football score APIs '''

import os
import logging
from datetime import datetime, date

from footie_scores.utils.log import start_logging
from footie_scores.apis.base import FootballAPICaller
from footie_scores.utils.time import datetime_string_make_aware


logger = logging.getLogger(__name__)

LEAGUE_ID_MAP = {
    'champions league': '1005',
    'europa league': '1007',
    'austria': '1093',
    'belgium': '1102',
    'czechoslovakia': '1184',
    'england cup': '1198',
    'england league cup': '1199',
    'england': '1204',
    'england 2nd': '1205',
    'france': '1221',
    'germany': '1229',
    'greece': '1232',
    'italy 2nd': '1265',
    'italy': '1269',
    'netherlands': '1322',
    'portugal': '1352',
    'spain cup': '1397',
    'spain': '1399',
    'switzerland': '1408',
    'turkey': '1425',
    'ukraine': '1428',
    'russia': '1457',
    None: None,
}

MINUTES_TO_CACHE_EXPIRY = {
    'competitions': 60 * 24,
    'game_active': 1,
    'game_past': 1,
}

class FootballAPI(FootballAPICaller):
    '''
    Calls to the Football-API API

    https://football-api.com/
    '''

    def __init__(self, competition=None, id_season=''):
        super().__init__()
        self.id_league = LEAGUE_ID_MAP[competition]
        self.id_season = id_season
        self.base_url = 'http://api.football-api.com/2.0/'
        self.key = os.environ['football_api_key']
        self.headers = None
        self.url_suffix = 'Authorization=' + self.key
        self.date_format = '%d.%m.%Y'
        self.time_format = '%H:%M'

    def _get_competitions(self):
        minutes_to_cache_expiry = MINUTES_TO_CACHE_EXPIRY['competitions']
        competitions_url = 'competitions?'
        return self.check_cache_else_request(
            competitions_url,
            minutes_to_cache_expiry,
        )

    def _get_fixtures_for_date(self, date_):
        # TODO games in the past and active games aren't differentiated here
        minutes_to_cache_expiry = MINUTES_TO_CACHE_EXPIRY['game_past']
        today = date_.strftime(self.date_format)
        fixtures_url = 'matches?comp_id={}&match_date={}&'.format(
            self.id_league, today)
        todays_fixtures = self.check_cache_else_request(
            fixtures_url,
            minutes_to_cache_expiry,
        )['data']

        return self._this_league_only(self.id_league, todays_fixtures)

    def _get_active_fixtures(self):
        minutes_to_cache_expiry = MINUTES_TO_CACHE_EXPIRY['game_active']
        fixtures_url = 'matches?'
        active_fixtures = self.check_cache_else_request(
            fixtures_url,
            minutes_to_cache_expiry,
        )['data']

        return self._this_league_only(self.id_league, active_fixtures)

    def _get_commentary_for_fixture(self, fixture_id):
        # TODO class requires competition ID but this method doesn't.
        # Would be useful to be able to call this method without
        # instantiating the class with a competition ID. Stop-gap
        # solution is to allow class instantiated with competition=None.
        minutes_to_cache_expiry = MINUTES_TO_CACHE_EXPIRY['game_active']
        commentary_url = 'commentaries/{}?'.format(fixture_id)
        commentary = self.check_cache_else_request(
            commentary_url,
            minutes_to_cache_expiry)
        return self._make_commentary_page_ready(commentary)

    def _make_fixtures_page_ready(self, fixtures):
        page_ready_fixtures = [
            {
                'team_home': f['localteam_name'],
                'team_away': f['visitorteam_name'],
                'score': self._format_fixture_score(f),
                'score_home': f['localteam_score'],
                'score_away': f['visitorteam_score'],
                'time_kick_off': self._format_fixture_time(f),
                'time_elapsed': f['timer'],
                'home_events': self._make_events_page_ready('localteam', f['events']),
                'away_events': self._make_events_page_ready('visitorteam', f['events']),
                'id': f['id'],
                'home_lineup': None,
                'away_lineup': None,
            }
            for f in fixtures]

        return page_ready_fixtures

    def _make_events_page_ready(self, team, fixture_events):
        filter_keys = ('goal',)
        events = [e for e in fixture_events if e['team'] == team and e['type'] in filter_keys]
        for e in events:
            if e['extra_min'] != '':
                e['time'] = e['minute'] + ' + ' + e['extra_min']
            else:
                e['time'] = e['minute']

        return events

    def _make_commentary_page_ready(self, commentary):
        page_ready_commentary = {
            'lineup_home': commentary['lineup']['localteam'],
            'lineup_away': commentary['lineup']['visitorteam'],
        }
        return page_ready_commentary

    def _format_fixture_score(self, fixture):
        home_score = fixture['localteam_score']
        away_score = fixture['visitorteam_score']
        if home_score == '?' and away_score == '?':
            score = fixture['time']
        else:
            score = '{} - {}'.format(home_score, away_score)
        return score

    def _format_fixture_time(self, fixture):
        # TODO make sure this outputs in local time zone (my local for now)
        dt_time = datetime_string_make_aware(fixture['time'], self.time_format)
        return dt_time

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
    fa = FootballAPI()
    #print (fa.page_ready_todays_fixtures())
    print(fa.page_ready_finished_fixtures(date(year=2017, month=4, day=15)))
