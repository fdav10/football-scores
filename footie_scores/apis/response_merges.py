

def merge_two_lists(primary_response, secondary_response, id_map):
    '''Merge two lists containing formatted responses from different APIs

    primary_response : list
    secondary_response : list
    id_map : dict
        mapping object which maps ids of items in the first list to
        those in the second
    '''

    r2_lookup = {row['api_id']: row for row in secondary_response}
    ids1 = [f['api_id'] for f in primary_response]
    ids2 = [id_map.get(str(id_)) for id_ in ids1]
    items1 = [item for item in primary_response]
    items2 = [r2_lookup.get(id2, {}) for id2 in ids2]
    for item1, item2 in zip(items1, items2):
        item2.update(item1)
    merged = [item for item in items2]
    return merged
