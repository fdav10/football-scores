''' Make webpage from API requests '''


from flask import Flask, render_template

from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.apis.football_data import FootballData


app = Flask(__name__)


@app.route("/test")
def test():
    return "It worked!"


@app.route("/scores")
def todays_fixtures():
    premier_league = FootballAPI(id_league='1204')
    pl_games = premier_league.page_ready_todays_fixtures()

    return render_template(
        'scores.html',
        date='today',
        games=pl_games,
    )


if __name__ == '__main__':
    start_logging()
    app.run()
