"""Module that provide the Meteosource interface object"""

import datetime as dt

from .request_handler import RequestHandler
from .types import langs, sections, units, endpoints, time_formats
from .errors import (InvalidArgumentError, InvalidDateFormat, InvalidDateRange,
                     InvalidDateSpecification)
from .data import Forecast, TimeMachine, AirQuality, Place


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
    get_time_machine
        Get archive data from time_machine endpoint
    get_air_quality
        Get air quality data for given point
    get_nearest_place
        Get the nearest named place for given point
    get_find_places
        Search for places by place name or ZIP code
    get_find_places_prefix
        Search for places by the beginning of the place name or ZIP code
    """
    def __init__(self, api_key, tier, host='https://www.meteosource.com/api',
                 use_gzip=True):
        """
        Basic constructor

        :param str: API key
        :param str: Tier the user is using
        :param str: Host URL of the Meteosource API
        :param bool: True if gzip compression should be used, False otherwise
        """
        # Initialize the request handler with the API key
        self.req_handler = RequestHandler(api_key, use_gzip)
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

    # pylint: disable=R0201
    def _build_location_pars(self, pars, place_id, lat, lon):
        """
        Add location specification to parameters dict

        The request should contain either place_id or lat+lon. This function
        checks whether the location is fully and non-ambiguously specified,
        and adds proper parameters.

        :param dict: Dictionary with the other-than-location parameter(s)
        :param str: Identifier of the place (place_id)
        :param float: Latitude of the point
        :param float: Longitude of the point
        :return dict: Dictionary with location parameter(s) set
        """
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

        return pars

    def get_point_forecast(self, place_id=None, lat=None, lon=None,
                           sections=(sections.CURRENT, sections.HOURLY),
                           tz='UTC', lang=langs.ENGLISH, units=units.AUTO,
                           endpoint=endpoints.POINT):
        """
        Get forecast data for given point

        :param str: Identifier of the place (place_id)
        :param float: Latitude of the point
        :param float: Longitude of the point
        :param str: Sections to return
        :param str: Timezone for final output. Requests are always made in UTC!
        :param str: Language
        :param str: Units to use
        :param str: Endpoint to use, can be overridden
        :return Forecast: Forecast object with the forecast data
        """
        # Build the URL for the request
        url = self._build_url(endpoint)
        if isinstance(sections, (list, tuple)):
            sections = ','.join(sections)
        # Parameters of the request, the requested tz is always UTC!
        pars = {'language': lang, 'units': units, 'timezone': 'UTC',
                'sections': sections}

        # Update parameters with location selection
        pars = self._build_location_pars(pars, place_id, lat, lon)

        # Execute the request with the built URL and parameters
        data = self.req_handler.execute_request(url, **pars)

        # Load the result into Forecast object and return it
        return Forecast(data, tz)

    def get_air_quality(self, place_id=None, lat=None, lon=None, tz='UTC',
                        endpoint=endpoints.AIR_QUALITY):
        """
        Get air quality data for given point

        :param str: Identifier of the place (place_id)
        :param float: Latitude of the point
        :param float: Longitude of the point
        :param str: Timezone for final output. Requests are always made in UTC!
        :param str: Endpoint to use, can be overridden
        :return AirQuality: AirQuality object with the air quality data
        """
        # Build the URL for the request
        url = self._build_url(endpoint)
        # Parameters of the request, the requested tz is always UTC!
        # Note: the air_quality endpoint does not accept a language
        # parameter (its data is numeric only), unlike the other endpoints.
        pars = {'timezone': 'UTC'}

        # Update parameters with location selection
        pars = self._build_location_pars(pars, place_id, lat, lon)

        # Execute the request with the built URL and parameters
        data = self.req_handler.execute_request(url, **pars)

        # Load the result into AirQuality object and return it
        return AirQuality(data, tz)

    def get_nearest_place(self, lat, lon, lang=langs.ENGLISH,
                          endpoint=endpoints.NEAREST_PLACE):
        """
        Get the nearest named place for given point

        This is useful to get a place_id (and other information) for
        given lat+lon, which can then be used in the other requests.

        :param float: Latitude of the point
        :param float: Longitude of the point
        :param str: Language
        :param str: Endpoint to use, can be overridden
        :return Place: Place object with the nearest place
        """
        # Build the URL for the request
        url = self._build_url(endpoint)
        # Parameters of the request
        pars = {'lat': lat, 'lon': lon, 'language': lang}

        # Execute the request with the built URL and parameters
        data = self.req_handler.execute_request(url, **pars)

        # Load the result into Place object and return it
        return Place(data)

    def get_find_places(self, text, lang=langs.ENGLISH,
                        endpoint=endpoints.FIND_PLACES):
        """
        Search for places by place name or ZIP code

        Complete words are required, use get_find_places_prefix if you
        need prefix search (e.g. for autocomplete forms).

        :param str: Place name or ZIP code to search for
        :param str: Language
        :param str: Endpoint to use, can be overridden
        :return list: List of Place objects that match the search
        """
        # Build the URL for the request
        url = self._build_url(endpoint)
        # Parameters of the request
        pars = {'text': text, 'language': lang}

        # Execute the request with the built URL and parameters
        data = self.req_handler.execute_request(url, **pars)

        # Load the result into list of Place objects and return it
        return [Place(place) for place in data]

    def get_find_places_prefix(self, text, lang=langs.ENGLISH,
                               endpoint=endpoints.FIND_PLACES_PREFIX):
        """
        Search for places by the beginning of the place name or ZIP code

        As opposed to get_find_places, the last word of the query can be
        incomplete, which is useful e.g. for autocomplete forms.

        :param str: Place name or ZIP code prefix to search for
        :param str: Language
        :param str: Endpoint to use, can be overridden
        :return list: List of Place objects that match the search
        """
        # Build the URL for the request
        url = self._build_url(endpoint)
        # Parameters of the request
        pars = {'text': text, 'language': lang}

        # Execute the request with the built URL and parameters
        data = self.req_handler.execute_request(url, **pars)

        # Load the result into list of Place objects and return it
        return [Place(place) for place in data]

    def _str_to_date(self, date):
        """
        Convert passed date to datetime.date instance

        :param str/datetime.date/datetime.datetime: Passed date
        :return datetime.date: Date instance
        """
        if type(date) is dt.date:  # pylint: disable=C0123
            return date
        if type(date) is dt.datetime:  # pylint: disable=C0123
            return date.date()

        # Convert string date to datetime.date, while checking the format
        try:
            return dt.datetime.strptime(date, time_formats.F2).date()
        except ValueError as e:
            raise InvalidDateFormat(date, time_formats.F2) from e

    def _get_tm_dates(self, date, date_from, date_to):
        """
        Get date list for the time_machine endpoint

        The user can either specify 'date', which can be string, datetime.date,
        datetime.datetime or list/set/tuple of these types; or date range
        (by specifying date_from, date_to - both are inclusive). We first check
        whether only one of these options were used, and then convert it to
        list of datetime.date instances, that we want to retrieve.

        :param iterable/str/datetime.date/datetime.datetime: Passed date(s)
        :param str/datetime.date/datetime.datetime: Start point of date range
        :param str/datetime.date/datetime.datetime: End point of date range
        """
        # Check date specification validity
        if date is None and (date_from is None or date_to is None):
            raise InvalidDateSpecification()
        if date is not None and (date_from is not None or date_to is not None):
            raise InvalidDateSpecification()

        # If we are not using range
        if date is not None:
            # Convert passed date(s) to list, if not allowed iterable
            return date if isinstance(date, (list, tuple, set)) else [date]

        # Convert the start and end dates to datetime.date
        dt_from = self._str_to_date(date_from)
        dt_to = self._str_to_date(date_to)

        # If we are using range, check date_from is smaller than date_to
        if dt_to <= dt_from:
            raise InvalidDateRange(date_from, date_to)

        # Calculate number of days from dt_from we need
        no_days = (dt_to - dt_from).days + 1

        # Return a list with these dates
        return [dt_from + dt.timedelta(days=x) for x in range(no_days)]

    def get_time_machine(self, date=None, date_from=None, date_to=None,
                         place_id=None, lat=None, lon=None, tz='UTC',
                         units=units.AUTO, endpoint=endpoints.TIME_MACHINE):
        """
        Get archive data from time_machine endpoint

        The user can either specify 'date', which can be string, datetime.date,
        datetime.datetime or list/set/tuple of these types; or date range
        (by specifying date_from, date_to - both are inclusive).

        :param str/date/iterable/None: Date(s) to retrieve
        :param str/date/None: Starting date (inclusive)
        :param str/date/None: End date (inclusive)
        :param str: Identifier of the place (place_id)
        :param float: Latitude of the point
        :param float: Longitude of the point
        :param str: Timezone for final output. Requests are always made in UTC!
        :param str: Units to use
        :param str: Endpoint to use, can be overridden
        :return TimeMachine: TimeMachine object with the archive data
        """
        # Build the URL for the request
        url = self._build_url(endpoint)

        # Update parameters with location selection, date will be added in loop
        pars = self._build_location_pars({'units': units}, place_id, lat, lon)
        # We need to specify UTC timezone
        pars['timezone'] = 'UTC'

        # Get list of dates to retrieve
        dates = self._get_tm_dates(date, date_from, date_to)

        # Placeholder for the resulting TimeMachine object
        tm = None
        # Iterate over the dates
        for d in dates:
            # Convert date to proper string format
            if type(d) is dt.date:  # pylint: disable=C0123
                pars['date'] = d.strftime(time_formats.F2)
            elif type(d) is dt.datetime:  # pylint: disable=C0123
                pars['date'] = d.date().strftime(time_formats.F2)
            elif isinstance(d, str):
                # Check the date format is correct for string dates
                _ = self._str_to_date(d)
                # Update the date in the parameters
                pars['date'] = d
            else:
                raise InvalidDateFormat(d, 'str or date instance')

            # Execute the request with the built URL and parameters
            data = self.req_handler.execute_request(url, **pars)

            # Create a TimeMachine instance
            cur_tm = TimeMachine(data, tz, d)

            # Assign the current instance to the result, or append it
            if tm is None:
                tm = cur_tm
            else:
                tm.append(cur_tm)

        return tm
