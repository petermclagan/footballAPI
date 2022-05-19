from datetime import datetime, date
from typing import Dict, Union

import numpy as np
import pandas as pd

from footballAPI import APIFootball


class LeagueTable:
    def __init__(
            self,
            country: str,
            league: str,
            season: int
    ):
        """
        Tool to build the league table at a given point in time for any league and season from football-api
        :param country: Name of the country desired (see countries endpoint for full list)
        :param league_name: Name of the league desired
        :param season: Starting year of the desired season, eg. for 2015/16 season use 2015
        """
        self.apifootball = APIFootball()
        self.country = country.upper()
        self.league = league.upper()
        self.season = season
        self._set_league_id()
        self._set_league_ft_fixtures()
        self.earliest_match = self.ft_fixtures["event_date"].dt.date.min()

    def _set_league_id(self):
        """
        Obtains the league_id from the leagues endpoint using the provided class inputs.
        """
        all_leagues = self.apifootball.get(endpoint="leagues")
        for league in all_leagues["api"]["leagues"]:
            if (league["country"].upper() == self.country) & \
                    (league["name"].upper() == self.league) & \
                    (league["season"] == self.season):
                self.league_id = league["league_id"]
            else:
                continue
        if not self.league_id:
            raise ValueError("league_id not found, please check input parameters")
        else:
            return

    def _set_league_ft_fixtures(self):
        """
        Obtains the league fixtures for a given country, league_name and season (starting year).
        Only returns games that are finished.
        """
        fixtures = self.apifootball.get(endpoint="league_fixtures", custom_ids={"league_id": self.league_id})
        fixtures_data = fixtures['api']['fixtures']
        fixtures_df = pd.json_normalize(fixtures_data)
        self.ft_fixtures = fixtures_df.loc[fixtures_df["statusShort"] == "FT"]
        self.ft_fixtures["event_date"] = pd.to_datetime(self.ft_fixtures["event_date"])
        if self.ft_fixtures.empty:
            raise ValueError("No fixtures found")
        return

    @staticmethod
    def _determine_points(fixture_id: int, home_goals: int, away_goals: int) -> Dict[str, int]:
        """
        Calculates how many points each team earns in a given fixture
        :param fixture_id: Fixture ID used for joining points back to results dataframe
        :param home_goals: Number of goals scored by the home team
        :param away_goals: Number of goals scored by the away team
        :return: Dictionary containing fixture_id, home_points and away_points to create new columns
        """
        if home_goals == away_goals:
            return {"fixture_id": fixture_id, "home_points": 1, "away_points": 1}
        else:
            winner = "home_points" if home_goals > away_goals else "away_points"
            loser = "away_points" if home_goals > away_goals else "home_points"
            return {"fixture_id": fixture_id, winner: 3, loser: 0}

    @staticmethod
    def _get_all_results(results_df: pd.DataFrame) -> pd.DataFrame:
        """
        Combines home and away results for each team into one Dataframe.
        :param results_df: Dataframe containing home and away results
        :return: Unioned dataframe containing home and away results
        """
        points_df = results_df.copy()
        home_df = points_df.rename(columns={
            "homeTeam.team_name": "TEAM",
            "home_points": "PTS",
            "goalsHomeTeam": "GF",
            "goalsAwayTeam": "GA"
        })[["TEAM", "PTS", "GF", "GA"]]
        away_df = points_df.rename(columns={
            "awayTeam.team_name": "TEAM",
            "away_points": "PTS",
            "goalsAwayTeam": "GF",
            "goalsHomeTeam": "GA"
        })[["TEAM", "PTS", "GF", "GA"]]
        return pd.concat([home_df, away_df])

    def _add_points(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds home_points and away_points columns to results_df.
        :param results_df: Dataframe containing results data.
        :return: Dataframe with home and away points columns for each fixture added.
        """
        points_df = results_df.apply(
            lambda row: pd.Series(self._determine_points(
                fixture_id=row["fixture_id"],
                home_goals=row["goalsHomeTeam"],
                away_goals=row["goalsAwayTeam"]
            )), axis=1
        )
        return results_df.merge(points_df, how="inner", on="fixture_id")

    def league_table(self, as_of: Union[datetime, date] = datetime.now()) -> pd.DataFrame:
        """
        Builds the league table at a given point in time.
        :param as_of: Date to return league table for, inclusive.
        :return: Ordered league table as of given date
        """
        if self.earliest_match > as_of.date():
            raise ValueError(
                f"No results earlier than as_of date. Earliest date is {self.earliest_match}"
            )
        points_df = self._add_points(self.ft_fixtures)
        all_results_df = self._get_all_results(points_df)

        aggregated_points_df = all_results_df.groupby("TEAM").sum().reset_index()
        aggregated_points_df["GD"] = aggregated_points_df["GF"] - aggregated_points_df["GA"]

        matches_played = all_results_df.groupby("TEAM").size().reset_index(name="PL")
        final_table_df = aggregated_points_df.merge(matches_played, how="inner", on="TEAM") \
            .sort_values(["PTS", "GD", "GF"], ascending=False)
        final_table_df.index = np.arange(1, len(final_table_df) + 1)
        final_table_df.index.names = ["POS"]
        return final_table_df.reset_index()
