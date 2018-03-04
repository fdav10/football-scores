

def merge_two_lists(primary_response, secondary_response, id_map, ensure_keys=False):
    '''Merge two lists containing formatted responses from different
    football APIs.

    primary_response : list
    secondary_response : list
    id_map : dict
        mapping object which maps ids of items in the first list to
        those in the second
    ensure_keys : bool
        if True ensure all instances of the resulting merged
        dictionaries have the same keys, else some items may have
        fewer keys due to there not being a one-to-one relationship
        between items in the two response lists.
    '''

    r2_lookup = {row['api_id']: row for row in secondary_response}
    ids1 = [f['api_id'] for f in primary_response]
    ids2 = [id_map.get(str(id_)) for id_ in ids1]
    secondary_response = [r2_lookup.get(id2, {}) for id2 in ids2]
    if ensure_keys:
        keys = next((k.keys() for k in secondary_response if k != {}))
        secondary_response = [d if d != {} else dict.fromkeys(keys) for d in secondary_response]
    for item1, item2 in zip(primary_response, secondary_response):
        item2.update(item1)
    return [item for item in secondary_response]
