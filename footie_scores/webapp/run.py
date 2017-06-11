#!/usr/bin/env python

''' Make webpage from API requests '''

import datetime as dt

from flask import Flask, render_template, request

from footie_scores import settings, db, utils
from footie_scores.utils.log import start_logging
from footie_scores.db import queries
import footie_scores.engine.updating as api_interface


app = Flask(__name__)
WEBDATEFORMAT = "%A %d %B %y" # e.g. Sunday 16 April 2017
TODAY = dt.date.strftime(utils.time.today(), settings.DB_DATEFORMAT)
TODAY = utils.time.today()
COMPS_FOR_PAGE = settings.COMPS


@app.route("/todays_games")
def todays_fixtures():
    # TODO make details link appear only if lineups etc. are available for fixture
    with db.session_scope() as session:
        comps = page_comps_only(queries.get_competitions(session))
        comp_ids = [c.api_id for c in comps]
        fixtures = queries.get_comp_grouped_fixtures_for_date(session, TODAY, comp_ids)
        todays_games = games_template(fixtures, utils.time.today())
    return todays_games


@app.route("/details_<fixture_id>")
def match_details(fixture_id):
    with db.session_scope() as session:
        fixture = queries.get_fixture_by_id(session, fixture_id)
        lineups = fixture.lineups
        template = details_template(fixture, lineups)
    return template 


def games_template(competitions, date_):
    return render_template(
        'scores.html',
        date=date_.strftime(WEBDATEFORMAT),
        competitions=competitions,
    )


def details_template(fixture, lineups):
    return render_template(
        'details.html',
        fixture=fixture,
        lineups=lineups,
    )


def page_comps_only(competitions):
    to_keep = COMPS_FOR_PAGE
    return [comp for comp in competitions if comp.api_id in to_keep]


if __name__ == '__main__':
    start_logging()
    app.run()
