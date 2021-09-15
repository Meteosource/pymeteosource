pymeteosource
==========

Python wrapper library for Meteosource API that provides detailed hyperlocal weather forecasts for any location on earth.


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


# Example usage

```python
from datetime import datetime, timedelta
import pytz

from pymeteosource.api import Meteosource
from pymeteosource.types import tiers, sections, langs, units


# Change this to your actual API key
YOUR_API_KEY = 'abcdefghijklmnopqrstuvwxyz0123456789ABCD'
# Change this to your actual tier
YOUR_TIER = tiers.PREMIUM

# Initialize the main Meteosource object
meteosource = Meteosource(YOUR_API_KEY, YOUR_TIER)

# Get the forecast for given point
forecast = meteosource.get_point_forecast(
    lat=37.7775,  # Latitude of the point
    lon=-122.416389,  # Longitude of the point
    place_id=None,  # You can specify place_id instead of lat+lon
    sections=[sections.CURRENT, sections.HOURLY],  # Defaults to 'current,hourly'
    tz='US/Pacific',  # Defaults to 'UTC', regardless of the point location
    lang=langs.ENGLISH,  # Defaults to 'en'
    units=units.US  # Defaults to 'auto'
)


# All the objects have overloaded __repr__ method, so you can print them to get
# useful info about them:
print(forecast)  # <Forecast for lat: 37.7775, lon: -122.416389>

# You can access all of the attributes with dot operator:
forecast.lat  # 37.7775

# ... or with bracket operator:
forecast['lon']  # -122.416389

# There is also information about the elevation of the point and the timezone
forecast.elevation  # 72
forecast.timezone  # 'US/Pacific'


# The current data contains data for many variables for a single point in time
# (represented by SingleTimeData). You can also print the instance, which gives:
#
# <Instance of SingleTimeData (current) with 17 member variables (cloud_cover,
#  dew_point, feels_like, humidity, icon, icon_num, irradiance, ozone,
#  precipitation, pressure, summary, temperature, uv_index, visibility,
#  wind, wind_chill)>
print(forecast.current)


# To get the list of available variables, use `get_members` method:
forecast.current.get_members()  # ['cloud_cover', 'dew_point', ..., 'wind_chill']

# Again, you can access the variables using the '.' operator
forecast.current.temperature
# ... or with the bracket operator
forecast.current['temperature']

# Some variables are grouped into logical groups, just like in the API response.
forecast.current.wind.get_members()  # ['angle', 'dir', 'gusts', 'speed']
# You can access the actual data with chained access operators:
forecast.current.wind.speed


# The minutely, hourly and daily sections contain forecasts for more points
# in time (represented by MultipleTimesData).
# The sections that are not requested are empty:
print(forecast.minutely)  # <Empty instance of MultipleTimesData>
print(forecast.daily)  # <Empty instance of MultipleTimesData>

# The sections that are requested can be printed, which shows number
# of available timesteps and their range (inclusive):
#
# <Instance of MultipleTimesData (hourly) with164 timesteps
#  from 2021-09-08T22:00:00 to 2021-09-15T17:00:00>
print(forecast.hourly)


# To get hourly forecast for the specific time, you can acces the hourly data with integer:
forecast.hourly[0].temperature

# Get a date in near future for which there are data in the current API response
current_date = (datetime.now() + timedelta(hours=48)).strftime("%Y-%m-%dT%H:00:00")

# ... or with string representation of wanted time in YYYY-MM-DDTHH:MM:SS format:
forecast.hourly[current_date].temperature

current_dt = datetime.strptime(current_date, "%Y-%m-%dT%H:00:00")
# ... or with unlocalized datetime (is localized into the data's timezone automatically):
forecast.hourly[current_dt].temperature

# ... or with localized datetime (which is automatically converted to the data's timezone)
forecast.hourly[pytz.utc.localize(current_dt)].temperature

# Note, that all time strings from the API response are converted to tz-aware
# datetimes:
type(forecast.hourly[0].date)  # <class 'datetime.datetime'>


# You can export any of the individual sections to pandas DataFrame:
df = forecast.hourly.to_pandas()

# The nested sections (for example wind.angle) are flattened, and the column
# names are created by concatenating them with '_'. So for example, instead
# of wind.angle, you get column with name 'wind_angle'.
#
# The day (in the daily data) or date (in the other sections) is used as
# pandas DateTimeIndex.
print(df)
```


### Contact us.

You can contact us [here](https://www.meteosource.com/contact).
