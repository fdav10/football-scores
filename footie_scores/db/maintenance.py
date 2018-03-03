

from footie_scores.db import session_scope
from footie_scores.db import queries
import queries
from footie_scores import settings 


log_template = '''
{comp_name}
{underline}
Number of fixtures in db: {n_db_fixtures}
Number of fixtures in season: {n_season_fixtures}
Completeness score: 0
'''


def check_fixtures_in_db(start_date, end_date, competitions):
    canonical_list = None
    bd_list = None


def log_db_status(competition_ids=settings.COMPS):
    status = {}
    with session_scope() as session:
        competitions = queries.get_competitions_by_id(session, competition_ids)
        for competition in competitions:
            status['n_db_fixtures'] = queries.count_fixtures_for_competition(
                session, competition.api_id)
            status['comp_name'] = competition.name
            status['n_season_fixtures'] = 0
            status['underline'] = '-' * len(competition.name)
            print(log_template.format(**status))


if __name__ == '__main__':
    log_db_status()
