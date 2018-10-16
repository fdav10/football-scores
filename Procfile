init: bin/init.sh
web: gunicorn footie_scores.webapp.run:app
worker: footie_scores/engine/updating.py