''' Make webpage from API requests '''

from datetime import date

from flask import Flask, render_template

from footie_scores.league_manager import competition_fixtures
from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.apis.football_data import FootballData


app = Flask(__name__)
DATEFORMAT = "%A %d %B %y" # e.g. Sunday 16 April 2017
DEFAULT_COMPETITIONS = (
    'champions league',
    'europa league',
    'england cup',
    'england',
    'france',
    'germany',
    'italy',
    'portugal',
    'spain',
    )


@app.route("/test")
def test():
    return "It worked!"


@app.route("/todays_games")
def todays_fixtures():
    fixtures = competition_fixtures(DEFAULT_COMPETITIONS)
    return games_template(fixtures, date.today())

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


if __name__ == '__main__':
    start_logging()
    app.run()
