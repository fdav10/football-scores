''' Runs the web app '''

from footie_scores.utils.log import start_logging
from footie_scores.app.run import app


def main():
    ''' Run web app '''
    start_logging()
    app.run()


if __name__ == '__main__':
    main()
