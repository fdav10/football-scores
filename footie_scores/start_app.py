#!/usr/bin/env python

''' Runs the web app '''

from multiprocessing import Process

from footie_scores import db, settings
from footie_scores.utils.log import start_logging
from footie_scores.app.run import app
from footie_scores import league_manager


def main():
    ''' Start web app and scores updater '''
    web_app = Process(target=app.run, kwargs={'debug': settings.FLASK_DEBUG})
    api_caller = Process(target=league_manager.main, args=())
    web_app.start()
    api_caller.start()


def start_web_app():
    app.run(debug=settings.FLASK_DEBUG)


def start_api_caller():
    league_manager.main()


if __name__ == '__main__':
    start_logging()
    # start_web_app()
    # start_api_caller()
    main()
