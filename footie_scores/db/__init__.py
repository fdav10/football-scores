import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)

engine = create_engine('sqlite:///footie_scores/db/fs.db', echo=True)
Session = sessionmaker(bind=engine)

date_format = '%d.%m.%Y'
time_format = '%H:%M'


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
