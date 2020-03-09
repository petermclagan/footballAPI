import json
import logging
import os

# Required dirs
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
CREDS_DIR = os.path.join(ROOT_DIR, "credentials")
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
TESTS_DIR = os.path.join(ROOT_DIR, "tests")
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")

API_CONFIG_DIR = os.path.join(CONFIG_DIR, "api")
API_SCHEMAS_DIR = os.path.join(API_CONFIG_DIR, "schemas")

SQL_ALCHEMY_CONFIG_DIR = os.path.join(CONFIG_DIR, "sql_alchemy")

REQUIRED_MODULE_DIRS = [CONFIG_DIR,
			   			CREDS_DIR,
			   			SCRIPTS_DIR,
			   			TESTS_DIR,
			   			TOOLS_DIR,
			   			API_CONFIG_DIR,
			   			API_SCHEMAS_DIR,
			   			SQL_ALCHEMY_CONFIG_DIR]

for DIR in REQUIRED_MODULE_DIRS:
	assert os.path.exists(DIR)

# optional dirs
UNICODE_MAPPING_DIR = os.path.join(CONFIG_DIR, "encoding")

UNICODE_MAPPING = dict()
if os.path.exists(UNICODE_MAPPING_DIR):
	for mapping_file in os.listdir(UNICODE_MAPPING_DIR):
		if mapping_file.endswith('.json'):
			with open(os.path.join(UNICODE_MAPPING_DIR, mapping_file)) as unicode_map:
				unicode_mapping_json = json.load(unicode_map)
			UNICODE_MAPPING.update(unicode_mapping_json)

# Initialise logger
logger = logging.getLogger()
logging.basicConfig(
            format='[%(asctime)s][%(threadName)s][%(levelname)s]: %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')

# Read the secrets.json file from CREDS_DIR
try:
	with open(os.path.join(CREDS_DIR, "secrets.json")) as secrets:
		SECRETS = json.load(secrets)
except FileNotFoundError:
	logger.error(f"No secret file found in {CREDS_DIR}")
	SECRETS = None

# Load all schemas into a global dictionary
API_SCHEMAS = dict()
for schema_file in os.listdir(API_SCHEMAS_DIR):
	if schema_file.endswith('.json'):
		with open(os.path.join(API_SCHEMAS_DIR, schema_file)) as schema_json:
			json_schema = json.load(schema_json)
		API_SCHEMAS[schema_file.replace('.json', '')] = json_schema
