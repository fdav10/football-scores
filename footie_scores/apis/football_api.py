''' Interfaces to football score APIs '''

import os
import logging
import datetime as dt

import pytz

from footie_scores.apis import base
from footie_scores.utils.log import start_logging
from footie_scores.apis.base import FootballAPICaller
from footie_scores.utils.time import datetime_string_make_aware
from footie_scores.utils.exceptions import NoFixturesToday, NoCommentaryAvailable


logger = logging.getLogger(__name__)


class FootballAPI(FootballAPICaller):
    '''
    Calls to the Football-API API

    https://football-api.com/
    '''

    # TODO this class is a bit confused over whether a competition is required or not

    def __init__(self, competition=None, id_season=''):
        super().__init__()
        if competition:
            self.id_league = competition['id']
        self.id_season = id_season
        self.base_url = 'http://api.football-api.com/2.0/'
        self.key = os.environ['football_api_key']
        self.headers = None
        self.url_suffix = 'Authorization=' + self.key
        self.date_format = '%d.%m.%Y'
        self.time_format = '%H:%M'

    def get_competitions(self):
        competitions_url = 'competitions?'
        return self.request(competitions_url)

    def _get_fixtures_for_date(self, date_, competition):
        str_date = date_.strftime(self.date_format)
        fixtures_url = 'matches?comp_id={}&match_date={}&'.format(
            competition['id'], str_date)
        todays_fixtures = self.request(fixtures_url)['data']
        logger.info(
            'Fixtures for %s %s on date %s retrieved',
            competition['region'], competition['name'], dt.date.today())

        for f in todays_fixtures:
            try:
                f['commentary'] = self._get_commentary_for_fixture(f['id'])
            except NoCommentaryAvailable:
                f['commentary'] = base.DEFAULT_COMMENTARY
                logger.info('No commentary for %s-%s on date %s',
                            f['localteam_name'], f['visitorteam_name'], dt.date.today())
        return todays_fixtures

    def _get_active_fixtures(self):
        fixtures_url = 'matches?'
        active_fixtures = self.request(fixtures_url,)['data']
        return self._this_league_only(self.id_league, active_fixtures)

    def _get_commentary_for_fixture(self, fixture_id):
        # TODO class requires competition ID but this method doesn't.
        # Would be useful to be able to call this method without
        # instantiating the class with a competition ID. Stop-gap
        # solution is to allow class instantiated with competition=None.
        commentary_url = 'commentaries/{}?'.format(fixture_id)
        commentary = self.request(commentary_url)
        return commentary

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
                'lineups': {
                    'lineup_home': self._get_lineup_from_commentary('localteam', f['commentary']),
                    'lineup_away': self._get_lineup_from_commentary('visitorteam', f['commentary']),
                },
                'id': f['id'],
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

    def _get_lineup_from_commentary(self, team, commentary):
        return commentary['lineup'][team]

    def _format_fixture_score(self, fixture):
        home_score = fixture['localteam_score']
        away_score = fixture['visitorteam_score']
        if home_score == '?' and away_score == '?':
            # score = self._format_fixture_time(fixture['time'])
            score = self._format_fixture_time(fixture)
        else:
            score = '{} - {}'.format(home_score, away_score)
        return score

    def _format_fixture_time(self, fixture):
        ''' API returns dates in UTC timezone so convert to local timezone (i.e UK).

        Date seems to need to be involved otherwise there's a bug (?)
        where changing the timezone offsets the minutes rather than
        hours.
        '''
        f_date = dt.datetime.strptime(fixture['formatted_date'], self.date_format)
        f_time = dt.datetime.strptime(fixture['time'], self.time_format).time()
        dt_ = dt.datetime.combine(f_date, f_time)
        utc_time = pytz.utc.localize(dt_)
        local_tz = pytz.timezone('Europe/London')
        local_time = utc_time.astimezone(local_tz)
        return local_time.strftime('%H:%M')

    def _this_league_only(self, league_id, matches):
        return [m for m in matches if m['comp_id'] == league_id]

    def _is_valid_response(self, response):
        try:
            assert isinstance(response, dict) and response['status'] == 'error'
            if 'There are no matches at the moment' in response['message']:
                raise NoFixturesToday()
            elif 'We did not find commentaries' in response['message']:
                raise NoCommentaryAvailable()
            else:
                return False
        except (AssertionError, KeyError):
            return True


if __name__ == '__main__':
    start_logging()
    fa = FootballAPI()
    #print (fa.page_ready_todays_fixtures())
    print(fa.page_ready_finished_fixtures(date(year=2017, month=4, day=15)))
