pymeteosource - Weather API library
==========

[Meteosource weather API](https://www.meteosource.com) provides accurate global weather data - get real-time, forecast, and historical hyperlocal data.

Meteosource weather forecasts are based on cutting-edge machine-learning models. The algorithms learn from historical data and forecasts from many [different models](https://www.meteosource.com/meteosource-technology), compare their data from different places and meteorological situations and create a single output to provide accurate hyperlocal weather forecasts anywhere in the world. Receive minute-by-minute rain forecast, detailed hour-by-hour weather forecast out to 7 days, and much more!

Using this python wrapper library, you can easily implement Meteosource JSON data into your app or service.


### Installation
The basic functionality of this library only needs `requests` and `pytz` modules. To install it with the minimal requirements, use:

```bash
pip3 install pymeteosource
```

The library has also optional feature of exporting the data to `pandas` `DataFrame`. To use it, you will also need `pandas` package. You can either install `pandas` manually, or use:

```bash
pip3 install pymeteosource[pandas]
```

### Get started

To use this library, you need to obtain your Meteosource API key. You can [sign up](https://www.meteosource.com/client/sign-up) or get the API key of existing account in [your dashboard](https://www.meteosource.com/client).


### Tests
The unit tests are written using `pytest`. As the `pandas` exporting feature is also tested, you should have `pandas` library installed. You can install both of them using:
```bash
pip3 install pytest
pip3 install pandas
```

The tests only make 2 actual requests to live API, most of the tests use mocked API response. You need to provide your actual API key using environment variable. To run the tests, use:
```bash
# Change this to your actual API key
export METEOSOURCE_API_KEY='abcdefghijklmnopqrstuvwxyz0123456789ABCD'
pytest tests
```


# Library usage

## Initialization

To initialize the `Meteosource` object, you need your API key and the name of your subscription plan (tier). Basic example of initialization is shown below:

```python
from datetime import datetime, timedelta
from pymeteosource.api import Meteosource
from pymeteosource.types import tiers

# Change this to your actual API key
YOUR_API_KEY = 'abcdefghijklmnopqrstuvwxyz0123456789ABCD'
# Change this to your actual tier
YOUR_TIER = tiers.FLEXI

# Initialize the main Meteosource object
meteosource = Meteosource(YOUR_API_KEY, YOUR_TIER)
```

## Get the weather data

Using `pymeteosource`, you can get weather forecasts or archive weather data (if you have a paid subscription).

### Forecast
To get the weather data for given place, use `get_point_forecast()` method of the `Meteosource` object. You have to specify either the coordinates of the place (`lat` + `lon`) or the `place_id`. Detailed description of the parameters can be found in the [API documentation](https://www.meteosource.com/documentation).

Note that the default timezone is always `UTC`, as opposed to the API itself (which defaults to the point's local timezone). This is because the library always queries the API for the `UTC` timezone to avoid ambiguous datetimes problems. If you specify a different timezone, the library still requests the API for `UTC`, and then converts the datetimes to desired timezone.

Note that all time strings from the API response are converted to timezone-aware `datetime` objects.

```python
from pymeteosource.types import sections, langs, units

# Get the forecast for given point
forecast = meteosource.get_point_forecast(
    lat=37.7775,  # Latitude of the point
    lon=-122.416389,  # Longitude of the point
    place_id=None,  # You can specify place_id instead of lat+lon
    sections=[sections.CURRENT, sections.HOURLY],  # Defaults to '("current", "hourly")'
    tz='US/Pacific',  # Defaults to 'UTC', regardless of the point location
    lang=langs.ENGLISH,  # Defaults to 'en'
    units=units.US  # Defaults to 'auto'
)
```

### Historical weather
Users with paid subscription to Meteosource can retrieve historical weather and long-term statistics from `time_machine` endpoint, using `get_time_machine()` method:

```python
# Get the historical weather
time_machine = meteosource.get_time_machine(
    date='2019-12-25',  # You can also pass list/tuple/set of dates, which can be 'str' or 'datetime' objects
    date_from=None,  # You can specify the range for dates you need, instead of list
    date_to=None,  # You can specify the range for dates you need, instead of list
    place_id='london',  # ID of the place you want the historical weather for
    lat=None,  # You can specify lat instead of place_id
    lon=None,  # You can specify lon instead of place_id
    tz='UTC',  # Defaults to 'UTC', regardless of the point location
    units=units.US  # Defaults to 'auto'
)
```
Note, that the historical weather data and long-term statistics are always retrieved for full UTC days. If you specify a different timezone, the datetimes get converted, but they will cover the full UTC, not the local day. If you specify a `datetime` to any of the date parameters, the hours, minutes, seconds and microseconds get ignored. So if you request `date='2021-12-25T23:59:59'`, you get data for full UTC day `2021-12-25`.

If you pass `list`/`tuple`/`set` of dates to `date` parameter, they days will be inserted into the inner structures in the order they are being iterated over. This affects time indexing by integer (see below). An API request is made for each day, even when you specify a date range.

## Working with the weather data
All of the pymeteosource's data objects have overloaded `__repr__()` methods, so you can `print` the objects them to get useful information about them:
```python
print(forecast)  # <Forecast for lat: 37.7775, lon: -122.416389>
print(time_machine)  # <TimeMachine for lat: 51.50853, lon: -0.12574>
```

### Attribute access

The library loads the JSON response into its internal structures. You can access the attributes using the dot operator (`.`), or the index operator (`[]`):

```python
# You can access all of the attributes with dot operator:
forecast.lat  # 37.7775

# ... or with index operator:
forecast['lon']  # -122.416389

# There is also information about the elevation of the point and the timezone
time_machine.elevation  # 82
time_machine.timezone  # 'UTC'
```

### Weather data sections

There are 5 weather forecast sections (`current`, `minutely`, `hourly`, `daily` and `alerts`) as attributes in the `Forecast` object.

The `current` data contains data for many variables for a single point in time (it is represented by `SingleTimeData` object):

```python
# <Instance of SingleTimeData (current) with 17 member variables (cloud_cover,
#  dew_point, feels_like, humidity, icon, icon_num, irradiance, ozone,
#  precipitation, pressure, summary, temperature, uv_index, visibility,
#  wind, wind_chill)>
print(forecast.current)
```

The `minutely`, `hourly` and `daily` sections contain forecasts for more points in time (represented by `MultipleTimesData`). The sections that were not requested are empty:
```python
print(forecast.minutely)  # <Empty instance of MultipleTimesData>
print(forecast.daily)  # <Empty instance of MultipleTimesData>
```

The sections that were requested can also be `print`ed, to view number of available timesteps and their range (inclusive):
```python
# <Instance of MultipleTimesData (hourly) with 164 timesteps
#  from 2021-09-08T22:00:00 to 2021-09-15T17:00:00>
print(forecast.hourly)
```

The `alerts` section contain meteorological alerts and warnings, if there are any issued for the location. The `alerts` object is an instance of `AlertsData` class. You can print the object or iterate over it:
```python
print(forecast.alerts) # <Instance of AlertsData containing 4 alerts>
for alert in alerts:
    # <Instance of SingleTimeData (alert) with 8 member variables
    #  (certainty, description, event, expires, headline, onset, sender, severity)>
    print(alert)
```
You can also get list of all active alerts for given time. If you use `str` or tz-naive `datetime` in this function, it will suppose that it is in the same timezone as requested for the forecast.
```python
# If you pass no parameter, it checks for current time
forecast.alerts.get_active_alerts() # returns list of SingleTimeData instances
# You can use either string...
forecast.alerts.get_active_alerts('2022-03-08T22:00:00')
# ... or datetime (both tz-aware and naive)
forecast.alerts.get_active_alerts(datetime(2022, 3, 8, 23, 0, 0))
```

There are sections `data` and `statistics` for historical weather as attributes in the `TimeMachine` object, both represented by `MultipleTimesData`.
```python
print(time_machine.data)  # <Instance of MultipleTimesData (time_machine) with 24 timesteps from 2019-12-25T00:00:00 to 2019-12-25T23:00:00>
print(time_machine.statistics)  # <Instance of MultipleTimesData (statistics) with 1 timesteps from 2019-12-25 to 2019-12-25>
```

### Time indexing

As mentioned above, the `minutely`, `hourly`, `daily` sections of `Forecast` and the `data` section of `TimeMachine` contain data for more timesteps. To get the data for a single time, you have several options.

  **1. Indexing with integer**

You can simply index an instance of `MultipleTimesData` with `int`, as the offset from the current time:

```python
forecast.hourly[0]
time_machine.data[0]
```

  **2. Indexing with string**

To get the exact time, you can use `str` in `YYYY-MM-DDTHH:00:00` format. The datetime string is assumed to be in the same timezone as the data.
```python
# Get a date in near future for which there are data in the current API response
current_date = (datetime.now() + timedelta(hours=48)).strftime("%Y-%m-%dT%H:00:00")
forecast.hourly[current_date]

# Get historical weather
time_machine.data['2019-12-25T03:00:00']
```

  **3. Indexing with `datetime`**

You can also use `datetime` as an index, both timezone naive and aware. If the object is naive, it is assumed to be in the same timezone as the data. If it is aware, it is automatically converted to the timezone of the data.

```python
# Get a date in near future for which there are data in the current API response
current_dt = datetime.strptime(current_date, "%Y-%m-%dT%H:00:00")

# Index with naive datetime
forecast.hourly[current_dt]

# Index with aware datetime
import pytz
forecast.hourly[pytz.utc.localize(current_dt)].temperature

# Get historical weather
time_machine.data[datetime(2019, 12, 25, 3)]
```


### Variable access

To get the list of available variables, use `get_members` method:

```python
forecast.current.get_members()  # ['cloud_cover', 'dew_point', ..., 'wind_chill']
time_machine.data[0].get_members()  # ['cape', 'cloud_cover', ..., 'wind']
```

To access the variable, you can use the dot operator (`.`), or the index operator (`[]`):
```python
forecast.current.temperature
forecast.hourly[0]['temperature']
time_machine.data[0]['weather']  # cloudy
```

Some variables are grouped into logical groups, just like in the API response. You can access the actual data with chained dot or index operators:
```python
forecast.current.wind.get_members()  # ['angle', 'dir', 'gusts', 'speed']
forecast.current.wind.speed
time_machine.data[0]['wind'].dir  # WNW
```

### Export to pandas

If you have `pandas` package installed, you can export any of the sections to `pandas` `DataFrame`. If you export the current data, you get a `DataFrame` with a single row (as there is only 1 timestep). If you export any other section, you get a row for each timestep.

The nested sections (for example `wind.angle`) are flattened, and the column names are created by concatenating them with `_`. So for example, instead of `wind.angle`, you get column named `wind_angle`.

The `day` (in the daily data) or `date` (in minutely and hourly data) is used as `pandas` `DateTimeIndex`.

```python
df = forecast.hourly.to_pandas()
print(df)
```

For historical weather data, you can also call the method on the `TimeMachine` object directly, so all following calls are valid:
```python
time_machine.data.to_pandas()
time_machine.statistics.to_pandas()
time_machine.to_pandas()
```

You can also merge the daily statistics and the hourly historical data into single `pandas` `DataFrame`. In this case, the daily statistics are duplicated into all hours of each day:
```python
time_machine.to_pandas(include_statistics=True)
```


### Contact us

You can contact us [here](https://www.meteosource.com/contact).
