''' '''

from datetime import date
from collections import defaultdict

from flask import Flask, render_template

from footie_scores.apis.football_api import FootballAPI

AVAILABLE_COMPETITIONS = set((
    'champions league',
    'europa league',
    'austria',
    'belgium',
    'czechoslovakia',
    'england cup',
    'england league cup',
    'england',
    'england 2nd',
    'france',
    'germany',
    'greece',
    'italy 2nd',
    'italy',
    'netherlands',
    'portugal',
    'spain cup',
    'spain',
    'switzerland',
    'turkey',
    'ukraine',
    'russia',
    ))



def competition_fixtures(competitions):
    fixtures = []
    for competition in competitions:
        comp_api = FootballAPI(competition['api_name'])
        try:
            comp_fixtures = comp_api.page_ready_todays_fixtures()
        except:
            # TODO catch custom error for no fixtures available
            comp_fixtures = []
        fixtures.append({
            'name': competition['print_name'],
            'fixtures': comp_fixtures
        })
    return fixtures
