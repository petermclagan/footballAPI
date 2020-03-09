import pytest
from jsonschema.exceptions import SchemaError, ValidationError

import footballAPI
from footballAPI.config import API_CONNECTION_CONFIG
from footballAPI.tools.api_football import APIFootball, InvalidEndpoint

API_KEY = footballAPI.SECRETS['API_KEY']
api_base_url = API_CONNECTION_CONFIG['base_url']
api_header = {'X-RapidAPI-Key': API_KEY}
apifootball = APIFootball(base_url=api_base_url,
                         headers=api_header)
apifootball.update_credits()

class TestAPIFootball:
	def test_available_credits_update_from_none(self):
		update = APIFootball(base_url=api_base_url,
                             headers=api_header)
		assert not update.available_credits
		assert not update.max_credits
		update.update_credits()
		assert type(update.available_credits) == int
		assert type(update.max_credits) == int
		assert 0 <= update.available_credits <= update.max_credits
		return

	def test_available_credits_decrease_with_call(self):
		initial_credits = apifootball.available_credits
		data = apifootball.get(endpoint_url='leagues', validate=False)
		new_credits = apifootball.available_credits
		assert new_credits < initial_credits
		return
		data = apifootball.get(endpoint_url='status',
							   dryrun=True)
		assert data is None
		return

	def test_no_expected_schema_and_no_dryrun_with_validation(self):
		with pytest.raises(AssertionError):
			data = apifootball.get(endpoint_url='status')
		return

	def test_get_valid_endpoint_no_validation(self):
		data = apifootball.get(endpoint_url='status', validate=False)
		assert type(data) == dict
		return

	def test_get_invalid_endpoint_no_validation(self):
		with pytest.raises(InvalidEndpoint):
			data = apifootball.get(endpoint_url='stus', validate=False)
		return

	def test_validate_data_with_good_data_good_schema(self):
		# This assumes that this schema is correct.
		data = apifootball.get(endpoint_url='status',
							   expected_schema=footballAPI.API_SCHEMAS['status'])
		assert type(data) == dict
		assert 'api' in data.keys()
		return

	def test_validate_data_with_good_data_bad_schema(self):
		with pytest.raises(SchemaError):
			data = apifootball.get(endpoint_url='status',
							   expected_schema={'invalid'})
		return

	def test_validate_data_with_bad_data_good_schema(self):
		with pytest.raises(InvalidEndpoint):
			data = apifootball.get(endpoint_url='stus',
								   expected_schema=footballAPI.API_SCHEMAS['status'])
		return

	def test_validate_data_with_bad_data_bad_schema(self):
		with pytest.raises(InvalidEndpoint):
			data = apifootball.get(endpoint_url='stus',
				 							 expected_schema={'invalid'})
		return