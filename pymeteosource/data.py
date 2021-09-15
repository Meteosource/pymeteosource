from warnings import warn
from datetime import datetime
import pytz
from .types.time_formats import F1
from .errors import (InvalidStrIndex, InvalidIndexType,
                     InvalidDatetimeIndex)

class BaseData:
    def __init__(self, timezone):
        self._timezone = timezone

    def load_data(self, data):
        tz = pytz.timezone(self._timezone)
        if data is None:
            return
        for it in data:
            val = data[it]
            if isinstance(val, dict):
                setattr(self, it, GroupData(val, self._timezone))
            else:
                if it in ('date', 'last_update'):
                    val = tz.localize(datetime.strptime(val, F1))

                setattr(self, it, val)

    def get_members(self):
        return [x for x in dir(self) if
                not callable(getattr(self, x)) and not x.startswith("_")]

    def __repr__(self):
        cname, ln = self.__class__.__name__, len(self.get_members())
        return '<Instance of {} with {} member variables>'.format(cname, ln)

    def __getitem__(self, attr):
        return getattr(self, attr)

    def to_dict(self, prefix=''):
        res = {}
        for k in self.get_members():
            val = getattr(self, k)
            if isinstance(val, BaseData):
                val = val.to_dict(prefix='{}_'.format(k))
                res.update(val)
            else:
                res['{}{}'.format(prefix, k)] = val

        return res


class GroupData(BaseData):
    def __init__(self, data, timezone):
        super().__init__(timezone)
        self.load_data(data)

    def __repr__(self):
        cname, members = self.__class__.__name__, self.get_members()
        return ('<Instance of {} with {} member variables ({})>'.format(
            cname, len(members), ', '.join(members)))


class SingleTimeData(BaseData):
    def __init__(self, data, timezone):
        super().__init__(timezone)
        self.load_data(data)


class MultipleTimesData(BaseData):
    def __init__(self, data, timezone):
        super().__init__(timezone)
        if data is None:
            return

        if 'summary' in data:
            self.summary = data['summary']

        self.data = [SingleTimeData(x, self._timezone) for x in data['data']]
        self.dates_str = [x.date.strftime(F1) for x in self.data]
        self.dates_dt = [x.date for x in self.data]

    def __repr__(self):
        cname, ln = self.__class__.__name__, len(self.data)
        return '<Instance of {} with {} timesteps>'.format(cname, ln)

    def __getitem__(self, attr):
        if isinstance(attr, int):
            return self.data[attr]
        if isinstance(attr, str):
            if attr not in self.dates_str:
                raise InvalidStrIndex(attr)
            return self.data[self.dates_str.index(attr)]
        if isinstance(attr, datetime):
            if attr not in self.dates_dt:
                raise InvalidDatetimeIndex(attr)
            return self.data[self.dates_dt.index(attr)]
        raise InvalidIndexType(attr)

    def to_pandas(self):
        try:
            import pandas as pd
        except ImportError:
            warn("Module pandas is not installed, cannot export the data. "
                 "Try to install pandas with 'pip install pandas'.")
            return None

        df = pd.DataFrame([x.to_dict() for x in self.data])
        df = df.set_index('date')

        return df


class Forecast:
    def __init__(self, data):
        lat, lon = data['lat'], data['lon']
        self.lat = float(lat[:-1]) if lat[-1] == 'N' else -float(lat[:-1])
        self.lon = float(lon[:-1]) if lon[-1] == 'E' else -float(lon[:-1])
        self.elevation = data['elevation']
        self.timezone = data['timezone']
        self.units = data['units']

        self.current = SingleTimeData(data.get('current', None), self.timezone)
        self.minutely = MultipleTimesData(data.get('minutely', None),
                                          self.timezone)
        self.hourly = MultipleTimesData(data.get('hourly', None),
                                        self.timezone)

    def __repr__(self):
        return '<Forecast for lat: {}, lon: {}>'.format(self.lat, self.lon)

    def __getitem__(self, attr):
        return getattr(self, attr)
