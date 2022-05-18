import pytest

from footballAPI import APIFootball

from footballAPI.exceptions import InvalidCustomId, InvalidStatusCode


class TestAPIFootball:
    def setup(self):
        self.api = APIFootball()
        self.endpoint1 = "status"
        self.endpoint2 = "countries"

    def test_check_200_status_code(self):
        assert self.api._check_status_code(200) is None

    def test_check_not_200_status_code(self):
        with pytest.raises(InvalidStatusCode):
            self.api._check_status_code(100)

    def test_dryrun_get_returns_none(self):
        assert self.api._get(endpoint=self.endpoint1, dryrun=True) is None

    def test_call_api(self):
        data = self.api.get(endpoint="countries")

        expected_country = {
            "country": "Algeria",
            "code": "DZ",
            "flag": "https://media.api-sports.io/flags/dz.svg"
        }

        assert expected_country in data["api"]["countries"]

    def test_custom_endpoint_valid_ids_dryrun(self):
        assert self.api.get(endpoint='match', dryrun=True, custom_ids={'fixture_id': 65}) is None

    def test_custom_endpoint_invalid_ids_dryrun(self):
        with pytest.raises(InvalidCustomId):
            self.api.get(endpoint='match', dryrun=True, custom_ids={'should_fail': 1})

    def test_custom_endpoint_no_ids_dryrun(self):
        with pytest.raises(ValueError):
            self.api.get(endpoint='match', dryrun=True)
