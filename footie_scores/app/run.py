''' Make webpage from API requests '''

from datetime import date

from flask import Flask, render_template

from footie_scores.league_manager import competition_fixtures
from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.apis.football_data import FootballData


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
    fixtures = competition_fixtures(COMPETITIONS)
    return games_template(fixtures, date.today())

@app.route("/details/<fixture_id>")
def match_details(fixture_id):
    fixture_details = FootballAPI().page_ready_fixture_details(fixture_id)
    return details_template(fixture_details)

@app.route("/prem")
def prem_fixtures():
    date_ = date(year=2017, month=4, day=15)
    premier_league = FootballAPI('england')
    pl_games = premier_league.page_ready_finished_fixtures(date_)
    return games_template(pl_games, date_)


def games_template(competitions, date_):
    return render_template(
        'scores.html',
        date=date_.strftime(DATEFORMAT),
        competitions=competitions,
    )


def details_template(details):
    return render_template(
        'details.html',
        details=details,
    )


if __name__ == '__main__':
    start_logging()
    app.run()
