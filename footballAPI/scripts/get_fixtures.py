from datetime import datetime

from footballAPI.scripts import *
from footballAPI.config.sql_alchemy.tables.fixtures import fixtures_spec
from footballAPI.config.sql_alchemy.tables.leagues import leagues_spec

leagues_table = football_alchemy.table(leagues_spec)

today = datetime.now()

def get_league_ids() -> List[int]:
	"""
	Gets league ids either from config or table.
	Return: list of league ids
	"""
	league_ids = USER_PREFERENCES.get('leagues')
	if league_ids:
		logger.info(f"Found {len(league_ids)} league_ids in preferences.")
	else:
		logger.warning("Getting league all league ids from info.leagues")
		league_ids = list(get_league_ids)
		logger.warning(f"This will result in {len(league_ids)} credits. Will proceed in 10 seconds")
		cancel_counter()
	return league_ids


def get_country_from_leagueid(league_id: int) -> str:
	"""
	Gets the country name from the league id as the country will be the schema for each set of fixtures
	league_id: The league id to get the country for
	return: The country name
	"""
	session = football_alchemy.Session()
	country = session.query(leagues_table.c.country).filter(leagues_table.c.league_id==league_id).one()[0]
	assert country not in [None, ''], f"No country returned for league id {league_id}"
	return country


def get_countries() -> Set[str]:
	"""
	Gets all countries as a set from league ids
	return: List of all countries
	"""
		# Each country will have a different schema
	countries = set()
	for league_id in league_ids:
		country = get_country_from_leagueid(league_id)
		logger.info(f"Country for league id {league_id} is {country}")
		countries.add(country)
	return countries


def filter_league_ids(league_ids: List[int], fixtures_table: table) -> List[int]: 
	"""
	Filters out historic leagues with fixtures already available
	league_ids: The full list of league_ids
	return: The filtered list of ids
	"""
	# Get start_date and end_date
	filtered_league_ids = list()
	for league_id in league_ids:
		league_row = session.query(leagues_table).filter(leagues_table.c.league_id==league_id).one()
		season_start = league_row.season_start
		season_end = league_row.season_end
		
		if season_end <= today.date():
			logger.debug(f"Checking for historical data for league: {league_id}")
			historic_data = session.query(fixtures_table).filter(fixtures_table.c.league_id==league_id).all()
			if len(historic_data) > 0:
				logger.info(f"Already have data for league id: {league_id}")
			else:
				filtered_league_ids.append(league_id)

		elif season_start >= today.date() > season_end:
			logger.debug(f"Current season for league id: {league_id}")
			filtered_league_ids.append(league_id)

		else:
			pass
	return filtered_league_ids


def extract_fixture_row(data: Dict) -> Tuple:
	"""
	Extracts the data for a row for the fixtures table
	data: A dictionary containing all of the data from the API
	return: A tuple of the row extracted
	"""
	event_date = datetime.utcfromtimestamp(data['event_timestamp'])

	# Don't want games not yet completed'
	if data['statusShort'] != 'FT':
		row = None
	
	# Don't want future games
	elif event_date.date() >= today.date():
		row = None
	
	else:
		row = (data['fixture_id'],
			   data['league_id'],
			   data['event_date'],
			   data['event_timestamp'],
			   data['firstHalfStart'],
			   data['secondHalfStart'],
			   data['round'],
			   data['status'],
			   data['statusShort'],
			   data['elapsed'],
			   data['venue'],
			   data['referee'],
			   data['homeTeam']['team_id'],
			   data['awayTeam']['team_id'],
			   data['goalsHomeTeam'],
			   data['goalsAwayTeam'],
			   data['score']['halftime'],
			   data['score']['fulltime'],
			   data['score']['extratime'],
			   data['score']['penalty']
			   )
	return row

if __name__ == '__main__':
	validate_schema('fixtures')

	fixtures_schema = API_SCHEMAS['fixtures']

	league_ids = get_league_ids()

	countries = get_countries()

	for country in countries:
		country_fixtures_spec = fixtures_spec.copy()
		country_fixtures_spec['schema'] = country
		logger.debug("Reflecting sqlalchemy metadata")
		football_alchemy.reflect("info")
		football_alchemy.reflect("teams")
		fixtures_table = football_alchemy.table(table_spec=country_fixtures_spec)

		try:
			football_alchemy.create_schema(schema_name=country, execute=True)
		except ProgrammingError:
			logger.warning("Schema fixtures already exists")

		football_alchemy.create_tables(table_list=[fixtures_table])

		filtered_league_ids = filter_league_ids(league_ids=league_ids,
						  					    fixtures_table=fixtures_table)
		for league_id in filtered_league_ids:
			existing_pks = get_current_pk(table=fixtures_table)
			data = api_football.get(endpoint_url=f'fixtures/league/{league_id}',
									expected_schema=fixtures_schema)
			total_results = data['api']['results']
			logger.info(f"There are {total_results} total fixtures for league {league_id}")
			fixtures_data = data['api']['fixtures']
			assert len(fixtures_data) == total_results, f"""
				Expected {total_results} fixtures, obtained {len(fixtures_data)}"""

			rows_to_insert = list()
			for fixture_data in fixtures_data:
				row = extract_fixture_row(fixture_data)
				if existing_pks:
					if not row[0] in existing_pks:
						rows_to_insert.append(row)
				else:
					rows_to_insert.append(row)

			# Insert rows in chunks of 50
			for chunk in list(batch_rows(rows_to_insert)):
				football_alchemy.insert_values(table=fixtures_table,
									  		   values=chunk,
									           execute=True)
