import pandas as pd

from footballAPI import LeagueTable


class TestLeagueTable:
    def setup_class(self):
        self.league_table = LeagueTable(
            country="England",
            league="Premier League",
            season=2015
        )

    def test_set_league_id(self):
        assert self.league_table.league_id == 696

    def test_valid_league_fixtures(self):
        assert len(self.league_table.ft_fixtures.index == 380)

    def test_determine_points_home_win(self):
        assert self.league_table._determine_points(fixture_id=1, home_goals=5, away_goals=1) == {
            "fixture_id": 1, "home_points": 3, "away_points": 0
        }

    def test_determine_points_away_win(self):
        assert self.league_table._determine_points(fixture_id=1, home_goals=0, away_goals=1) == {
            "fixture_id": 1, "home_points": 0, "away_points": 3
        }

    def test_determine_points_draw(self):
        assert self.league_table._determine_points(fixture_id=1, home_goals=1, away_goals=1) == {
            "fixture_id": 1, "home_points": 1, "away_points": 1
        }

    def test_add_points(self):
        df = self.league_table._add_points(self.league_table.ft_fixtures)
        test_fixture_pts = df[df["fixture_id"] == 192297][["home_points", "away_points"]]
        expected_pts = pd.DataFrame(data={"home_points": [3], "away_points": [0]})
        assert test_fixture_pts.equals(expected_pts)

    def test_get_all_results(self):
        df = self.league_table._add_points(self.league_table.ft_fixtures)
        all_results = self.league_table._get_all_results(df)
        assert len(all_results.index == 380)

    def test_league_table(self):
        expected_df = pd.DataFrame(data={
            "POS": [1],
            "TEAM": ["Leicester"],
            "PTS": [81],
            "GF": [68],
            "GA": [36],
            "GD": [32],
            "PL": [38]
        })
        final_table = self.league_table.league_table()
        assert final_table[final_table["POS"] == 1].equals(expected_df)
