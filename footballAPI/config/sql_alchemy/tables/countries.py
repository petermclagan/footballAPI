from footballAPI.config.sql_alchemy.tables import *

countries_spec = {
		"table_name": "countries",
		"schema": "info",
		"columns": [
			Column("country", VARCHAR),
			Column("code", VARCHAR)
			]
	}