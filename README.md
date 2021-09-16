pymeteosource - Weather API library
==========

Python wrapper library for [Meteosource weather API](https://www.meteosource.com) that provides detailed hyperlocal weather forecasts for any location on earth.


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

To initialize the `Meteosource` object, you need your API key and the name your subscription plan (tier). The basic example of initialization is shown below:

```python
from datetime import datetime, timedelta
from pymeteosource.api import Meteosource
from pymeteosource.types import tiers

# Change this to your actual API key
YOUR_API_KEY = 'abcdefghijklmnopqrstuvwxyz0123456789ABCD'
# Change this to your actual tier
YOUR_TIER = tiers.PREMIUM

# Initialize the main Meteosource object
meteosource = Meteosource(YOUR_API_KEY, YOUR_TIER)
```

## Get the weather forecast

To get the weather data for given place, use `get_point_forecast()` method of the `Meteosource` object. You have to specify either the coordinates of the place (`lat` + `lon`) or the `place_id`.

Note that the default timezone is always `UTC`, as opposed to the API itself (which defaults to the point's local timezone). This is because the library always queries the API for the `UTC` timezone to avoid ambiguous datetimes problems. If you specify a different timezone, the library still requests the API for `UTC`, and then converts the datetimes to desired timezone.

Note, that all time strings from the API response are converted to timezone-aware `datetime`s.

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


## Working with the weather forecasts
All of the pymeteosource's data objects have overloaded `__repr__()` methods, so you can `print` the objects them to get useful information about them:
```python
print(forecast)  # <Forecast for lat: 37.7775, lon: -122.416389>
```

### Attribute access

The library loads the JSON response into its internal structures. You can access the attributes using the dot operator (`.`), or the index operator (`[]`):

```python
# You can access all of the attributes with dot operator:
forecast.lat  # 37.7775

# ... or with index operator:
forecast['lon']  # -122.416389

# There is also information about the elevation of the point and the timezone
forecast.elevation  # 72
forecast.timezone  # 'US/Pacific'
```

### Forecast sections

There are 4 weather forecast sections (`current`, `minutely`, `hourly` and `daily`) as attributes in the `Forecast` object.

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

### Time indexing

As mentioned above, the `minutely`, `hourly` and `daily` sections contain forecasts for a single points in time. To get the forecast for a single point in time, you have several options.

  **1. Indexing with integer**

You can simply index an instance of `MultipleTimesData` with `int`, as the offset from the current time:

```python
forecast.hourly[0]
```

  **2. Indexing with string**

To get the exact time, you can use `str` in `YYYY-MM-DDTHH:00:00` format. The datetime string is assumed to be in the same timezone as the data.
```python
# Get a date in near future for which there are data in the current API response
current_date = (datetime.now() + timedelta(hours=48)).strftime("%Y-%m-%dT%H:00:00")
forecast.hourly[current_date]
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
```


### Variable access

To get the list of available variables, use `get_members` method:

```python
forecast.current.get_members()  # ['cloud_cover', 'dew_point', ..., 'wind_chill']
```

To access the variable, you can use the dot operator (`.`), or the index operator (`[]`):
```python
forecast.current.temperature
forecast.hourly[0]['temperature']
```

Some variables are grouped into logical groups, just like in the API response. You can access the actual data with chained dot or index operators:
```python
forecast.current.wind.get_members()  # ['angle', 'dir', 'gusts', 'speed']
forecast.current.wind.speed
```

### Export to pandas

If you have `pandas` package installed, you can export any of the sections to `pandas` `DataFrame`. If you export the current data, you get a `DataFrame` with a single row (as there is only 1 timestep). If you export any other section, you get a row for each timestep.

The nested sections (for example `wind.angle`) are flattened, and the column names are created by concatenating them with `_`. So for example, instead of `wind.angle`, you get column named `wind_angle`.

The `day` (in the daily data) or `date` (in minutely and hourly data) is used as `pandas` `DateTimeIndex`.

```python
df = forecast.hourly.to_pandas()
print(df)
```


### Contact us

You can contact us [here](https://www.meteosource.com/contact).
