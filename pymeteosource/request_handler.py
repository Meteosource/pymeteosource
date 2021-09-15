"""Module that handles sending the requests to API"""

import requests

from .errors import InvalidRequestError

class RequestHandler:
    """
    Object that handles sending the requests to API

    Attributes
    ----------
    session : requests.sessions.Session
        A session object to send the requests. This can speed-up multiple
        requests within a program run.

    Methods
    -------
    execute_request
        Execute request and return the JSON response
    """

    def __init__(self, key):
        """
        :param str: The API key
        """
        # Initialize the session
        self.session = requests.Session()
        # Automatically add key header to all requests made within the session
        self.session.headers.update({'X-API-Key': key})

    def execute_request(self, url, **params):
        """
        Make a request and return the JSON response

        :param str: URL of the requests (without the parameters)
        :param kwargs: Arguments of the request (lat, lon, ...)
        """
        response = self.session.get(url, params=params)
        if response.status_code != 200:
            raise InvalidRequestError(response)

        data = response.json()

        # We always get the source data in UTC and then convert to local tz
        assert data['timezone'] == 'UTC'

        return data
