class InvalidCustomId(Exception):
    """
    Raised when a custom id key does not match those listed in VALID_CUSTOM_IDS in globals.py.
    """
    pass


class InvalidEndpoint(Exception):
    """
    Raised when an invalid endpoint is passed. Valid endpoints are defined under BASE_ENDPOINTS in globals.py.
    """
    pass


class InvalidStatusCode(Exception):
    """
    Raised when an invalid status code is recieved from the API.
    """
    pass


class MissingAPIKey(Exception):
    """
    Raised when the api key has not been passed to the APIFootball class and is not an environment variable.
    """
    pass


class NoAvailableCredits(Exception):
    """
    Raised when the user does not have enough credits to make the requested calls.
    """
    pass


class NoValidationSchema(Exception):
    """
    Raied when vaildation is required but no schema is available.
    """
    pass
