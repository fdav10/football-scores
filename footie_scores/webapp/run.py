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
TODAY = utils.time.today()
THIS_YEAR = TODAY.year
COMPS_FOR_PAGE = settings.COMPS


@app.route("/todays_games")
def todays_fixtures():
    with db.session_scope() as session:
        comps = page_comps_only(queries.get_competitions(session))
        comp_ids = [c.api_id for c in comps]
        fixtures = queries.get_comp_grouped_fixtures_for_date(session, TODAY, comp_ids)
        todays_games = games_template(
            fixtures,
            utils.time.today(),
            'Games Today',
            games_today_as_filter=True,
            games_today_as_link=False,
        )
    return todays_games


@app.route("/past_results_<comp_id>_<month_index>")
def past_results(comp_id, month_index=TODAY.month):

    start_day = dt.date(year=THIS_YEAR, month=int(month_index), day=1)
    end_day = (dt.date(year=THIS_YEAR, month=int(month_index) % 12 + 1, day=1)
               - dt.timedelta(days=1))

    with db.session_scope() as session:
        comps = page_comps_only(queries.get_competitions(session))
        comp_ids = [c.api_id for c in comps]
        selected_comp = next(c.name for c in comps if c.api_id == int(comp_id))
        fixtures = queries.get_comp_grouped_fixtures_for_date(session, start_day, comp_ids, end_day)
        for fixture in fixtures:
            if fixture['api_id'] != int(comp_id):
                fixture['display'] = False
            else:
                fixture['display'] = True
            past_games = games_template(
                fixtures,
                utils.time.today(),
                'Past Results - ' + selected_comp,
                comp_id)
    return past_games


@app.route("/details_<fixture_id>")
def match_details(fixture_id):
    with db.session_scope() as session:
        fixture = queries.get_fixture_by_id(session, fixture_id)
        lineups = fixture.lineups
        template = details_template(fixture, lineups)
    return template 


def games_template(competitions,
                   date_, 
                   title,
                   comp_id='',
                   games_today_as_filter=False,
                   games_today_as_link=True):

    return render_template(
        'scores.html',
        title=title,
        date=date_.strftime(WEBDATEFORMAT),
        competitions=competitions,
        comp_id=comp_id,
        games_today_filter=games_today_as_filter,
        games_today_link=games_today_as_link,
    )


def details_template(fixture, lineups):
    return render_template(
        'details.html',
        fixture=fixture,
        lineups=lineups,
    )


def page_comps_only(competitions):
    to_keep = COMPS_FOR_PAGE
    return filter_comps(competitions, to_keep)


def filter_comps(competitions, to_keep):
    return [comp for comp in competitions if comp.api_id in to_keep]
    


if __name__ == '__main__':
    start_logging()
    app.run(debug=settings.FLASK_DEBUG)
