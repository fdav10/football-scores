init: bin/create_db
web: gunicorn footie_scores.webapp.run:app
worker: footie_scores/engine/updating.py