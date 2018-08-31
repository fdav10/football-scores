""" Start the updating process.

Monitors APIs and updates scores when
fixtures are active"""

from footie_scores.utils.log import start_logging, log_list
from footie_scores.engine.updating import start_updater


start_logging()
start_updater()
