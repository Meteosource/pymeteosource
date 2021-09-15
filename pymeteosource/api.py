"""Module that provide the Meteosource interface object"""

from .request_handler import RequestHandler
from .types import langs, sections, units, endpoints
from .errors import InvalidArgumentError
from .data import Forecast


class Meteosource:
    """
    The main object that provides the interface for Meteosource API

    Attributes
    ----------
    req_handler : RequestHandler
        RequestHandler object to be used for the requests
    host : string
        The host URL of the Meteosource API
    tier : string
        The tier the user is using

    Methods
    -------
    _build_url
        Build URL for the request
    get_point_forecast
        Get forecast data for given point
    """
    def __init__(self, api_key, tier, host='https://www.meteosource.com/api'):
        """
        Basic constructor

        :param str: API key
        :param str: Tier the user is using
        :param str: Host URL of the Meteosource API
        """
        # Initialize the request handler with the API key
        self.req_handler = RequestHandler(api_key)
        self.host = host
        self.tier = tier

    def _build_url(self, endpoint):
        """
        Build URL for the request

        :param str: Endpoint for the request
        :return str: The URL of the request without parameters (lat, lon, ...)
        """
        pars = {'host': self.host, 'tier': self.tier, 'endpoint': endpoint}
        url = '{host}/v1/{tier}/{endpoint}'.format(**pars)

        return url

    def get_point_forecast(self, place_id=None, lat=None, lon=None,
                           sections=(sections.CURRENT, sections.HOURLY),
                           tz='UTC', lang=langs.ENGLISH, units=units.AUTO):
        """
        Get forecast data for given point

        :param str: Identifier of the place (place_id)
        :param float: Latitude of the point
        :param float: Longitude of the point
        :param str: Sections to return
        :param str: Timezone for final output. Requests are always made in UTC!
        :param str: Language
        :param str: Units to use
        :return Forecast: Forecast object with the forecast data
        """
        # Build the URL for the request
        url = self._build_url(endpoints.POINT)
        if isinstance(sections, (list, tuple)):
            sections = ','.join(sections)
        # Parameters of the request, the requested tz is always UTC!
        pars = {'language': lang, 'units': units, 'timezone': 'UTC',
                'sections': sections}

        # If place_id is not specified, we use lat+lon
        if place_id is None:
            # Check if both lat+lon are specified
            if lat is None or lon is None:
                raise InvalidArgumentError()
            # Add the lat+lon to the parameters
            pars.update({'lat': lat, 'lon': lon})
        else:
            # Check that only place_id is specified
            if lat is not None or lon is not None:
                raise InvalidArgumentError()
            # Add the place_id to the parameters
            pars.update({'place_id': place_id})

        # Execute the request with the built URL and parameters
        data = self.req_handler.execute_request(url, **pars)

        # Load the result into Forecast object and return it
        return Forecast(data, tz)
