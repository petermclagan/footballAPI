# footballAPI
This is a package designed to work with the football (soccer) API provided by [API-Sports](https://www.api-football.com/). Full documentation and subscription details are provided on the website. Usage of this package requires **any** level of subscription and a valid `API_KEY`.

<h2 id=api-football> APIFootball</h2>
This is the main module of the package. It handles requests, and manages available credits to avoid using more than a subscription covers, as well as performing validation on the structure of the API response.

The module can be instantiated as below:
```python
from footballAPI import APIFootball

apifootball = APIFootball(**kwargs)
```
Arguments:
	- `api_key`: a valid API key. If not provided it must be available as an environment variable named `API_KEY`.
	- `base_url (optional)`: the URL to query, defaulting to `https://server1.api-football.com`.  Implemented in case of changes.
	- `headers (optional)`: any additional headers required. Note that the `X-RapidAPI-Key` header is added separately and should **not** be included. Default is `None`.
	- `verify (optional)`: verification to be passed to `requests.get`. Defaults to `False`.

<h3 id=base-endpoints> Base Endpoints </h3>
The permitted endpoints are defined in the [documentation](https://www.api-football.com/documentation). Currently these are:

- status
- timezone
- seasons
- countries
- leagues
- teams
- players
- leagueTable
- fixtures
- events
- lineups
- statistics
- predictions
- coachs
- transfers
- sidelined
- odds

Any `get` command that is called will ensure that one of these endpoints has been passed, otherwise an `InvalidEndpoint` exception shall be raised.

<h3 id=custom-endpoints> Custom Endpoints </h3>

These are endpoints which are not standard from the API and have been built and implemented manually to make using the API easier.
 An additional argument is required for the `get` command, **custom_ids**. This should be a dictionary with the key being the name of id type and the value being the provided id. These are then used to build the correct API url to request.

The implemented custom endpoints with their corresponding endpoint are:

| custom endpoint | APIFootball endpoint    | required custom\_ids |
|-----------------|:-----------------------:|---------------------:|
| match           | fixture/id/{fixture_id} |           fixture_id |

If the required custom_ids are not passed a `ValueError` is raised. Only the custom_ids in the above table have been implemented, any others will  raise an `InvalidCustomId` error.
 
 <h5 id=custom-example> Example </h5>
 
 ```python
 apifootball.get(endpoint='match', custom_ids={'fixture_id': 1}
 ```
 This will return the match data for the fixture_id of 1.

**Usage of more detailed endpoints such as those requiring specific ids not covered in custom endpoints are not checked and can result in wasting credits if not checked.**

<h3 id=checking-credits> Checking Credits </h3>
Upon instantiating the class a call to the `status` endpoint is done. **This does not use any credits**. This creates the class variables:
	- `max_credits`: this is the maximum number of available credits per day linked to the provided `API_KEY`.
	- `available_credits`: this is the difference between used credits and `max_credits` minus one to allow for an additional level of security.

**If `available_credits` is 1 or less a `NoAvailableCredits` exception will be raised**.

After each API call these values are updated, and can be updated at any time using the `update_credits()` method.

<h3 id=making-requests>Making Requests</h3>

Requests to the API should be made using the `get` method. See [here](#get-examples) for example usage.

`method: get(endpoint, dryrun=False, validate=True, validation_schema=None)`

This method will call the API for the provided `endpoint` and return the data in a JSON format.

Arguments:
	- `endpoint`: the endpoint to call (see [documentation](https://www.api-football.com/documentation) for available endpoints.
	- `dryrun (optional)`: if `True` this will only print logs stating the endpoints and calls that will be made. The method will return `None` when this is used.
	- `validate (optional)`: perform [jsonschema](https://json-schema.org/) validation on the JSON data received from the API (see [here](#jsonvalidation) for more details).
	- `validation_schema (optional)`: a valid `jsonschema` to validate response against. Will default to those provided within the package.

<h4 id=get-examples>Examples</h4>

1) Requesting `countries` data:
	```python
	data = apifootball.get(endpoint="countries")
	```
2) Requesting `fixtures` data with `league_id` parameter:
	```python
	data = apifootball.get(endpoint="fixtures")
	```
<h3 id=jsonvalidation>JSON Validation </h3>

Validation can be performed on the responses from the API through the usage of the [jsonschema](https://json-schema.org/) library. This can be turned off if desired, or validated using custom schemas by using the `validate` and `validation_schema` arguments of the [get](#making-requests) method.

Currently there are available schemas contained within the package for the following endpoints:

- `status`
- `fixtures` - this applies to the fixtures obtained by league id only
- `teams` - this applies only to the teams data and not the team statistics
- `leagues`
- `countries`
- `timezone`
- `seasons`
- `players` - this applies only to the squad endpoint of players currently
- `coachs`
- `match`

Others shall be added to this list.

<h2 id=further-notes>Further Notes </h2>

- Running all of the `pytests` for this package will currently use 1 credit of the user, and requires the `API_KEY` environment variable to be available.

<h1 id=release-notes> Release Notes </h1>
<h3 id=0.1.0-1.0.0> 0.1.0 -> 1.0.0 </h3>

- Deprecated `params` argument from `get` function due to it not functioning with the API. To call API the user must now pass the full endpoint, eg. `fixtures/live`.
- Added validation to the base endpoint provided to avoid wasting credits, with configuration of this list in the new `globals.py` file.
- Added additional validation schemas for coachs, players, seasons and timezone.

<h3 id=1.0.0-1.1.0> 1.0.0 -> 1.1.0 </h3>

- Added new custom endpoints feature to improve handling of different endpoints.
- Improvements to logging of schema validation errors.
- Match is now a permitted endpoint with a validation schema. This requires a specific `fixture_id` and will return fixture, lineup, events, statistic and player statistic data for this `fixture_id`.
