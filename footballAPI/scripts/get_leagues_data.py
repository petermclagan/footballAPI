from footballAPI.scripts import *
from footballAPI.config.sql_alchemy.tables.leagues import leagues_spec

assert 'leagues' in API_SCHEMAS.keys(), "leagues schema is required for validation"


def extract_leagues_row(data: Dict) -> Tuple:
	"""
	Extracts a row of leagues data and formats into a tuple.
	data: The json data to extract
	"""
	row = (
			data['league_id'],
			data['name'],
			data['type'],
			data['country'],
			data['country_code'],
			data['season'],
			data['season_start'],
			data['season_end'],
			data['standings'],
			data['is_current'],
			data['coverage']['standings'],
			data['coverage']['fixtures']['events'],
			data['coverage']['fixtures']['lineups'],
			data['coverage']['fixtures']['statistics'],
			data['coverage']['fixtures']['players_statistics'],
			data['coverage']['players'],
			data['coverage']['topScorers'],
			data['coverage']['predictions'],
			data['coverage']['odds']
			)
	assert len(row) == 19, f"Expected 19 columns, only have {len(row)}" 
	return row


if __name__ == '__main__':
	validate_schema('leagues')
	leagues_schema = API_SCHEMAS['leagues']

	leagues_table = football_alchemy.table(table_spec=leagues_spec)

	try:
		football_alchemy.create_schema(schema_name='info', execute=True)
	except ProgrammingError:
		logger.warning("Schema info already exists")

	football_alchemy.create_tables(table_list=[leagues_table])

	data = api_football.get(endpoint_url='leagues',
					        expected_schema=leagues_schema)
	
	total_results = data['api']['results']
	logger.info(f"There are {total_results} total leagues")
	leagues_data = data['api']['leagues']
	assert len(leagues_data) == total_results, f"Expected {total_results} leagues, obtained {len(leagues_data)}"

	rows_to_insert = list()
	for league_data in leagues_data:
		row = extract_leagues_row(league_data)
		rows_to_insert.append(row)

	# Insert rows in chunks of 50
	for chunk in list(batch_rows(rows_to_insert)):
		football_alchemy.insert_values(table=leagues_table,
							  		   values=chunk,
							           execute=True)
