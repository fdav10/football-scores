import re
import json
import logging
import datetime as dt

import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base

from footie_scores import db, settings, utils


TIME_OVERRIDE = settings.OVERRIDE_DAY or settings.OVERRIDE_TIME
logger = logging.getLogger(__name__)
Base = declarative_base()


class _JsonEncodedDict(sqla.TypeDecorator):
    impl = sqla.String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


class Updatable():
    def __init__(self):
        self.atts_to_update = []

    def update_from_equivalent(self, equivalent):
        changed = False
        for name in self.atts_to_update:
            old = getattr(self, name)
            new = getattr(equivalent, name)
            if old != new:
                logger.info('%s: %s updated. was: %s, now: %s', self, name, old, new)
                changed = True
            setattr(self, name, getattr(equivalent, name))
        return changed


class Competition(Base):
    __tablename__ = 'competitions'

    id = sqla.Column(sqla.Integer, primary_key=True)
    api_id = sqla.Column(sqla.Integer)
    name = sqla.Column(sqla.String)
    region = sqla.Column(sqla.String)
    fixtures = sqla.orm.relationship('Fixture', back_populates='competition')
    games_in_season = sqla.Column(sqla.Integer)
    teams_in_competition = sqla.Column(sqla.Integer)
    shortcode =  sqla.Column(sqla.String)
    start_date = sqla.Column(sqla.Date)
    end_date = sqla.Column(sqla.Date)

    def __init__(self, api_id, name, region, **kwargs):
        self.api_id = api_id
        self.name = name
        self.region = region
        self.print_name = None

    def __repr__(self):
        return "<Competition(%s %s (api id %s) (db id %s))>" %(
            self.region, self.name, self.api_id, self.id)


class Team(Base):
    __tablename__ = 'teams'

    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.String)
    short_name = sqla.Column(sqla.String)
    api_id = sqla.Column(sqla.Integer)

    def __init__(self, team_name, short_name, api_id):
        self.name = team_name
        self.short_name = short_name
        self.api_id = api_id


class Lineups(Base, Updatable):
    # TODO make name singular
    __tablename__ = 'lineups'

    id = sqla.Column(sqla.Integer, primary_key=True)
    api_fixture_id = sqla.Column(sqla.String)
    home = sqla.Column(_JsonEncodedDict)
    away = sqla.Column(_JsonEncodedDict)
    home_subs = sqla.Column(_JsonEncodedDict)
    away_subs = sqla.Column(_JsonEncodedDict)

    fixture_id = sqla.Column(sqla.Integer, sqla.ForeignKey('fixtures.id'))
    fixture = sqla.orm.relationship('Fixture', back_populates='lineups')

    atts_to_update = ('home', 'away')

    def __init__(self, api_fixture_id, home_lineup, away_lineup, home_subs, away_subs):
        self.api_fixture_id = api_fixture_id
        self.home = home_lineup
        self.away = away_lineup
        self.home_subs = home_subs
        self.away_subs = away_subs

    def is_complete(self):
        return all((self.home, self.away, self.home_subs, self.away_subs))

    def is_partially_complete(self):
        return any((self.home, self.away))

    def __repr__(self):
        return "<Lineups for {}>".format(self.fixture.short_repr())


class Fixture(Base, Updatable):
    # TODO lineups, players, events can be stored as own table
    __tablename__ = 'fixtures'

    id = sqla.Column(sqla.Integer, primary_key=True)
    date = sqla.Column(sqla.Date)
    time = sqla.Column(sqla.Time)
    team_home = sqla.Column(sqla.String)
    team_away = sqla.Column(sqla.String)
    score = sqla.Column(sqla.String)
    comp_api_id = sqla.Column(sqla.Integer)
    api_fixture_id = sqla.Column(sqla.String)
    events = sqla.Column(_JsonEncodedDict)
    status = sqla.Column(sqla.String)

    lineups = sqla.orm.relationship('Lineups', uselist=False, back_populates='fixture')

    competition_id = sqla.Column(sqla.Integer, sqla.ForeignKey('competitions.id'))
    competition = sqla.orm.relationship(
        'Competition',
        back_populates='fixtures')

    atts_to_update = ('team_home', 'team_away', 'score', 'events', 'status', 'date', 'time')
    date_format = settings.DB_DATEFORMAT
    time_format = settings.DB_TIMEFORMAT
    datetime_format = settings.DB_DATETIMEFORMAT

    def __init__(self, team_home, team_away, comp_api_id,
                 api_fixture_id, score, date, time, status,
                 events=None):

        self.team_home = team_home
        self.team_away = team_away
        self.comp_api_id = comp_api_id
        self.api_fixture_id = api_fixture_id
        self.score = score
        self.date = date

        # TODO think about what to do here 
        if not isinstance(time, str):
            self.time = time
        else:
            self.stime = time

        self.status = status
        if events:
            self.events = events
        self.lineups = None


    def __repr__(self):
        sdate = self.date.strftime(self.date_format)
        if self.time:
            stime = self.time.strftime(self.time_format)
        else:
            try:
                stime = self.stime
            except:
                stime = 'Err'
        return "<Fixture(%s vs %s on %s at %s id %s)>" %(
            self.team_home, self.team_away, sdate, stime, self.api_fixture_id)

    def short_repr(self):
        # return "<Fixture(%s vs %s)>" %(self.team_home, self.team_away)
        return "{} vs {}".format(self.team_home, self.team_away)

    def is_active(self):
        timer_re = re.compile(r'\d+$')
        if TIME_OVERRIDE:
            return self.status in ('HT', 'Pen', 'ET', 'FT') or timer_re.match(self.status)
        else:
            return self.status in ('HT', 'Pen', 'ET') or timer_re.match(self.status)

    def has_lineups(self):
        if not self.lineups:
            return False
        return self.lineups.is_complete()

    def time_to_kickoff(self):
        tz = dt.timezone.utc
        kick_off_time = dt.datetime.combine(self.date, self.time, tzinfo=tz)
        timedelta_to_kickoff = kick_off_time - utils.time.now()
        return timedelta_to_kickoff.total_seconds()

    def kicks_off_within(self, seconds_from_now):
        return 0. < self.time_to_kickoff() <= seconds_from_now

    def to_python(self):
        keys = ['team_home', 'team_away', 'score', 'events', 'status', 'api_fixture_id']
        try:
            getattr(self, 'override_score')
            keys += ['override_score', 'override_status', 'override_events']
        except AttributeError:
            pass
        return {k: getattr(self, k) for k in keys}


def create_db():
    Base.metadata.create_all(db.engine)


def drop_tables():
    Base.metadata.drop_all(db.engine)


def drop_table(table):
    table.__table__.drop(db.engine)
