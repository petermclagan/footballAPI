from jsonschema import Draft7Validator

from footballAPI import API_SCHEMAS, logger


def validate_schema(endpoint: str):
	"""
	Validates the expected API schema contained within
	the global variable API_SCHEMAS
	"""
	assert endpoint in API_SCHEMAS.keys(), f"Missing endpoint {endpoint} from API_SCHEMAS."
	api_schema = API_SCHEMAS[endpoint]
	logger.debug(f"Checking schema for {endpoint}")
	Draft7Validator.check_schema(api_schema)
	return
