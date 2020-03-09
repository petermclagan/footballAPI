from footballAPI.config.sql_alchemy.tables import *

teams_spec = {
	"table_name": "teams",
	"schema": "teams",
	"columns": [
		Column("team_id", INT, primary_key=True, autoincrement=False),
		Column("name", VARCHAR, nullable=False),
		Column("code", VARCHAR),
		Column("is_national", Boolean),
		Column("country", VARCHAR),
		Column("founded", INT),
		Column("venue_name", VARCHAR),
		Column("venue_surface", VARCHAR),
		Column("venue_address", VARCHAR),
		Column("venue_city", VARCHAR),
		Column("venue_capacity", INT)
		]
}