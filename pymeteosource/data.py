"""Module with classes that represent the API data"""

from warnings import warn
from datetime import datetime, date
import pytz

from .types.time_formats import F1, F2
from .types.icons import ICONS
from .errors import (InvalidStrIndexError, InvalidIndexTypeError,
                     InvalidDatetimeIndexError, EmptyInstanceError,
                     InvalidClassType, InvalidAlertIndexTypeError,
                     InvalidDateFormat)


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
                    if key in ('date', 'rise', 'set', 'onset', 'expires'):
                        # Convert to datetime
                        dt = datetime.strptime(value, F1)
                        # Localize from UTC
                        value = pytz.utc.localize(dt).astimezone(tz)
                    # Items that only contain day (not hours, etc.)
                    if key == 'day':
                        # Only convert to datetime
                        if not isinstance(value, date):
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
        if isinstance(self, (MultipleTimesData, AlertsData)):
            # pylint: disable=E1101
            df = pd.DataFrame([x.to_dict() for x in self.data])
        # This is also possible, but results in 1-row DataFrame
        elif isinstance(self, SingleTimeData):
            df = pd.DataFrame([self.to_dict()])  # pylint: disable=E1101
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
        date = getattr(self, 'date', getattr(self, 'day', 'current'))
        if getattr(self, 'expires', None):
            date = 'alert'
        return ('<Instance of {} ({}) with {} member variables ({})>'.format(
            c, date, len(members), ', '.join(members)))

    def __getitem__(self, attr):
        """
        Override __getitem__ to allow variable access using [] operator
        """
        return getattr(self, attr)


class AlertsData(BaseData):
    """
    Class that represents alerts data

    Attributes
    ----------
    data : list
        List of SingleTimeData instances, each containing single alert

    Methods
    -------
    get_active_alerts : list
        Get all alerts that are active at given time
    """

    def __init__(self, data, timezone):
        """
        :param dict: The alerts data from the API
        :param str: String identifier of used timezone
        """
        # Call the parent's constructor to initialize the timezone
        super().__init__(timezone)
        # Keep empty instance if no data are available
        if data is None:
            return

        # Build the list of SingleTimeData instances from the data
        self.data = [SingleTimeData(x, self._timezone) for x in data['data']]

    def get_active_alerts(self, orig_dt=None):
        """
        Get all alerts that are active at given time

        :param None/str/datetime: If None, assume current time.
                                  String in YYYY-MM-DDTHH:MM:SS format.
                                  If datetime is tz-non aware, data timezone is assumed.
        :return list: List of SingleTimeData representing alerts active at given time
        """
        # Initialize pytz timezone object using the data's timezone
        tz = pytz.timezone(self._timezone)

        # If orig_dt is None, we use current time
        if orig_dt is None:
            dt = datetime.now(tz)
        # For strings, we first convert to datetime and then make if tz-aware
        elif isinstance(orig_dt, str):
            try:
                orig_dt = datetime.strptime(orig_dt, F1)
            except ValueError as ex:
                raise InvalidDateFormat(orig_dt, F1) from ex
            dt = tz.localize(orig_dt)
        # For datetimes
        elif isinstance(orig_dt, datetime):
            # If it is tz-naive, we set the tzinfo
            if orig_dt.tzinfo is None:
                dt = tz.localize(orig_dt)
            else:
                # Else we just copy it
                dt = orig_dt
        else:
            raise InvalidClassType(type(orig_dt))

        # Return all Alerts that are active at 'dt' time
        return [x for x in self.data if x.onset <= dt <= x.expires]

    def __repr__(self):
        """
        Override __repr__ to have usefull text when attepting to print
        """
        c = self.__class__.__name__
        return '<Instance of {} containing {} alerts>'.format(c, len(self.data))

    def __getitem__(self, attr):
        """
        Override __getitem__ to allow variable access using [] operator
        """
        # We only allow integer indices
        if not isinstance(attr, int):
            raise InvalidAlertIndexTypeError(type(attr))
        # Raise when trying to index empty instance
        if len(self.data) == 0:
            raise EmptyInstanceError()

        return self.data[attr]

    def __len__(self):
        """
        Override __len__ to support len() calls to the instance
        """
        try:
            return len(self.data)
        except AttributeError:
            return 0

    def __iter__(self):
        """
        Override __iter__ to support alert iterator
        """
        return iter(self.data)


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
    Class that represents data in multiple points in time

    This class is used to represent 'current' section, and the individual
    timesteps of 'minutely', 'hourly', 'daily' or 'time_machine'.

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
        if self.data_type in ('daily', 'statistics'):
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

    def append(self, other):
        """
        Append another MultipleTimesData instance

        :param MultipleTimesData: The instance to append to this one
        """
        # Check the type
        if type(other) is not MultipleTimesData: # pylint: disable=C0123
            raise InvalidClassType(type(other))

        # Append all data structures
        self.data += other.data
        self.dates_str += other.dates_str
        self.dates_dt += other.dates_dt

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
            c, self.data_type, len(self), min(self.dates_str),
            max(self.dates_str))

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
            # If the datetime is naive
            if attr.tzinfo is None:
                attr = pytz.timezone(self._timezone).localize(attr)
            else:
                # If it is tz-aware, we convert it to the same timezone
                attr = attr.astimezone(pytz.timezone(self._timezone))
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
    def __init__(self, data, tz):
        lat, lon = data['lat'], data['lon']
        # Parse the lat, lon string values to floats
        self.lat = float(lat[:-1]) if lat[-1] == 'N' else -float(lat[:-1])
        self.lon = float(lon[:-1]) if lon[-1] == 'E' else -float(lon[:-1])
        self.elevation = data['elevation']
        self.timezone = tz
        self.units = data['units']

        self.current = SingleTimeData(data.get('current', None), self.timezone)
        self.minutely = MultipleTimesData(data.get('minutely', None),
                                          'minutely', self.timezone)
        self.hourly = MultipleTimesData(data.get('hourly', None),
                                        'hourly', self.timezone)
        self.daily = MultipleTimesData(data.get('daily', None),
                                       'daily', self.timezone)
        self.alerts = AlertsData(data.get('alerts', None), self.timezone)

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


class TimeMachine:
    """
    Class that represents time machine archive data


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
    data : MultipleTimesData
        The acutal archive data
    statistics : MultipleTimesData
        Long term normals (statistics)

    Methods
    -------
    to_pandas
        Export the data to pandas DataFrame
    """
    def __init__(self, data, tz, day):
        lat, lon = data['lat'], data['lon']
        # Parse the lat, lon string values to floats
        self.lat = float(lat[:-1]) if lat[-1] == 'N' else -float(lat[:-1])
        self.lon = float(lon[:-1]) if lon[-1] == 'E' else -float(lon[:-1])
        self.elevation = data['elevation']
        self.timezone = tz
        self.units = data['units']
        self.data = MultipleTimesData(data, 'time_machine', self.timezone)
        # Preprocess statistics to fit data structures
        statistics = {'data': [{'statistics': data['statistics']}]}
        statistics['data'][0]['day'] = day
        self.statistics = MultipleTimesData(statistics, 'statistics', 'UTC')

        # Assing human-readable weather category from icon number
        for x in self.data.data:
            x.weather = ICONS.get(x.icon, 1)['weather']
            x.weather_id = ICONS.get(x.icon, 1)['weather_id']

    def append(self, other):
        """
        Append another TimeMachine instance's data to this instance

        :param TimeMachine: TimeMachine instance to be appended
        """
        # Call MultipleTimesData's 'append' method
        self.data.append(other.data)
        self.statistics.append(other.statistics)

    def __repr__(self):
        """
        Override __repr__ to have usefull text when attepting to print
        """
        return '<TimeMachine for lat: {}, lon: {}>'.format(self.lat, self.lon)

    def __getitem__(self, attr):
        """
        Override __getitem__ to allow variable access using [] operator
        """
        return getattr(self, attr)

    def to_pandas(self, include_statistics=False):
        """
        Export the data to pandas DataFrame

        NOTE: This needs 'pandas' module, which is not needed for any other
        parts of pymeteosource. Because of this, it is not installed by default
        setup.py to keep the dependencies as minimal as possible. To use this
        feature, use 'pip install pymeteosource[pandas]' to install this
        package, or install pandas manually using 'pip install pandas'.

        :param bool: If True, includes daily long term statistics epanded to hours
        :return pandas.DataFrame: The DataFrame with 'date' as index
        """
        res = self.data.to_pandas()
        if not include_statistics:
            return res

        # Convert statistics to pandas
        stats = self.statistics.to_pandas()
        # Create helper column to merge the data on
        res['day'] = res.index.tz_convert('UTC').date

        # Merge the data with statistics and reset index to original
        res = res.reset_index().merge(stats, on='day', how='left').set_index('date')
        # Drop the helper column
        res = res.drop('day', axis=1)

        return res
