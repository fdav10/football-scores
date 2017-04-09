''' Make webpage from API requests '''


from flask import Flask, render_template

from api_request import get_todays_fixtures


app = Flask(__name__)


@app.route("/test")
def test():
    return "It worked!"


@app.route("/scores")
def todays_fixtures():
    fixtures = get_todays_fixtures()
    return render_template(
        'scores.html',
        date='today',
        fixtures=fixtures,
    )


if __name__ == '__main__':
    app.run()
