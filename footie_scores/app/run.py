''' Make webpage from API requests '''


from flask import Flask, render_template

from footie_scores.utils.utilities import start_logging
from footie_scores.apis.api_request import SoccerSportsOpenData as SSOD


app = Flask(__name__)


@app.route("/test")
def test():
    return "It worked!"


@app.route("/scores")
def todays_fixtures():
    premier_league = SSOD(id_league='premier-league', id_season='16-17')
    pl_games = premier_league.todays_fixtures_page_ready()

    return render_template(
        'scores.html',
        date='today',
        games=pl_games,
    )


if __name__ == '__main__':
    start_logging()
    app.run()
