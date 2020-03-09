import json
import os
import time
from typing import *

from sqlalchemy import table
from sqlalchemy.exc import ProgrammingError

from footballAPI import API_SCHEMAS, ROOT_DIR, SECRETS, logger
from footballAPI.config import API_CONNECTION_CONFIG
from footballAPI.tools.api_football import APIFootball
from footballAPI.tools.micro_alchemy import MicroAlchemy
from footballAPI.validation.validate_api_response_schemas import validate_schema

football_alchemy = MicroAlchemy(**SECRETS)
session = football_alchemy.Session()

api_football = APIFootball(**API_CONNECTION_CONFIG)
api_football.update_credits()

# Load user preferences, if any
USER_PREFERENCES_DIR = os.path.join(ROOT_DIR, "preferences")
USER_PREFERENCES_FILE = os.path.join(USER_PREFERENCES_DIR, "preferences.json")
if os.path.exists(USER_PREFERENCES_FILE):
	logger.info("Found preferences.json.")
	with open(USER_PREFERENCES_FILE) as prefs:
		USER_PREFERENCES = json.load(prefs)
else:
	logger.warning("No user preferences found. Will collect all data. This will use many credits and requires a subscription.")
	USER_PREFERENCES = None


def batch_rows(rows: List) -> List[List]:
	"""
	Batches rows into chunks of 50 for inserting.
	This is required to ensure that the database doesn't struggle
	with either one large query, or many individual rows.
	rows: The full list of rows to be batched
	return: A list of lists of rows to be inserted
	"""
	for i in range(0, len(rows), 50):
		yield rows[i: i+50]


def get_current_pk(table: table):
	"""
	Get all existing primary keys from a table. Only works with one PK
	"""
	pks_raw = session.query(table.primary_key.columns.values()[0]).all()
	pks = [pk[0] for pk in pks_raw]
	return pks


def cancel_counter():
	"""
	This gives the user 10 seconds to cancel before running costly queries
	"""
	for sec in range(0,10):
		ell = "."*(sec+1)
		logger.warning(f"{10-sec} seconds to cancel{ell}")
		time.sleep(1)
	return


def get_league_ids():
	"""
	Gets all league ids from leagues table
	"""
	from footballAPI.config.sql_alchemy.tables.leagues import leagues_spec
	leagues_table = football_alchemy.table(table_spec=leagues_spec)
	x = get_current_pks(table=leagues_table)
	rows = session.query(leagues_table.c.league_id).all()
	for row in rows:
		yield row.league_id
