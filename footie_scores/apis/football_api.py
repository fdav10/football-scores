''' Interfaces to football score APIs '''

import os
import logging
import datetime as dt

from footie_scores import settings
from footie_scores.db.schema import Fixture, Lineups
from footie_scores.apis import base
from footie_scores.utils.log import start_logging
from footie_scores.apis.base import FootballAPICaller
from footie_scores.utils.time import datetime_string_make_aware, naive_utc_to_uk_tz
from footie_scores.utils.exceptions import *


logger = logging.getLogger(__name__)
TODAY = dt.date.today()

class FootballAPI(FootballAPICaller):
    '''
    Calls to the Football-API API

    https://football-api.com/
    '''


    def __init__(self, id_season=''):
        super().__init__()
        self.id_season = id_season
        self.base_url = 'http://api.football-api.com/2.0/'
        self.key = os.environ['football_api_key']
        self.headers = None
        self.url_suffix = 'Authorization=' + self.key
        self.api_date_format = '%d.%m.%Y'
        self.api_time_format = '%H:%M'

    def get_competitions(self):
        competitions_url = 'competitions?'
        response = self.request(competitions_url)
        logger.info('Competitions retrieved from football-api API')
        return response

    def _get_fixtures_for_date(self, date_=TODAY, competitions=settings.COMPS):
        str_date = date_.strftime(self.api_date_format)
        fixtures_url = 'matches?match_date={}&'.format(str_date)
        all_fixtures = self.request(fixtures_url)
        logger.info(
            'Fixtures for all competitions on date %s retrieved', dt.date.today())
        fixtures = self._filter_by_competition(all_fixtures, competitions)
        return fixtures

    def _make_fixtures_db_ready(self, fixtures):
        db_ready_fixtures = [
            Fixture(
                f['localteam_name'],
                f['visitorteam_name'],
                f['comp_id'],
                f['id'],
                self._format_fixture_score(f),
                self._make_date_db_ready(f['formatted_date']),
                self._format_fixture_time(f['time']),
                f['status'],
                self._make_events_db_ready(f),
            ) for f in fixtures]
        return db_ready_fixtures

    def _get_lineups_for_fixtures(self, fixture_ids):
        urls = ['commentaries/{}?'.format(id_) for id_ in fixture_ids]
        commentaries = self.batch_request(urls, correct_unicode=True)
        return [self._make_lineups_db_ready(c) for c in commentaries]

    def _make_lineups_db_ready(self, commentary):
        return Lineups(
            commentary['match_id'],
            commentary['lineup']['localteam'],
            commentary['lineup']['visitorteam']
        )

    def _make_events_db_ready(self, fixture):
        events = fixture['events']
        filter_keys = ('goal',)
        h_events = [e for e in events if e['team'] == 'localteam' and e['type'] in filter_keys]
        a_events = [e for e in events if e['team'] == 'visitorteam' and e['type'] in filter_keys]
        for events in (h_events, a_events):
            for e in events:
                if e['extra_min'] != '':
                    e['time'] = e['minute'] + ' + ' + e['extra_min']
                else:
                    e['time'] = e['minute']
        return {'home': h_events, 'away': a_events}

    def _format_fixture_score(self, fixture):
        home_score = fixture['localteam_score']
        away_score = fixture['visitorteam_score']
        if home_score == '?' and away_score == '?':
            score = self._format_fixture_time(fixture['time'])
        else:
            score = '{} - {}'.format(home_score, away_score)
        return score

    def _format_fixture_time(self, fixture_time):
        ''' API returns dates in UTC timezone so convert to local timezone (i.e UK).

        Date seems to need to be involved otherwise there's a bug (?)
        where changing the timezone offsets the minutes rather than
        hours.
        '''
        formatted_time = naive_utc_to_uk_tz(
            fixture_time,
            self.api_time_format,
            self.db_time_format)
        return self._make_time_db_ready(formatted_time)


    def _filter_by_competition(self, fixtures, comp_ids):
        return [f for f in fixtures if f['comp_id'] in comp_ids]


    def _is_valid_response(self, response):
        # TODO this is pretty ugly and unclear
        try:
            assert isinstance(response, dict)
            if 'Key not authorised' in response.values():
                raise AuthorisationError(self.key)
            assert response['status'] == 'error'
            if 'There are no matches at the moment' in response['message']:
                raise NoFixturesToday()
            elif 'We did not find commentaries' in response['message']:
                raise NoCommentaryAvailable()
        except (AssertionError, KeyError):
            return True


if __name__ == '__main__':
    start_logging()
    fa = FootballAPI()
