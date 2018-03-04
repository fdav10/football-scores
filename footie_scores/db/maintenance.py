

from footie_scores.db import session_scope
from footie_scores.db import queries
import queries
from footie_scores import settings 


log_template = '''
{comp_name}
{underline}
Number of fixtures in db: {n_db_fixtures}
Number of fixtures in season: {n_season_fixtures}
Completeness score: {completeness:.1f}%
'''


def check_fixtures_in_db(start_date, end_date, competitions):
    canonical_list = None
    bd_list = None


def log_db_status(competition_ids=settings.COMPS):
    status = {}
    with session_scope() as session:
        competitions = queries.get_competitions_by_id(session, competition_ids)
        for competition in competitions:
            n_fixtures_in_db = queries.count_fixtures_for_competition(
                session, competition.api_id)
            n_fixtures_in_season = competition.games_in_season
            status['n_db_fixtures'] = n_fixtures_in_db
            status['comp_name'] = competition.name
            status['n_season_fixtures'] = n_fixtures_in_season
            status['underline'] = '-' * len(competition.name)
            if n_fixtures_in_season:
                status['completeness'] = n_fixtures_in_db / n_fixtures_in_season * 100
            else:
                status['completeness'] = 0
            print(log_template.format(**status))


if __name__ == '__main__':
    log_db_status()
