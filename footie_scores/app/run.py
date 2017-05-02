''' Make webpage from API requests '''

from datetime import date

from flask import Flask, render_template, request

from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.apis.football_data import FootballData
import footie_scores.league_manager as api_interface


app = Flask(__name__)
DATEFORMAT = "%A %d %B %y" # e.g. Sunday 16 April 2017


@app.route("/test")
def test():
    return "It worked!"


@app.route("/todays_games")
def todays_fixtures():
    # TODO active fixtures are sometimes shown as not yet kicked off
    fixtures = api_interface.retrieve_fixtures_from_cache()
    return games_template(fixtures, date.today())


@app.route("/details_<fixture_id>")
def match_details(fixture_id):
    fixture = api_interface.retrieve_fixture_from_cache(fixture_id)
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


if __name__ == '__main__':
    start_logging()
    app.run()
