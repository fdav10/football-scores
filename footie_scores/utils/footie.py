
def score_from_events(events):
    home_goals = len([e for e in events['home'] if e['type'] == 'goal'])
    away_goals = len([e for e in events['away'] if e['type'] == 'goal'])
    score = ' - '.join((str(home_goals), str(away_goals)))
    return score

