from footballAPI.config.sql_alchemy.tables import *

leagues_spec = {
			"table_name": "leagues",
			"schema": "info",
			"columns": [
					Column('league_id', INT, primary_key=True, autoincrement=False),
					Column('name', VARCHAR(100)),
					Column('type', VARCHAR(30)),
					Column('country', VARCHAR(30)),
					Column('country_code', CHAR(3)),
					Column('season', INT),
					Column('season_start', DATE),
					Column('season_end', DATE),
					Column('standings', INT),
					Column('is_current', INT),
					Column('standings_coverage', Boolean),
					Column('fixture_events', Boolean),
					Column('fixture_lineups', Boolean),
					Column('fixture_statistics', Boolean),
					Column('fixture_player_statistics', Boolean),
					Column('players', Boolean),
					Column('topScorers', Boolean),
					Column('predictions', Boolean),
					Column('odds', Boolean)
				]
		}
