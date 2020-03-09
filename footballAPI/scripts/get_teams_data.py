from footballAPI.scripts import *
from footballAPI.config.sql_alchemy.tables.teams import teams_spec


def extract_team_row(data: Dict) -> Tuple:
	row = (
		data['team_id'],
		data['name'],
		data['code'],
		data['is_national'],
		data['country'],
		data['founded'],
		data['venue_name'],
		data['venue_surface'],
		data['venue_address'],
		data['venue_city'],
		data['venue_capacity']
		)
	return row


if __name__ == '__main__':
	validate_schema('teams')
	teams_schema = API_SCHEMAS['teams']

	teams_table = football_alchemy.table(table_spec=teams_spec)

	try:
		football_alchemy.create_schema(schema_name='teams', execute=True)
	except ProgrammingError:
		logger.warning("Schema teams already exists")

	football_alchemy.create_tables(table_list=[teams_table])

	league_ids = USER_PREFERENCES.get('leagues')
	if league_ids:
		logger.info(f"Found {len(league_ids)} league_ids in preferences.")
	else:
		logger.warning("Getting league all league ids from info.leagues")
		league_ids = list(get_league_ids)
		logger.warning(f"This will result in {len(league_ids)} credits. Will proceed in 10 seconds")
		cancel_counter()

	for league_id in league_ids:
		existing_pks = get_current_pk(table=teams_table)
		
		data = api_football.get(endpoint_url=f'teams/league/{league_id}',
						        expected_schema=teams_schema)

		total_results = data['api']['results']
		logger.info(f"There are {total_results} total teams for league {league_id}")
		teams_data = data['api']['teams']
		assert len(teams_data) == total_results, f"Expected {total_results} teams, obtained {len(teams_data)}"

		rows_to_insert = list()
		for team_data in teams_data:
			row = extract_team_row(team_data)
			if not row[0] in existing_pks:
				rows_to_insert.append(row)

		# Insert rows in chunks of 50
		for chunk in list(batch_rows(rows_to_insert)):
			football_alchemy.insert_values(table=teams_table,
								  		   values=chunk,
								           execute=True)