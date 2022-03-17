"""Tests for pymeteosource"""

import os
import sys
from datetime import datetime, date
from unittest.mock import MagicMock
from os.path import realpath, join, dirname
import pytz
import pytest
import pandas

from pymeteosource.api import Meteosource
from pymeteosource.types import tiers, endpoints, units, sections
from pymeteosource.types.time_formats import F1
from pymeteosource.data import (Forecast, SingleTimeData, MultipleTimesData,
                                AlertsData)
from pymeteosource.errors import (InvalidArgumentError, InvalidIndexTypeError,
                                  InvalidStrIndexError, EmptyInstanceError,
                                  InvalidDatetimeIndexError, InvalidDateFormat,
                                  InvalidDateSpecification, InvalidDateRange)

from .sample_data import SAMPLE_POINT, SAMPLE_TIME_MACHINE
from .dst_changes_data import LONG_DAY
from .variables_list import (CURRENT, PRECIPITATION_CURRENT, WIND, MINUTELY,
                             HOURLY, CLOUD, PRECIPITATION, PROBABILITY, DAILY,
                             ALL_DAY, PART_DAY, ASTRO, SUN, MOON, STATS,
                             STATS_TEMP, STATS_WIND, STATS_PREC, ALERTS)

sys.path.insert(0, realpath(join(dirname(__file__), "..")))

# Load API key from environment variable
API_KEY = os.environ.get('METEOSOURCE_API_KEY')
if API_KEY is None:
    raise ValueError("You need to provide API key as environment variable.")


def test_to_dst_changes():
    """Test exporting to pandas"""
    m = Meteosource(API_KEY, tiers.FLEXI)
    # We mock the API requests with sample data
    m.req_handler.execute_request = MagicMock(return_value=LONG_DAY)
    # Get the mocked forecast
    f = m.get_point_forecast(place_id='london', tz='Europe/Prague')
    # Check the ambiguous date is handled properly
    dts = ['2021-10-31T01:00:00', '2021-10-31T02:00:00',
           '2021-10-31T02:00:00', '2021-10-31T03:00:00']
    assert f.hourly.dates_str == dts

    # Check the astro datetimes are OK when DST changes
    tz = pytz.timezone('Europe/Prague')
    dt = tz.localize(datetime(2021, 10, 31, 1, 24, 35), is_dst=None)
    assert f.daily[0].astro.sun.rise == dt
    dt = tz.localize(datetime(2021, 10, 31, 2, 24, 35), is_dst=True)
    assert f.daily[0].astro.sun.set == dt
    dt = tz.localize(datetime(2021, 10, 31, 2, 24, 35), is_dst=False)
    assert f.daily[0].astro.moon.rise == dt
    dt = tz.localize(datetime(2021, 10, 31, 3, 24, 35), is_dst=None)
    assert f.daily[0].astro.moon.set == dt


def test_build_url():
    """Test URL building"""
    url = 'https://www.meteosource.com/api/v1/%s/%s'
    for tier in [tiers.FLEXI, tiers.STANDARD, tiers.STARTUP, tiers.FREE]:
        for endpoint in [endpoints.POINT, endpoints.TIME_MACHINE]:
            m = Meteosource(API_KEY, tier)
            assert m._build_url(endpoint) == url % (tier, endpoint)


def test_get_point_forecast_exceptions():
    """Test detection of invalid point specification detection"""
    m = Meteosource(API_KEY, tiers.FLEXI)
    # We mock the API requests with sample data
    m.req_handler.execute_request = MagicMock(return_value=SAMPLE_POINT)

    # Test invalid place definitions
    with pytest.raises(InvalidArgumentError) as e:
        m.get_point_forecast(place_id='london', lat=50)
    assert str(e.value) == 'Only place_id or lat+lon can be specified!'
    with pytest.raises(InvalidArgumentError) as e:
        m.get_point_forecast(place_id='london', lon=14)
    assert str(e.value) == 'Only place_id or lat+lon can be specified!'
    with pytest.raises(InvalidArgumentError) as e:
        m.get_point_forecast(place_id='london', lat=50, lon=14)
    assert str(e.value) == 'Only place_id or lat+lon can be specified!'
    with pytest.raises(InvalidArgumentError) as e:
        m.get_point_forecast(lat=50)
    assert str(e.value) == 'Only place_id or lat+lon can be specified!'
    with pytest.raises(InvalidArgumentError) as e:
        m.get_point_forecast(lon=14)
    assert str(e.value) == 'Only place_id or lat+lon can be specified!'
    with pytest.raises(InvalidArgumentError) as e:
        m.get_point_forecast()
    assert str(e.value) == 'Only place_id or lat+lon can be specified!'

    # Test valid place definitions
    m.get_point_forecast(place_id='london')
    m.get_point_forecast(lat=50, lon=14)


def test_get_time_machine_exceptions():
    """Test date specification for get_time_machine"""
    m = Meteosource(API_KEY, tiers.FLEXI)
    # We mock the API requests with sample data
    m.req_handler.execute_request = MagicMock(return_value=SAMPLE_TIME_MACHINE)

    # Test invalid dates
    with pytest.raises(InvalidDateFormat) as e:
        m.get_time_machine(date='2021-01-0', place_id='london')
    assert str(e.value) == 'Invalid date "2021-01-0", should be "%Y-%m-%d"'
    with pytest.raises(InvalidDateFormat) as e:
        m.get_time_machine(date='fgh', place_id='london')
    assert str(e.value) == 'Invalid date "fgh", should be "%Y-%m-%d"'
    with pytest.raises(InvalidDateFormat) as e:
        m.get_time_machine(date=5, place_id='london')
    assert 'str or date instance' in str(e.value)

    # Test invalid date specifications
    with pytest.raises(InvalidDateSpecification) as e:
        m.get_time_machine(place_id='london')
    assert str(e.value) == 'Specify either "date" or "date_from" and "date_to"'
    with pytest.raises(InvalidDateSpecification) as e:
        m.get_time_machine(date='2021-01-01', date_to='2021-01-02',
                           place_id='london')
    assert str(e.value) == 'Specify either "date" or "date_from" and "date_to"'
    with pytest.raises(InvalidDateSpecification) as e:
        m.get_time_machine(date='2021-01-01', date_from='2021-01-02',
                           place_id='london')
    assert str(e.value) == 'Specify either "date" or "date_from" and "date_to"'
    with pytest.raises(InvalidDateSpecification) as e:
        m.get_time_machine(date_to='2021-01-02', place_id='london')
    assert str(e.value) == 'Specify either "date" or "date_from" and "date_to"'
    with pytest.raises(InvalidDateSpecification) as e:
        m.get_time_machine(date_from='2021-01-02', place_id='london')
    assert str(e.value) == 'Specify either "date" or "date_from" and "date_to"'
    with pytest.raises(InvalidDateSpecification) as e:
        m.get_time_machine(date='2021-01-01', date_from='2021-01-01',
                           date_to='2021-01-02', place_id='london')
    assert str(e.value) == 'Specify either "date" or "date_from" and "date_to"'

    # Test invalid date range
    with pytest.raises(InvalidDateRange) as e:
        m.get_time_machine(date_from='2021-01-03',
                           date_to=datetime(2021, 1, 3, 23, 59),
                           place_id='london')
    assert 'is not smaller than "date_to"' in str(e.value)

    # Test valid date definitions
    m.get_time_machine(date='2021-01-01', place_id='london')
    m.get_time_machine(date=['2021-01-01', datetime(2021, 1, 2)],
                       place_id='london')
    m.get_time_machine(date_from='2021-01-01', date_to=datetime(2021, 1, 3),
                       place_id='london')
    m.get_time_machine(date_from='2021-01-01', date_to=date(2021, 1, 3),
                       place_id='london')


def test_forecast_indexing():
    """Test indexing MultipleTimesData with int, string and datetimes"""
    m = Meteosource(API_KEY, tiers.FLEXI)
    # We mock the API requests with sample data
    m.req_handler.execute_request = MagicMock(return_value=SAMPLE_POINT)
    # Get the mocked forecast
    f = m.get_point_forecast(place_id='london', tz='UTC')

    # Index by int
    assert f.hourly[1].wind.angle == 106

    # Index by too large int
    with pytest.raises(IndexError):
        assert f.hourly[1000]

    # Index by string
    assert f.hourly['2021-09-08T11:00:00'].feels_like == 23.2

    # Index by string with wrong format
    with pytest.raises(InvalidStrIndexError):
        f.hourly['2021-09-08 11:00:00']  # pylint: disable=W0104

    # Index by unsupported type
    with pytest.raises(InvalidIndexTypeError):
        f.hourly[1.1]  # pylint: disable=W0104

    # Index by tz-naive datetime
    dt = datetime.strptime('2021-09-09T00:00:00', F1)
    assert f.hourly[dt].probability.precipitation == 61

    # Index by tz-aware datetime but in different tz
    dt1 = pytz.timezone('UTC').localize(dt)
    assert f.hourly[dt1].probability.precipitation == 61

    # Index by tz-aware datetime
    dt1 = pytz.timezone('Europe/London').localize(dt)
    assert f.hourly[dt1].probability.precipitation == 21

    # Index by tz-aware datetime but with wrong timezone
    dt2 = pytz.timezone('Asia/Kabul').localize(dt)
    with pytest.raises(InvalidDatetimeIndexError) as e:
        f.hourly[dt2]  # pylint: disable=W0104
    assert 'Invalid datetime index' in str(e.value)

    # Check timezone settings
    f = m.get_point_forecast(place_id='london', tz='Europe/London')
    dt = pytz.timezone('Europe/London').localize(datetime(2021, 9, 8, 10))
    assert f.hourly[0].date == dt

    f = m.get_point_forecast(place_id='london', tz='Europe/Prague')
    dt = pytz.timezone('Europe/Prague').localize(datetime(2021, 9, 8, 11))
    assert f.hourly[0].date == dt

    f = m.get_point_forecast(place_id='london', tz='Asia/Kabul')
    dt = pytz.timezone('Asia/Kabul').localize(datetime(2021, 9, 8, 13, 30))
    assert f.hourly[0].date == dt


def test_to_pandas():
    """Test exporting to pandas"""
    m = Meteosource(API_KEY, tiers.FLEXI)
    # We mock the API requests with sample data
    m.req_handler.execute_request = MagicMock(return_value=SAMPLE_POINT)
    # Get the mocked forecast
    f = m.get_point_forecast(place_id='london')

    df = f.current.to_pandas()
    assert len(df) == 1

    df = f.minutely.to_pandas()
    assert len(df) == 116
    assert isinstance(df.index, pandas.core.indexes.datetimes.DatetimeIndex)

    df = f.hourly.to_pandas()
    assert len(df) == 155
    assert isinstance(df.index, pandas.core.indexes.datetimes.DatetimeIndex)

    df = f.daily.to_pandas()
    assert len(df) == 30
    assert isinstance(df.index, pandas.core.indexes.datetimes.DatetimeIndex)

    df = f.alerts.to_pandas()
    assert len(df) == 4


def test_to_dict():
    """Test exporting to pandas"""
    m = Meteosource(API_KEY, tiers.FLEXI)
    # We mock the API requests with sample data
    m.req_handler.execute_request = MagicMock(return_value=SAMPLE_POINT)
    # Get the mocked forecast
    f = m.get_point_forecast(place_id='london')

    # Test multilevel dict flattening
    assert 'afternoon_wind_angle' in f.daily[0].to_dict()


def test_forecast_structure():
    """Test structure of the Forecast object on real data"""
    # Initialize the Meteosource object
    m = Meteosource(API_KEY, tiers.FLEXI)
    # Get real forecast data (not mocked)
    f = m.get_point_forecast(place_id='london', tz='Asia/Kabul',
                             units=units.METRIC, sections=sections.ALL)

    # Check if the header is correct
    assert isinstance(f, Forecast)
    assert f.lat == 51.50853
    assert f.lon == -0.12574
    assert f.elevation == 25
    assert f.timezone == 'Asia/Kabul'
    assert f.units == 'metric'

    # Check types of the sections
    assert isinstance(f.current, SingleTimeData)
    assert isinstance(f.minutely, MultipleTimesData)
    assert isinstance(f.hourly, MultipleTimesData)
    assert isinstance(f.daily, MultipleTimesData)

    # Check current section
    assert set(f.current.get_members()) == CURRENT
    assert set(f.current.wind.get_members()) == WIND  # pylint: disable=E1101
    # pylint: disable=E1101
    assert set(f.current.precipitation.get_members()) == PRECIPITATION_CURRENT

    # Check minutely section
    assert isinstance(f.minutely.summary, str)
    assert isinstance(f.minutely, MultipleTimesData)
    assert len(f.minutely) > 0
    assert set(f.minutely[0].get_members()) == MINUTELY
    assert isinstance(f.minutely[0].date, datetime)

    # Check hourly section
    assert isinstance(f.hourly, MultipleTimesData)
    assert len(f.hourly) > 0
    assert set(f.hourly[0].get_members()) == HOURLY
    assert set(f.hourly[0].wind.get_members()) == WIND
    assert set(f.hourly[0].cloud_cover.get_members()) == CLOUD
    assert set(f.hourly[0].precipitation.get_members()) == PRECIPITATION
    assert set(f.hourly[0].probability.get_members()) == PROBABILITY

    # Check daily section
    assert isinstance(f.daily, MultipleTimesData)
    assert set(f.daily[0].get_members()) == DAILY
    assert isinstance(f.daily[0].day, datetime)
    assert set(f.daily[0].all_day.get_members()) == ALL_DAY
    assert set(f.daily[0].all_day.wind.get_members()) == WIND
    assert set(f.daily[0].morning.get_members()) == PART_DAY
    assert set(f.daily[0].morning.wind.get_members()) == WIND
    assert set(f.daily[0].afternoon.get_members()) == PART_DAY
    assert set(f.daily[0].afternoon.wind.get_members()) == WIND
    assert set(f.daily[0].evening.get_members()) == PART_DAY
    assert set(f.daily[0].evening.wind.get_members()) == WIND
    assert set(f.daily[0].astro.get_members()) == ASTRO
    assert set(f.daily[0].astro.sun.get_members()) == SUN
    assert set(f.daily[0].astro.moon.get_members()) == MOON
    assert set(f.daily[0].statistics.get_members()) == STATS
    assert set(f.daily[0].statistics.temperature.get_members()) == STATS_TEMP
    assert set(f.daily[0].statistics.wind.get_members()) == STATS_WIND
    assert set(f.daily[0].statistics.precipitation.get_members()) == STATS_PREC

    # Check alerts section
    assert isinstance(f.alerts, AlertsData)

    # Check correct exception raising when minutely data are not present
    m = Meteosource(API_KEY, tiers.FREE)
    # Get real forecast data (not mocked)
    f = m.get_point_forecast(place_id='london')
    with pytest.raises(EmptyInstanceError) as e:
        f.minutely[0]  # pylint: disable=W0104
    assert str(e.value) == 'The instance does not contain any data!'


def test_time_machine_structure():
    """Test structure of the Forecast object on real data"""
    # Shortcut for UTC timezone object
    utc = pytz.timezone('UTC')
    # Shortcut for Kabul timezone object
    kbl = pytz.timezone('US/Pacific')

    # Initialize the Meteosource object
    m = Meteosource(API_KEY, tiers.FLEXI)
    # Get real forecast data (not mocked)
    tm = m.get_time_machine(date=[date(2021, 1, 1), '2019-05-05',
                            datetime(2020, 12, 15, 1, 10, 25)],
                            place_id='london', tz='UTC')
    assert len(tm.data) == 72
    assert tm.data[0].date == datetime(2021, 1, 1, 0, tzinfo=utc)
    assert tm.data[-1].date == datetime(2020, 12, 15, 23, tzinfo=utc)
    assert tm.data[25].date == datetime(2019, 5, 5, 1, tzinfo=utc)

    tm = m.get_time_machine(date_from='2019-05-05', date_to=date(2019, 5, 9),
                            lat=35.295, lon=69.5, tz='Asia/Kabul')
    assert len(tm.data) == 120
    dt = pytz.utc.localize(datetime(2019, 5, 5)).astimezone(kbl)
    assert tm.data[0].date == dt


def test_alerts():
    """Test alerts"""
    m = Meteosource(API_KEY, tiers.FLEXI)
    # We mock the API requests with sample data
    m.req_handler.execute_request = MagicMock(return_value=SAMPLE_POINT)
    # Get the mocked alerts data
    alerts = m.get_point_forecast(place_id='london', tz='UTC').alerts

    assert len(alerts) == 4
    for a in alerts:
        assert set(a.get_members()) == ALERTS

    assert alerts[3].event == 'Moderate Thunderstorms'
    assert len(alerts.get_active_alerts('2022-03-08T22:10:00')) == 3
    assert len(alerts.get_active_alerts(datetime(2022, 3, 8, 23, 0, 0))) == 3

    dt = pytz.timezone("Asia/Bangkok").localize(datetime(2022, 3, 8, 23, 0, 0))
    assert len(alerts.get_active_alerts(dt)) == 2
