"""Module that provide the MeteoSource interface object"""

from .request_handler import RequestHandler
from .types import langs, sections, units, endpoints
from .errors import InvalidArgumentError
from .data import Forecast


class MeteoSource:
    """
    The main object that provides the interface for MeteoSource API

    Attributes
    ----------
    req_handler : RequestHandler
        fdf
    host : string
        The host URL of the MeteoSource API
    tier : string
        The tier the user is using

    Methods
    -------
    build_url
        Build URL for the request
    get_point_forecast
        Get forecast data for given point
    """
    def __init__(self, api_key, tier, host='https://www.meteosource.com/api'):
        """
        Basic constructor

        :param str: API key
        :param str: Tier the user is using
        :param str: Host URL of the MeteoSource API
        """
        # Initialize the request handler with the API key
        self.req_handler = RequestHandler(api_key)
        self.host = host
        self.tier = tier

    def build_url(self, endpoint):
        """
        Build URL for the request

        :param str: Endpoint for the request
        :return str: The URL of the request without parameters (lat, lon, ...)
        """
        pars = {'host': self.host, 'tier': self.tier, 'endpoint': endpoint}
        url = '{host}/v1/{tier}/{endpoint}'.format(**pars)

        return url

    def get_point_forecast(self, place_id=None, lat=None, lon=None,
                           sections=sections.ALL, tz='UTC',
                           lang=langs.ENGLISH, units=units.METRIC):
        """
        Get forecast data for given point

        :param str: Identifier of the place (place_id)
        :param float: Latitude of the point
        :param float: Longitude of the point
        :param str: Sections to return
        :param str: Timezone in which the times will be expressed
        :param str: Language
        :param str: Units to use
        :return Forecast: Forecast object with the forecast data
        """
        # Build the URL for the request
        url = self.build_url(endpoints.POINT)
        # Parameters of the request
        pars = {'language': lang, 'units': units, 'timezone': tz,
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
        return Forecast(data)
