import json
import logging
import os
import pkg_resources
import urllib3
from typing import Dict, Union

import jsonschema
import requests
from requests.models import Response

from footballAPI.exceptions import *

class APIFootball:
	def __init__(
		self,
		api_key: str=None, 
		base_url: str="https://server1.api-football.com",
		headers: Union[Dict[str, str], None]=None,
		verify: bool=False
		):
		"""
		This will build the base connection parameters for usage of the API and will
		create the core structure for all API calls.

		Also updates total available credits available for the user.

		:param base_url: Base URL of the endpoint, defaults to currently active one
		:param headers: Any additional headers to be passed to API calls. Should NOT include API KEY
		:param verify: Use requests verification
		"""
		self.base_url = base_url

		if not api_key:
			try:
				api_key = os.environ["API_KEY"]
			except KeyError:
				raise MissingAPIKey("No API_KEY environment variable or passed to class.")

		self.headers = {"X-RapidAPI-Key": api_key}
		if headers:
			self.headers.update(headers)
		self.verify = verify
		self.available_credits = None
		self.max_credits = None
		self.logger = logging.getLogger()
		logging.basicConfig(
					format='[%(asctime)s][%(threadName)s][%(levelname)s]: %(message)s',
					level=logging.INFO,
					datefmt='%Y-%m-%d %H:%M:%S')

		if not self.verify:
			urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

		# Update available_credits and max_credits
		self.update_credits()

	def _check_status_code(self, status_code: int):
		"""
		Check the status code of a response to ensure it is valid. 
		Should only ever return a 200 status code.

		:param status_code: The status code to be validated
		"""
		if status_code == 200:
			self.logger.debug("Valid status code recieved")
			return
		else:
			raise InvalidStatusCode(f"{str(status_code)} is an invalid status_code!")

	def _get(
		self,
		endpoint: str,
		dryrun: bool=False,
		params: Dict[str, str]=None
		) -> Union[Response, None]:
		"""
		Calls the api and returns the response if a successful status code
		
		:param endpoint: The extension of the base url with any filters added
		:param dryrun: If True it will only say which endpoint will be called and return None
		:param params: The params to be passed to the request
		
		return: The returned response from the API or None if dryrun
		"""
		if params and not isinstance(params, Dict):
			raise InvalidParams("Params passed to request are not of type dict.")

		self.logger.debug("Building payload.")
		api_url = f"{self.base_url}/{endpoint}"
		payload = {
			"url": api_url,
			"headers": self.headers,
			"verify": self.verify,
			"params": params
		}
		self.logger.debug("Payload built successfully.")

		self.logger.info(f"{'(dryrun)' if dryrun else ''} Requesting {api_url}.")
		if not dryrun:
			resp = requests.get(**payload)
			self.logger.debug("Checking for valid status code.")
			self._check_status_code(resp.status_code)

		else:
			resp = None

		return resp

	def _validate_data(
		self,
		endpoint: str,
		data: Dict,
		expected_schema: Dict=None
		):
		"""
		Validates the JSON response from the API against a valid jsonschema object.

		:param endpoint: The base endpoint for the request
		:param: resp: The JSON response from the API
		:param expected_schema: The expected jsonschema object, defaults to provided shcemas
		"""
		self.logger.debug(f"Loading validation schema for {endpoint}")
		if not expected_schema:
			default_schema = f"validation_schemas/{endpoint}.json"
			default_schema_path = pkg_resources.resource_filename(__name__, default_schema)

			if not os.path.exists(default_schema_path):
				raise NoValidationSchema(f"No validation schema in default for endpoint {endpoint}.")

			with open(default_schema_path) as schema_json:
				schema = json.load(schema_json)

		else: 
			schema = expected_schema

		jsonschema.validate(instance=data, schema=schema)
		return

	def get(
		self,
		endpoint: str,
		dryrun: bool=False,
		params: Dict[str, str]=None,
		validate: bool=True,
		validation_schema: Dict=None
		) -> Union[Dict, None]:
		"""
		Can be used to run against any arbitrary endpoint. Using this function directly may result in wasting credits if the endpoint is invalid.
		
		:param endpoint: The endpoint to call
		:param dryrun: Execute the requests
		:param params: Any parameters to pass to the request
		:param validate: Perform validation against a jsonschema
		:param validation_schema: A non-default validation schema for validation if required

		return: The JSON response from the endpoint if not dryrun, or None 
		"""
		if self.available_credits > 0:
			resp = self._get(
						endpoint=endpoint,
						dryrun=dryrun,
						params=params
					)
			self.update_credits()

		if dryrun:
			return None

		data = resp.json()

		if validate:
			self.logger.debug(f"Performing validation")
			self._validate_data(
				endpoint=endpoint,
				data=data,
				expected_schema=validation_schema 
				)

		return data

	def update_credits(self):
		"""
		Updates the total available credits available by querying the status endpoint
		"""
		self.logger.debug("Updating credits")
		resp = self._get(endpoint="status")
		data = resp.json()

		self._validate_data(endpoint="status", data=data)

		self.max_credits = data["api"]["status"]["requests_limit_day"]

		# Add additional used credit for saftey net
		used_credits = data["api"]["status"]["requests"] + 1

		self.available_credits = self.max_credits - used_credits

		self.logger.info(f"{self.available_credits} credit(s) available.")

		return
