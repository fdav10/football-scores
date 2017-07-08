#!/usr/bin/env python

''' Make webpage from API requests '''

import datetime as dt

from flask import Flask, render_template, request

from footie_scores import settings, db, utils
from footie_scores.utils.log import start_logging
from footie_scores.db import queries
from footie_scores.interfaces import db_to_web


app = Flask(__name__)
WEBDATEFORMAT = "%A %d %B %y" # e.g. Sunday 16 April 2017
TODAY = utils.time.today()
THIS_YEAR = TODAY.year
COMPS_FOR_PAGE = settings.COMPS


@app.route("/todays_games")
def todays_fixtures():
    with db.session_scope() as session:
        all_comps = db_to_web.get_competitions_by_id(session, COMPS_FOR_PAGE)
        fixtures = db_to_web.get_comp_grouped_fixtures(session, TODAY, COMPS_FOR_PAGE)
        comps_with_games = [f['name'] for f in fixtures if f['fixtures']]
        web_date = utils.time.custom_strftime(settings.WEB_DATEFORMAT_SHORT, TODAY)
        todays_games = games_template(
            'scores.html',
            all_comps,
            fixtures,
            utils.time.today(),
            'Live Scores - ' + web_date,
            competitions_with_games_today=comps_with_games,
        )
    return todays_games


@app.route("/past_results_<comp_id>_<month_index>")
def past_results(comp_id, month_index=TODAY.month):

    start_day = dt.date(year=THIS_YEAR, month=int(month_index), day=1)
    end_day = (dt.date(year=THIS_YEAR, month=int(month_index) % 12 + 1, day=1)
               - dt.timedelta(days=1))

    with db.session_scope() as session:
        fixtures_today = db_to_web.get_comp_grouped_fixtures(session, TODAY, COMPS_FOR_PAGE)
        comps_with_games = [f['name'] for f in fixtures_today if f['fixtures']]
        all_comps = db_to_web.get_competitions_by_id(session, COMPS_FOR_PAGE)
        selected_comp = db_to_web.get_competition_by_id(session, int(comp_id))
        fixtures = db_to_web.get_date_grouped_fixtures(session, start_day, int(comp_id), end_day)
        past_games = games_template(
            'fixtures_results.html',
            all_comps,
            fixtures,
            utils.time.today(),
            selected_comp.name + ' - Results / Fixtures',
            comp_id,
            comps_with_games)
    return past_games


@app.route("/details_<fixture_id>")
def match_details(fixture_id):
    with db.session_scope() as session:
        fixture = queries.get_fixture_by_id(session, fixture_id)
        lineups = fixture.lineups
        template = details_template(fixture, lineups)
    return template 


def games_template(
        template, page_competitions, grouped_fixtures, date_, title,
        comp_id='', competitions_with_games_today=None,
        ):

    options = {
        'fixtures_results.html': {
            'display_todays_games_sublist': 'none',
            'display_results_sublist': 'block',
            'games_today_filter': False,
            'games_today_link': True
        },
        'scores.html': {
            'display_todays_games_sublist': 'block',
            'display_results_sublist': 'none',
            'games_today_filter': True,
            'games_today_link': False
        }
    }

    display_todays_games_sublist = options[template]['display_todays_games_sublist']
    display_results_sublist = options[template]['display_results_sublist']
    games_today_filter = options[template]['games_today_filter']
    games_today_link = options[template]['games_today_link']

    return render_template(
        template,
        title=title,
        date=date_.strftime(WEBDATEFORMAT),
        competitions=page_competitions,
        competitions_with_games=competitions_with_games_today,
        grouped_fixtures=grouped_fixtures,
        comp_id=comp_id,
        games_today_filter=games_today_filter,
        games_today_link=games_today_link,
        todays_games_sublist_display=display_todays_games_sublist,
        past_results_sublist_display=display_results_sublist,
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
