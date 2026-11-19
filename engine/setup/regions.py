"""Countries that setup can select without a US state map download.

Sweden uses the library's own base map. Street-address search for Sweden is not in the
published state indexes, so choosing it sends no map and no address index.
"""

COUNTRIES = {
    'SE': {'id': 'SE', 'title': 'Sweden'},
}


def country(region_id):
    return COUNTRIES.get(region_id)
