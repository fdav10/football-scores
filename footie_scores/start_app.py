''' Runs the web app '''

from multiprocessing import Process

from footie_scores.utils.log import start_logging
from footie_scores.app.run import app
from footie_scores.league_manager import start_api_calls 
from footie_scores.app import run


def main():
    ''' Run web app '''
    start_logging()
    web_app = Process(target=app.run)
    api_caller = Process(target=start_api_calls, args=(run.COMPETITIONS,))
    web_app.start()
    api_caller.start()


if __name__ == '__main__':
    main()
