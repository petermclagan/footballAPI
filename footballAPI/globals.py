# Defined on https://www.api-football.com/documentation
BASE_ENDPOINTS = [
    'status',
    'timezone',
    'seasons',
    'countries',
    'leagues',
    'teams',
    'players',
    'leagueTable',
    'fixtures',
    'events',
    'lineups',
    'statistics',
    'predictions',
    'coachs',
    'transfers',
    'trophies',
    'sidelined',
    'odds',
    'match',
    'league_fixtures',
]

# These are custom created endpoints to make the user experience easier. 
CUSTOM_ENDPOINTS = {
    'match': 'fixtures/id/{fixture_id}',  # returns all data for a given fixture_id,
    'league_fixtures': 'fixtures/league/{league_id}',   # returns all fixtures for a given league_id
}

VALID_CUSTOM_IDS = [
    'fixture_id',
    'league_id',
]
