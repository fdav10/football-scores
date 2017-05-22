''' Interfaces to football score APIs '''

import os
import logging
import datetime as dt

from footie_scores import settings
from footie_scores.db.schema import Fixture
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
        try:
            assert self._is_valid_response(response), 'Competition lookup failed'
        except:
            import traceback; traceback.print_exc();
            import ipdb; ipdb.set_trace()
        return response

    def _get_fixtures_for_date(self, date_=TODAY, competitions=settings.COMPS):
        str_date = date_.strftime(self.api_date_format)
        fixtures_url = 'matches?match_date={}&'.format(str_date)
        all_fixtures = self.request(fixtures_url)
        logger.info(
            'Fixtures for all competitions on date %s retrieved', dt.date.today())

        fixtures = self._filter_by_competition(all_fixtures, competitions)
        # commentaries = self._get_commentary_for_fixtures(fixtures)
        for f in fixtures:
            try:
                # TODO save these to db as they're retrieved
                f['commentary'] = self._get_commentary_for_fixture(f['id'])
            except (NoCommentaryAvailable, AuthorisationError):
                f['commentary'] = base.DEFAULT_COMMENTARY
                logger.info('No commentary for %s-%s on date %s',
                            f['localteam_name'], f['visitorteam_name'], dt.date.today())
        return fixtures

    def _get_commentary_for_fixture(self, fixture_id):
        commentary_url = 'commentaries/{}?'.format(fixture_id)
        try:
            commentary = self.request(commentary_url, correct_unicode=True)
            logger.info(
                'Commentary for fixture with id %s retrieved', fixture_id)
        except AuthorisationError:
            # TODO better error handling for random authorisation errors
            logger.info('AuthorisationError, default commentary used')
            commentary = base.DEFAULT_COMMENTARY
        return commentary

    def _get_commentary_for_fixtures(self, fixtures):
        urls = ['commentaries/{}?'.format(f['id']) for f in fixtures]
        commentaries = self.batch_request(urls, correct_unicode=True)
        return commentaries

    def _make_fixtures_db_ready(self, fixtures):
        db_ready_fixtures = [
            Fixture(
                f['localteam_name'],
                f['visitorteam_name'],
                f['comp_id'],
                f['id'],
                self._format_fixture_score(f),
                self._make_date_db_ready(f['formatted_date']),
                self._format_fixture_time(f, dt_object=True),
                self._get_lineup_from_commentary(f['commentary']),
                self._make_events_db_ready(f),
            ) for f in fixtures]
        return db_ready_fixtures

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

    def _get_lineup_from_commentary(self, commentary):
        try:
            return {'home': commentary['lineup']['localteam'],
                    'away': commentary['lineup']['visitorteam']}
        except KeyError:
            # attempt to catch elusive KeyError
            import traceback; traceback.print_exc();
            import ipdb; ipdb.set_trace()

    def _format_fixture_score(self, fixture):
        home_score = fixture['localteam_score']
        away_score = fixture['visitorteam_score']
        if home_score == '?' and away_score == '?':
            score = self._format_fixture_time(fixture)
        else:
            score = '{} - {}'.format(home_score, away_score)
        return score

    def _format_fixture_time(self, fixture, dt_object=False):
        ''' API returns dates in UTC timezone so convert to local timezone (i.e UK).

        Date seems to need to be involved otherwise there's a bug (?)
        where changing the timezone offsets the minutes rather than
        hours.
        '''
        formatted_time = naive_utc_to_uk_tz(
            fixture['time'],
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
            else:
                import ipdb; ipdb.set_trace()
                return False
        except (AssertionError, KeyError):
            return True


if __name__ == '__main__':
    start_logging()
    fa = FootballAPI()
