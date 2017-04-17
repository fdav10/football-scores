''' Make webpage from API requests '''

from datetime import date

from flask import Flask, render_template

from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.apis.football_data import FootballData


app = Flask(__name__)
DATEFORMAT = "%A %d %B %y" # e.g. Sunday 16 April 2017


@app.route("/test")
def test():
    return "It worked!"


@app.route("/todays_games")
def todays_fixtures():
    premier_league = FootballAPI(id_league='1204')
    pl_games = premier_league.page_ready_todays_fixtures()

    return games_template(pl_games, date.today())


@app.route("/past_games")
def past_fixtures():
    date_ = date(year=2017, month=4, day=15)
    premier_league = FootballAPI(id_league='1204')
    pl_games = premier_league.page_ready_finished_fixtures(date_)

    return games_template(pl_games, date_)


def games_template(games, date_):
    return render_template(
        'scores.html',
        date=date_.strftime(DATEFORMAT),
        games=games,
    )


if __name__ == '__main__':
    start_logging()
    app.run()
