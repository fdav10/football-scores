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
    for competition_name in competitions:
        comp = FootballAPI(competition_name)
        try:
            comp_fixtures = comp.page_ready_todays_fixtures()
        except:
            comp_fixtures = []
        fixtures.append({
            'name': competition_name,
            'fixtures': comp_fixtures
        })
    return fixtures
