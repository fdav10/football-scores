''' Make webpage from API requests '''

import datetime as dt

from flask import Flask, render_template, request

from footie_scores import settings
from footie_scores.utils.log import start_logging
from footie_scores import db
import footie_scores.db.interface as queries
import footie_scores.league_manager as api_interface


app = Flask(__name__)
WEBDATEFORMAT = "%A %d %B %y" # e.g. Sunday 16 April 2017
TODAY = dt.date.strftime(dt.date.today(), db.date_format)
YESTERDAY = dt.date.strftime(dt.date.today() - dt.timedelta(days=1), db.date_format)
COMPS_FOR_PAGE = settings.COMPS


@app.route("/test")
def test():
    return "It worked!"


@app.route("/todays_games")
def todays_fixtures():
    # TODO make details link appear only if lineups etc. are available for fixture
    with db.session_scope() as session:
        comps = page_comps_only(queries.get_competitions(session))
        comp_ids = [c.api_id for c in comps]
        fixtures = queries.get_fixtures_by_date(session, TODAY, comp_ids)
        todays_games = games_template(fixtures, dt.date.today())
    return todays_games


@app.route("/details_<fixture_id>")
def match_details(fixture_id):
    with db.session_scope() as session:
        fixture = queries.get_fixture_by_id(session, fixture_id)
        template = details_template(fixture)
    return template 


def games_template(competitions, date_):
    return render_template(
        'scores.html',
        date=date_.strftime(WEBDATEFORMAT),
        competitions=competitions,
    )


def details_template(fixture):
    return render_template(
        'details.html',
        fixture=fixture,
    )


def page_comps_only(competitions):
    to_keep = COMPS_FOR_PAGE
    return [comp for comp in competitions if comp.api_id in to_keep]
