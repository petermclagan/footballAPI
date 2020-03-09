import json
import os
import requests
import urllib3
import jsonschema
from typing import Dict, List, Union

from footballAPI import API_SCHEMAS, logger
from footballAPI.config import API_CONNECTION_CONFIG

assert 'endpoints' in API_CONNECTION_CONFIG.keys(), "Require endpoints in connection.json"

class InvalidEndpoint(Exception):
    pass

class InvalidStatusCode(Exception):
    pass

class NoAvailableCredits(Exception):
    pass

class APIFootball:
    """
    This is a wrapper to make using api-football easier in Python.
    """
    def __init__(self, base_url: str, headers: Union[Dict[str, str], None]=None, verify: bool=False, **kwargs):
        self.base_url = base_url
        self.headers = headers
        self.verify = verify
        self.available_credits = None
        self.max_credits = None
        self.config_endpoints = API_CONNECTION_CONFIG['endpoints']
        self.allowed_endpoints = [e.split('/')[0] for e in self.config_endpoints]
        if not self.verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return

    def _check_status_code(self, status_code: int):
        """
        Check the status code of a response to ensure it is valid
        status_code: The status code to be validated
        """
        if status_code == 200:
            logger.debug("Valid status code recieved")
            return
        else:
            raise InvalidStatusCode(f"{str(status_code)} is an invalid status_code!")

    def _endpoint_is_valid(self, endpoint: str):
        """
        Ensures that the endpoint passed is expected to avoid wasting credits.
        endpoint: The endpoint to check
        """
        actual_endpoint = endpoint.split('/')[0]
        if not actual_endpoint in self.allowed_endpoints:
            raise InvalidEndpoint(f"{actual_endpoint} is not in the connection.json file.")
        logger.debug(f"{endpoint} is contained in the connection.json file.")
        return

    def _get(self,
            endpoint_url: str,
            dryrun: bool=False,
            params: Dict[str, str]=None
            ) -> Union[requests.Response, None]:
        """
        Calls the api and returns the response if a successful status code
        endpoint_url: The extension of the base url
        dryrun: If True it will only say which endpoint will be called
        params: The params to be passed to the request
        return: The returned response from the API
        """
        if params:
            assert type(params) == dict, 'Parameters are not a dictionary.'

        logger.debug("Building payload")
        api_url = os.path.join(self.base_url, endpoint_url)
        payload = {"url": api_url,
                   "headers": self.headers,
                   "verify": self.verify,
                   "params": params}
        logger.debug("Payload built successfully")
        if not dryrun:
            resp = requests.get(**payload)
            if not endpoint_url == 'status':
                logger.debug("Updating credits after api call")
                self.available_credits -= 1
            logger.debug("Checking for a valid status code")
            self._check_status_code(resp.status_code)
        else:
            logger.info(f"Dryrun: Will call {api_url} with parameters {params}")
            resp = None
        return resp

    def _validate_data(self,
                       resp: requests.Response,
                       expected_schema: Dict) -> Dict:
        """
        Checks that the expected keys are contained in the response.
        resp: The requests response to validate
        expected_schema: A JSON object of the structure, for use with jsonschema package
        return: Returns the validated JSON data
        """
        logger.debug("Loading JSON data from response.")
        data = resp.json()
        jsonschema.validate(instance=data, schema=expected_schema)
        return data

    def get(self,
            endpoint_url: str,
            expected_schema: Dict=None,
            dryrun: bool=False,
            params: Dict[str, str]=None,
            validate: bool=True,
            **kwargs
            ) -> Union[Dict, None]:
        """
        This is the user interface version of get. Ensures that there are enough valid credits.
        endpoint_url: The endpoint to call
        expected_schema: The expected schema response
        dryrun: If True it will only say which endpoint will be called
        params: The params to be passed to the request
        validate: Validate the JSON returned
        return: The returned response from the API
        """
        self._endpoint_is_valid(endpoint=endpoint_url)

        if not self.available_credits:
            logger.error(f"Need to determine available credits. Please use the update_credits() function.")
            exit(1)

        if validate and not dryrun:
            assert expected_schema, "Validation requires an expected schema"

        if self.available_credits > 0:
            resp = self._get(endpoint_url=endpoint_url,
                             dryrun=dryrun,
                             params=params)

        else:
            raise NoAvailableCredits("There are no available credits to use.")

        if dryrun:
            logger.warning(f"No data as dryrun, skipping validation.")
            return None
        else:
            if validate:
                logger.debug(f"Validating response")
                validated_data = self._validate_data(resp=resp,
                                                     expected_schema=expected_schema)
                return validated_data
            else:
                logger.warning(f"Skipping validation of response")
                return resp.json()

    def update_credits(self):
        """
        Update the total available credits available by querying the status endpoint
        """
        logger.debug("Updating credits")
        resp = self._get(endpoint_url='status')
        data = self._validate_data(resp=resp,
                                   expected_schema=API_SCHEMAS['status'])
        self.max_credits = data['api']['status']['requests_limit_day']
        # Add an additional credit for safety
        used_credits = data['api']['status']['requests'] + 1
        self.available_credits = self.max_credits - used_credits
        logger.info(f"There are {self.available_credits} available credits available.")
        return

if __name__ == '__main__':
    import footballAPI
    from footballAPI import config
    API_KEY = footballAPI.SECRETS['API_KEY']
    API_SCHEMAS = footballAPI.API_SCHEMAS

    status_schema = API_SCHEMAS['status']

    api_base_url = config.API_CONNECTION_CONFIG['base_url']
    api_header = {'X-RapidAPI-Key': API_KEY}
    apifetcher = APIFootball(base_url=api_base_url,
                             headers=api_header)
    apifetcher.update_credits()
    

    data = {
    "api": {
        "results": 970,
        "leagues": [
            {
                "league_id": 1,
                "name": "World Cup",
                "type": "Cup",
                "country": "World",
                "country_code": None,
                "season": 2018,
                "season_start": "2018-06-14",
                "season_end": "2018-07-15",
                "logo": "https://media.api-football.com/leagues/1.png",
                "flag": None,
                "standings": 1,
                "is_current": 1,
                "coverage": {
                    "standings": True,
                    "fixtures": {
                        "events": True,
                        "lineups": True,
                        "statistics": True,
                        "players_statistics": False
                    },
                    "players": True,
                    "topScorers": True,
                    "predictions": True,
                    "odds": False
                }
            }
        ]
    }
    }

    jsonschema.validate(instance=data, schema=API_SCHEMAS['leagues'])