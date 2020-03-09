import json
import os

from footballAPI import API_CONFIG_DIR, SECRETS, logger

## API config load
API_CONNECTION_CONFIG_FILE = os.path.join(API_CONFIG_DIR, "connection.json")

if not os.path.exists(API_CONNECTION_CONFIG_FILE):
	logger.error(f"No connection.json file in: {API_CONNECTION_CONFIG_FILE}")
	exit(1)

with open(API_CONNECTION_CONFIG_FILE) as api_conn:
	API_CONNECTION_CONFIG = json.load(api_conn)

assert 'base_url' in API_CONNECTION_CONFIG.keys(), f"{API_CONNECTION_CONFIG_FILE} requires a base_url."

API_CONNECTION_CONFIG['headers'] = {'X-RapidAPI-Key': SECRETS['API_KEY']}
