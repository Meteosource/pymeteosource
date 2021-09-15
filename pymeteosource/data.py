"""Module with classes that represent the API data"""

from warnings import warn
from datetime import datetime
import pytz

from .types.time_formats import F1, F2
from .errors import (InvalidStrIndexError, InvalidIndexTypeError,
                     InvalidDatetimeIndexError, EmptyInstanceError)


class BaseData:
    """
    Abstract class that represents data in any section of the response

    Attributes
    ----------
    _timezone : str
        String identifier of used timezone

    Methods
    -------
    load_data
        Load the API data from dict to member variables
    get_members
        Get names of member variables that are available
    to_pandas
        Export the data to pandas DataFrame
    """
    def __init__(self, timezone):
        """
        :param str: String identifier of used timezone
        """
        # Prevent users from instantiating the BaseData
        if type(self) is BaseData:  # pylint: disable=C0123
            raise Exception('BaseData cannot be instantiated!')
        # Save the timezone of the data
        self._timezone = timezone

    def load_data(self, data):
        """
        Load the API section data from dict to member variables

        All the members of the 'data' dicts that are not dicts (the direct)
        values are stored into member variables. The nested data (e.g.
        wind.angle) are stored as SingleTimeData instances.

        All dates are converted from strings to 'datetime's. Those dates that
        contain times are localized to be timezone-aware.

        :param dict: The dictionary as retrieved from RequestHandler
        """
        # Keep empty instance if no data are available
        if data is None:
            return

        # Initialize pytz timezone object using the data's timezone
        tz = pytz.timezone(self._timezone)

        # Iterate over the keys of the 'data' dict
        for key, value in data.items():
            # For nested data, initialize SingleTimeData instance
            if isinstance(value, dict):
                # Save the data into the instance attribute
                setattr(self, key, SingleTimeData(value, self._timezone))
            else:
                # None values can occur in the data
                if value is not None:
                    # Items that contain datetime and need to be localized
                    if key in ('date', 'last_update', 'rise', 'set'):
                        # Convert to datetime and localize
                        value = tz.localize(datetime.strptime(value, F1))
                    # Items that only contain day (not hours, etc.)
                    if key == 'day':
                        # Only convert to datetime
                        value = datetime.strptime(value, F2)

                # Save the data into the instance attribute
                setattr(self, key, value)

    def get_members(self):
        """
        Build list of variable names that are available in the instance

        :return list: List with string names of the available variables
        """
        # Ignore callables and variables that start with '_'
        return [x for x in dir(self) if
                not callable(getattr(self, x)) and not x.startswith("_")]

    def to_pandas(self):
        """
        Export the data to pandas DataFrame

        NOTE: This needs 'pandas' module, which is not needed for any other
        parts of pymeteosource. Because of this, it is not installed by default
        setup.py to keep the dependencies as minimal as possible. To use this
        feature, use 'pip install pymeteosource[pandas]' to install this
        package, or install pandas manually using 'pip install pandas'.

        :return pandas.DataFrame: The DataFrame with 'date'/'day' as index
        """
        # Try to lazy-load 'pandas' module
        try:
            import pandas as pd  # pylint: disable=C0415
        except ImportError:
            # If pandas is not installed, print warning and return None
            warn("Module pandas is not installed, cannot export the data. "
                 "Try to install pandas with 'pip install pandas'.")
            return None

        # This is the basic use case - rows are the timesteps
        if isinstance(self, MultipleTimesData):
            # pylint: disable=E1101
            df = pd.DataFrame([x.to_dict() for x in self.data])
        # This is also possible, but results in 1-row DataFrame
        elif isinstance(self, SingleTimeData):
            df = pd.DataFrame([self.to_dict()]) # pylint: disable=E1101
        # This should not happen
        else:
            c = self.__class__.__name__
            raise NotImplementedError("Cannot export {} to pandas.".format(c))

        # If 'date' or 'day' column is present, set it as index
        if 'date' in df.columns:
            df.set_index('date', inplace=True)
        elif 'day' in df.columns:
            df.set_index('day', inplace=True)

        return df

    def __repr__(self):
        """
        Override __repr__ to have usefull text when attepting to print
        """
        c, members = self.__class__.__name__, self.get_members()
        date = getattr(self, 'date', getattr(self, 'day', None))
        return ('<Instance of {} ({}) with {} member variables ({})>'.format(
            c, date, len(members), ', '.join(members)))

    def __getitem__(self, attr):
        """
        Override __getitem__ to allow variable access using [] operator
        """
        return getattr(self, attr)


class SingleTimeData(BaseData):
    """
    Class that represents data in single point in time

    This class is used to represent 'current' section, and the individual
    timesteps of 'minutely', 'hourly' and 'daily'.

    Methods
    -------
    to_dict
        Export the data to flat (not nested) dict
    """
    def __init__(self, data, timezone):
        # Call the parent's constructor to initialize the timezone
        super().__init__(timezone)
        # Load the data
        self.load_data(data)

    def to_dict(self, prefix=''):
        """
        Export the data to flat (not nested) dict

        To flatten the nested structures, the variable names are concatenated
        with '_'. For example, wind['angle'] becomes 'wind_angle'. In daily
        data, there are more than two levels of the nested data, so for example
        all_day['wind']['angle'] becomes all_day_wind_angle.

        :return dict: The data as dict
        """
        # Dict to hold the result
        res = {}
        # Iterate over the member variables representing the elements
        for key in self.get_members():
            # Get the value of current key (from the member variable)
            val = getattr(self, key)
            # If the data is nested, we recursively expand it
            if isinstance(val, BaseData):
                # Chain the variable name separated by '_' in each level
                res.update(val.to_dict(prefix='{}{}_'.format(prefix, key)))
            else:
                # If we have not-nested type, we simply add it to the dict
                res['{}{}'.format(prefix, key)] = val

        return res


class MultipleTimesData(BaseData):
    """
    Class that represents data in single point in time

    This class is used to represent 'current' section, and the individual
    timesteps of 'minutely', 'hourly' and 'daily'.

    Attributes
    ----------
    summary : str
        Summary of precipitation minutecast - only present for minutely data
    data_type : str
        The type of section the instance represents, e.g. 'minutely'
    data : list
        List of SingleTimeData instances, each containing single timestep
    dates_str : list
        List of 'str' dates of the timesteps (in the same order)
    dates_dt : list
        List of 'datetime' dates of the timesteps (in the same order)
    """
    def __init__(self, data, data_type, timezone):
        # Call the parent's constructor to initialize the timezone
        super().__init__(timezone)
        # Keep empty instance if no data are available
        if data is None:
            return

        # Get the datetime column based on the 'data_type'
        self.data_type = data_type
        if self.data_type == 'daily':
            date_col, form = 'day', F2
        else:
            date_col, form = 'date', F1

        # Build the list of SingleTimeData instances from the data
        self.data = [SingleTimeData(x, self._timezone) for x in data['data']]
        # Build the list of corresponding 'str' dates
        self.dates_str = [x[date_col].strftime(form) for x in self.data]
        # Build the list of corresponding 'datetime' dates
        self.dates_dt = [x[date_col] for x in self.data]

        # If summary is present, save it
        if 'summary' in data:
            self.summary = data['summary']

    def __repr__(self):
        """
        Override __repr__ to have usefull text when attepting to print
        """
        # Shortcut for the class name
        c = self.__class__.__name__
        # For empty instances, we cannot print any info__
        if len(self) == 0:
            return '<Empty instance of {}>'.format(c)
        # For non-empty instances, we print the timesteps range
        return '<Instance of {} ({}) with {} timesteps from {} to {}>'.format(
            c, self.data_type, len(self), self.dates_str[0],
            self.dates_str[-1])

    def __len__(self):
        """
        Override __len__ to support len() calls to the instance
        """
        try:
            return len(self.data)
        except AttributeError:
            return 0

    def __getitem__(self, attr):
        """
        Override __getitem__ to allow variable access using [] operator

        We want to use the operator to acces wanted timestep. We support
        integer (classic 0-based index), string (using YYYY-MM-DDTHH:MM:SS or
        YYYY-MM-DD format) or datetime (both localized or unlocalized).
        """
        if len(self) == 0:
            raise EmptyInstanceError()
        # For ints, we simply return the data with given index
        if isinstance(attr, int):
            return self.data[attr]
        """
        For string, we use 'dates_str' list and return the data with
        'date'/'day' corresponding to first occurence in 'date_str'. On long
        day, there can be two timesteps with the same string representation of
        the datetime, which is why the 'first occurence' is mentioned here.
        """
        if isinstance(attr, str):
            if attr not in self.dates_str:
                raise InvalidStrIndexError(attr)
            return self.data[self.dates_str.index(attr)]
        # For datetimes, we localize it if necessary and use 'dates_dt' list
        if isinstance(attr, datetime):
            if attr.tzinfo is None:
                attr = pytz.timezone(self._timezone).localize(attr)
            if attr not in self.dates_dt:
                raise InvalidDatetimeIndexError(attr)
            return self.data[self.dates_dt.index(attr)]

        raise InvalidIndexTypeError(attr)


class Forecast:
    """
    Class that represents point forecast


    Attributes
    ----------
    lat : float
        Actual latitude of the point
    lon : float
        Actual longitude of the point
    elevation : int
        Elevation of the location
    timezone : str
        Timezone str identifier in pytz notation
    units : str
        Units set of the data
    current : SingleTimeData
        The data from 'current' section
    minutely : MultipleTimesData
        The data from 'minutely' section
    hourly : MultipleTimesData
        The data from 'hourly' section
    daily : MultipleTimesData
        The data from 'daily' section
    """
    def __init__(self, data):
        lat, lon = data['lat'], data['lon']
        # Parse the lat, lon string values to floats
        self.lat = float(lat[:-1]) if lat[-1] == 'N' else -float(lat[:-1])
        self.lon = float(lon[:-1]) if lon[-1] == 'E' else -float(lon[:-1])
        self.elevation = data['elevation']
        self.timezone = data['timezone']
        self.units = data['units']

        self.current = SingleTimeData(data.get('current', None), self.timezone)
        self.minutely = MultipleTimesData(data.get('minutely', None),
                                          'minutely', self.timezone)
        self.hourly = MultipleTimesData(data.get('hourly', None),
                                        'hourly', self.timezone)
        self.daily = MultipleTimesData(data.get('daily', None),
                                       'daily', self.timezone)

    def __repr__(self):
        """
        Override __repr__ to have usefull text when attepting to print
        """
        return '<Forecast for lat: {}, lon: {}>'.format(self.lat, self.lon)

    def __getitem__(self, attr):
        """
        Override __getitem__ to allow variable access using [] operator
        """
        return getattr(self, attr)
