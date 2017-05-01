''' Make webpage from API requests '''

from datetime import date

from flask import Flask, render_template, request

from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.apis.football_data import FootballData
from footie_scores.league_manager import retrieve_fixtures_from_cache


app = Flask(__name__)
DATEFORMAT = "%A %d %B %y" # e.g. Sunday 16 April 2017
COMPETITIONS = [
    {'api_name': 'champions league', 'print_name': 'Champions League'},
    {'api_name': 'europa league', 'print_name': 'Europa League'},
    {'api_name': 'england cup', 'print_name': 'FA Cup'},
    {'api_name': 'england', 'print_name': 'Premier League'},
    {'api_name': 'france', 'print_name': 'Ligue 1'},
    {'api_name': 'germany', 'print_name': 'Bundesliga'},
    {'api_name': 'italy', 'print_name': 'Serie A'},
    {'api_name': 'portugal', 'print_name': 'Primeira Liga'},
    {'api_name': 'spain', 'print_name': 'La Liga'},
]


@app.route("/test")
def test():

    return "It worked!"


@app.route("/todays_games")
def todays_fixtures():
    # TODO active fixtures are sometimes shown as not yet kicked off
    #fapi = FootballAPI()
    #fixtures = fapi.page_ready_todays_fixtures('france')
    fixtures = retrieve_fixtures_from_cache(COMPETITIONS)
    return games_template(fixtures, date.today())


@app.route("/details/<fixture_id>")
def match_details(fixture_id):
    fixture = request.args.get('fixture')
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
