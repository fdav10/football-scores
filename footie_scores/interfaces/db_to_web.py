
import datetime as dt
from collections import defaultdict
import logging

from sqlalchemy import and_

from footie_scores import settings
from footie_scores import utils
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
    end_date = start_date if end_date is None else end_date
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
    end_date = start_date if end_date is None else end_date

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


def get_competitions_by_id(session, ids):
    return queries.get_competitions_by_id(session, ids)


def get_competition_by_id(session, id_):
    return queries.get_competition_by_id(session, id_)


def filter_fixtures_with_override_time(fixtures):
    return [filter_fixture_with_override_time(f) for f in fixtures]


def filter_fixture_with_override_time(fixture):
    f = fixture
    fixture_ko = dt.datetime.combine(f.date, f.time)
    minutes_elapsed = (utils.time.now() - fixture_ko).total_seconds() / 60
    gametime_elapsed = minutes_elapsed - (15 if minutes_elapsed > 45 else 0)
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
            f.override_score = ' - '.join(
                (str(len(f.override_events['home'])),
                str(len(f.override_events['away']))))

            # TODO this is unreliable, e.g. delayed games or games with ET
            f.override_status = int(gametime_elapsed) if gametime_elapsed <= 115 else 'FT'
            logger.info('%s vs %s: override score: %s, status: %s',
                        f.team_home, f.team_away, f.override_score, f.override_status)
    return fixture
