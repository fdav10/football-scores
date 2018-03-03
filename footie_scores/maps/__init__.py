import json, os

_dir = os.path.split(__file__)[0]

competition_map = json.load(open(os.path.join(_dir, 'competitions.json')))
