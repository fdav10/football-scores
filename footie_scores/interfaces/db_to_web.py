
import datetime as dt
from collections import defaultdict
from itertools import chain
import logging
from difflib import get_close_matches, SequenceMatcher

from sqlalchemy import and_

from footie_scores import settings
from footie_scores import utils
from footie_scores.utils.footie import score_from_events
from footie_scores.utils.generic import query_list_of_dicts
from footie_scores.db import queries
from footie_scores.db.schema import Competition, Fixture


logger = logging.getLogger(__name__)
TIME_OVERRIDE = settings.OVERRIDE_TIME or settings.OVERRIDE_DAY


def get_fixture_by_id(session, id_):
    fixture = queries.get_fixture_by_id(session, id_)
    if TIME_OVERRIDE:
        fixture = filter_fixture_with_override_time(fixture)
    return fixture


def get_comp_grouped_fixtures(
        session, start_date, comp_ids=settings.COMPS, end_date=None):

    grouped_fixtures = []
    for id_ in comp_ids:
        competition = queries.get_competition_by_id(session, id_)
        fixtures = queries.get_fixtures_by_date_and_comp(session, start_date, id_, end_date)
        if TIME_OVERRIDE:
            fixtures = filter_fixtures_with_override_time(fixtures)
        grouped_fixtures.append({'name': competition.name,
                                 'fixtures': fixtures})
    return grouped_fixtures


def get_date_grouped_fixtures(
        session, start_date, comp_id, end_date=None):

    grouped_fixtures = []
    date_keyed_dict = defaultdict(list)

    fixtures = queries.get_fixtures_by_date_and_comp(session, start_date, comp_id, end_date)
    if TIME_OVERRIDE:
        fixtures = filter_fixtures_with_override_time(fixtures)
    for fixture in fixtures:
        date_keyed_dict[fixture.date].append(fixture)

    for date, fixtures in date_keyed_dict.items():
        web_format_time = utils.time.custom_strftime(settings.WEB_DATEFORMAT, date)
        grouped_fixtures.append({'name': web_format_time,
                                 'fixtures': fixtures})

    return grouped_fixtures


def get_fixtures_by_dates_and_comps(
        session, start_date, comp_ids, end_date=None):

    fixtures = []
    for comp_id in comp_ids:
        fixtures.append(queries.get_fixtures_by_date_and_comp(
            session, start_date, comp_id, end_date))
    fixtures = list(chain(*fixtures))
    if TIME_OVERRIDE:
        return filter_fixtures_with_override_time(fixtures)
    return fixtures


def get_competitions_by_id(session, ids):
    return queries.get_competitions_by_id(session, ids)


def get_competition_by_id(session, id_):
    return queries.get_competition_by_id(session, id_)


def filter_fixtures_with_override_time(fixtures):
    return [filter_fixture_with_override_time(f) for f in fixtures]


def filter_fixture_with_override_time(fixture):
    f = fixture
    fixture_ko = dt.datetime.combine(f.date, f.time)
    mins_elapsed = (utils.time.now() - fixture_ko).total_seconds() / 60
    gametime_elapsed = mins_elapsed if mins_elapsed < 45 else 45 if mins_elapsed < 60 else mins_elapsed - 15
    time_filtered_events = {'home': [], 'away': []}

    if gametime_elapsed < 0:
        f.override_score = f.time.strftime(settings.DB_TIMEFORMAT)
        f.override_events = time_filtered_events
        f.override_status = ' '
    else:
        for team in ('home', 'away'):
            for event in f.events[team]:
                if gametime_elapsed >= int(event['time']):
                    time_filtered_events[team].append(event)
                else:
                    logger.info('%s vs %s: %s at %s filtered, override game time: %s',
                                f.team_home, f.team_away,
                                event['type'], event['time'], gametime_elapsed)

        if time_filtered_events != f.events or gametime_elapsed < 115:
            f.override_events = time_filtered_events
            home_goals = len([e for e in f.override_events['home'] if e['type'] == 'goal'])
            away_goals = len([e for e in f.override_events['away'] if e['type'] == 'goal'])
            f.override_score = ' - '.join((str(home_goals), str(away_goals)))

            # TODO this is unreliable, e.g. delayed games or games with ET
            f.override_status = int(gametime_elapsed) if gametime_elapsed <= 115 else 'FT'
            logger.info('%s vs %s: override score: %s, status: %s',
                        f.team_home, f.team_away, f.override_score, f.override_status)
    return fixture


def determine_substitutions(lineups, events):
    sides = ('home', 'away')
    for side in sides:
        lineup = getattr(lineups, side)
        subs = getattr(lineups, side+'_subs')
        sub_events = [e for e in events[side] if e['type'] == 'subst']
        for player in lineup:
            sub_event = query_list_of_dicts(
                sub_events,
                lookups=[('assist_id', player['id'], None),
                         ('assist', player['name'], None),
                         ('assist', player['name'], lambda x: x.lower().split()[-1]),
                         ('assist', player['name'], lambda x: x.lower().replace('\'', '').split()[-1]),
                ])
            if sub_event is None:
                player['subbed'] = None
            else:
                player['subbed'] = 'subbed_off'
                player['subst_event_string'] = '({}\')  \u2935'.format(sub_event['minute'])
            
        possible_names = [event['player'] for event in sub_events]
        for player in subs:
            sub_event = query_list_of_dicts(
                sub_events,
                lookups=[('player_id', player['id'], None),
                         ('player', player['name'], None),
                         ('player', player['name'], lambda x: x.split()[-1]),
                         ('player', player['name'], lambda x: x.lower().replace('\'', '').split()[-1]),
                         ('player', player['name'], lambda x: get_close_matches(x, possible_names, cutoff=0.4)),
                ])
            if sub_event is None:
                player['subbed'] = None
            else:
                player['subbed'] = 'subbed_on'
                player['subst_event_string'] = '({}\')  \u2934'.format(sub_event['minute'])
                sub_event_player, player = sub_event['player'], player['name']
                closeness = SequenceMatcher(None, sub_event_player, player).ratio()
                if closeness < 0.5:
                    logger.warning(
                        'Substitute {} from event paired with {} from subs list, closeness: {:.2f} which is a bit low'.format(
                        sub_event_player, player, SequenceMatcher(None, sub_event_player, player).ratio()))
        try:
            assert(len(sub_events) == len([p['subbed'] for p in lineup if p['subbed']]))
            assert(len(sub_events) == len([p['subbed'] for p in subs if p['subbed']]))
        except:
            logger.error('Number of subs not the same as number of sub events')

    return lineups
