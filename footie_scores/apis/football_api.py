''' Interfaces to football score APIs '''

import os, re
import logging
import datetime as dt

from footie_scores import utils
from footie_scores import settings
from footie_scores.apis.base import FootballAPICaller
from footie_scores.utils.exceptions import *

logger = logging.getLogger(__name__)


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

    def get_competitions(self, source_competitions=settings.COMPS):
        competitions_url = 'competitions?'
        raw_competitions = self.request(competitions_url)
        competitions = _format_competitions(raw_competitions)
        logger.info('Competitions retrieved from football-api API')
        return _filter_competition_by_competition(competitions, source_competitions)

    def get_fixtures_for_date(self, start_date=None,
                              competitions=settings.COMPS,
                              end_date=None):

        if not start_date:
            start_date = utils.time.today()
        end_date = start_date if end_date is None else end_date
        str_start, str_end = [d.strftime(self.api_date_format) for d in (start_date, end_date)]
        fixtures_url = 'matches?from_date={}&to_date={}&'.format(str_start, str_end)
        [all_fixtures] = self.request(fixtures_url)
        fixtures = self._filter_fixture_by_competition(all_fixtures, competitions)

        logger.info('Fixtures for all competitions for %s to %s retrieved (%d fixtures)',
                    str_start, str_end, len(fixtures))
        return self._format_fixtures(fixtures)

    def get_lineups_for_fixtures(self, fixture_ids):
        urls = ['commentaries/{}?'.format(id_) for id_ in fixture_ids]
        # commentaries = self.batch_request(urls, correct_unicode=True)
        commentaries = self.request(*urls, correct_unicode=True)
        return [self._format_lineups(c) for c in commentaries]

    def _format_fixtures(self, fixtures):
        formatted_fixtures = [{
            'team_home': f['localteam_name'],
            'team_away': f['visitorteam_name'],
            'comp_api_id': int(f['comp_id']),
            'api_fixture_id': f['id'],
            'score': self._format_fixture_score(f),
            'date': self._make_date_db_ready(f['formatted_date']),
            'time': self._format_fixture_time(f['time']),
            'status': self._format_status(f),
            'events': self._format_events(f)
            } for f in fixtures]
        return formatted_fixtures

    def _format_lineups(self, commentary):
        c = commentary
        return {'api_fixture_id': c['match_id'],
                'home_lineup': c['lineup']['localteam'],
                'away_lineup': c['lineup']['visitorteam'],
                'home_subs': c['subs']['localteam'] if c['subs']['localteam'] else [],
                'away_subs': c['subs']['visitorteam'] if c['subs']['visitorteam'] else [],
        }

    def _format_status(self, fixture):
        if re.match('[0-9]+:[0-9]+', fixture['status']):
            # Status is kick off time so don't store as status.
            return ''
        return fixture['status']

    def _format_events(self, fixture):
        events = fixture['events']
        filter_keys = ('goal', 'subst')
        h_events = [e for e in events if e['team'] == 'localteam' and e['type'] in filter_keys]
        a_events = [e for e in events if e['team'] == 'visitorteam' and e['type'] in filter_keys]
        for events in (h_events, a_events):
            for e in events:
                if e['extra_min'] != '':
                    e['minutes_since_ko'] = int(e['minute']) + int(e['extra_min'])
                    e['time'] = e['minute'] + ' + ' + e['extra_min']
                else:
                    e['minutes_since_ko'] = int(e['minute'])
                    e['time'] = e['minute']
        return {'home': h_events, 'away': a_events}

    def _format_fixture_score(self, fixture):
        home_score = fixture['localteam_score']
        away_score = fixture['visitorteam_score']
        if home_score == '?' and away_score == '?':
            score = self._format_fixture_time(fixture['time']).strftime(self.db_time_format)
        else:
            score = '{} - {}'.format(home_score, away_score)
        return score

    def _format_fixture_time(self, fixture_time):
        ''' API returns dates in UTC timezone so convert to local timezone (i.e UK).

        Date seems to need to be involved otherwise there's a bug (?)
        where changing the timezone offsets the minutes rather than
        hours.
        '''
        if fixture_time == 'TBA' or fixture_time == 'Postp.':
            return fixture_time
        formatted_time = utils.time.reformat_datetime(
            fixture_time, self.api_time_format, self.db_time_format)
        return self._make_time_db_ready(formatted_time)

    def _filter_fixture_by_competition(self, fixtures, comp_ids):
        try:
            return [f for f in fixtures if int(f['comp_id']) in comp_ids]
        except:
            import traceback; traceback.print_exc();
            import ipdb; ipdb.set_trace()

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


def _format_competitions(competitions):
    formatted_competitions = [{
        'api_id': int(c['id']),
        'region': c['region'],
        'name': c['name']
    } for c in competitions]
    return formatted_competitions

def _filter_competition_by_competition(competitions, comp_ids):
    return [c for c in competitions if c['api_id'] in comp_ids]

