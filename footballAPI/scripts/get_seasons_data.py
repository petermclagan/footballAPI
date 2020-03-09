from footballAPI.scripts import *
from footballAPI.config.sql_alchemy.tables.countries import countries_spec


def extract_countries_row(data: Dict) -> Tuple:
	row = (data['country'],
		   data['code'])
	return row


if __name__ == '__main__':
	validate_schema('countries')
	countries_schema = API_SCHEMAS['countries']

	countries_table = football_alchemy.table(table_spec=countries_spec)

	try:
		football_alchemy.create_schema(schema_name='info', execute=True)
	except ProgrammingError:
		logger.warning("Schema info already exists")

	football_alchemy.create_tables(table_list=[countries_table])

	data = api_football.get(endpoint_url='countries',
					        expected_schema=countries_schema)
	
	total_results = data['api']['results']
	logger.info(f"There are {total_results} total countries")
	countries_data = data['api']['countries']
	assert len(countries_data) == total_results, f"Expected {total_results} countries, obtained {len(countries_data)}"

	countries_codes_to_insert = list()
	for country in countries_data:
		row = extract_countries_row(country)
		countries_codes_to_insert.append(row)

	# Insert rows in chunks of 50
	for chunk in list(batch_rows(countries_codes_to_insert)):
		football_alchemy.insert_values(table=countries_table,
							  		   values=chunk,
							           execute=True)
