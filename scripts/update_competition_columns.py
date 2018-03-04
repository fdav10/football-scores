import logging

from footie_scores import constants
from footie_scores.db import queries
from footie_scores.db import session_scope
from footie_scores.utils.log import start_logging
from footie_scores.apis import response_merges
from footie_scores.maps import competition_map
from footie_scores.apis.football_api import FootballAPI
from footie_scores.apis.football_data import FootballData

from common import load_football_api_comps, load_football_data_comps
from common import api_get_football_api_comps, api_get_football_data_comps

logger = logging.getLogger(__name__)

start_logging()

API_DB_KEY_COL_MAP = {
    'short_name': 'shortcode',
    'n_teams': 'teams_in_competition',
    'n_fixtures': 'games_in_season'
}


def get_update_competitions():
    # fapi_comps = load_football_api_comps()
    # fdata_comps = load_football_data_comps()
    fapi_comps = api_get_football_api_comps()
    fdata_comps = api_get_football_data_comps(constants.ALL_COMPS)
    competitions = response_merges.merge_two_lists(
        fapi_comps,
        fdata_comps,
        id_map=competition_map['football-api_to_football-data'],
        consistent_keys=True)
    return competitions


def api_comps_id_match(api_comps, api_id):
    return (api_comp for api_comp in api_comps if api_comp['api_id'] == api_id)


def update_db_competitions(updated_comps):
    with session_scope() as session:
        db_comps = queries.get_competitions(session)
        for dbc in db_comps:
            try:
                api_comp = next(api_comps_id_match(updated_comps, dbc.api_id))
                print('Vars updated on {}'.format(dbc))
                for api_key, db_column in API_DB_KEY_COL_MAP.items():
                    setattr(dbc, db_column, api_comp.get(api_key))
                    print('\t{} on {} set to {}'.format(db_column, dbc, api_comp.get(api_key)))
            except StopIteration:
                pass
                # print('No id {} competion retrieved from APIs'.format(dbc.api_id))


def main():
    latest_comps = get_update_competitions()
    update_db_competitions(latest_comps)


if __name__ == '__main__':
    main()
