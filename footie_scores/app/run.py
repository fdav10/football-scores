''' Make webpage from API requests '''

import datetime as dt

from flask import Flask, render_template, request

from footie_scores import settings
from footie_scores.utils.log import start_logging
from footie_scores import db
import footie_scores.db.interface as queries
import footie_scores.league_manager as api_interface


app = Flask(__name__)
DATEFORMAT = "%A %d %B %y" # e.g. Sunday 16 April 2017
TODAY = dt.date.strftime(dt.date.today(), db.date_format)
YESTERDAY = dt.date.strftime(dt.date.today() - dt.timedelta(days=1), db.date_format)
COMPS_FOR_PAGE = settings.MAIN_COMPS


@app.route("/test")
def test():
    return "It worked!"


@app.route("/todays_games")
def todays_fixtures():
    comps = page_comps_only(queries.get_competitions())
    comp_ids = [c['api_id'] for c in comps]
    unsorted_fixtures = queries.get_fixtures_by_date(YESTERDAY, comp_ids)
    fixtures = sort_fixtures_by_competition(unsorted_fixtures)
    return games_template(fixtures, dt.date.today())


@app.route("/details_<fixture_id>")
def match_details(fixture_id):
    fixture = api_interface.retrieve_fixture_from_db(fixture_id)
    return details_template(fixture)


def games_template(competitions, date_):
    return render_template(
        'scores.html',
        date=date_.strftime(DATEFORMAT),
        competitions=competitions,
    )


def details_template(fixture):
    return render_template(
        'details.html',
        fixture=fixture,
    )


def page_comps_only(competitions):
    to_keep = COMPS_FOR_PAGE
    return [comp for comp in competitions if comp['api_id'] in to_keep]


def sort_fixtures_by_competition(fixtures):
    sorted_fixtures = []
    comp_ids = set([f['competition_id'] for f in fixtures])
    for id_ in comp_ids:
        sorted_fixtures.append({
            'name': id_,
            'fixtures': [fix for fix in fixtures if fix['competition_id'] == id_]
        })
    return sorted_fixtures


if __name__ == '__main__':
    start_logging()
    app.run()
