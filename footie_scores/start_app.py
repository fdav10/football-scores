''' Module to start and run the web app '''

from footie_scores.utils.log import start_logging
from footie_scores.app.run import app

start_logging()
app.run()
