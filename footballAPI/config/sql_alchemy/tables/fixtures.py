from footballAPI.config.sql_alchemy.tables import *

# Schema will be the country and will be dynamiclly added
fixtures_spec = {
	"table_name": "fixtures",
	"columns": [
		Column("fixture_id", INT, primary_key=True, autoincrement=False),
		Column("league_id", INT, ForeignKey("info.leagues.league_id"), nullable=False),
		Column("event_date", VARCHAR),
		Column("event_timestamp", INT),
		Column("firstHalfStart", INT),
		Column("secondHalfStart", INT),
		Column("round", VARCHAR),
		Column("status", VARCHAR),
		Column("statusShort", VARCHAR),
		Column("elapsed", INT),
		Column("venue", VARCHAR),
		Column("referee", VARCHAR),
		Column("home_team_id", INT, ForeignKey("teams.teams.team_id"), nullable=False),
		Column("away_team_id", INT, ForeignKey("teams.teams.team_id"), nullable=False),
		Column("goalsHomeTeam", INT),
		Column("goalsAwayTeam", INT),
		Column("score_HT", VARCHAR),
		Column("score_FT", VARCHAR),
		Column("score_ET", VARCHAR),
		Column("score_PEN", VARCHAR)
		]
}