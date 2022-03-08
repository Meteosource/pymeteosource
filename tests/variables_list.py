"""Definitions of present variables at given places in the response"""

WIND = {'angle', 'dir', 'gusts', 'speed'}

MINUTELY = {'date', 'precipitation'}

CLOUD = {'total', 'low', 'middle', 'high'}

PROBABILITY = {'precipitation', 'storm', 'freeze'}

PRECIPITATION = {'total', 'type', 'convective', 'rainspot'}

CURRENT = {'cloud_cover', 'dew_point', 'feels_like', 'humidity', 'icon',
           'icon_num', 'irradiance', 'ozone', 'precipitation', 'pressure',
           'summary', 'temperature', 'uv_index', 'visibility', 'wind',
           'wind_chill'}

PRECIPITATION_CURRENT = {'total', 'type'}

HOURLY = {'date', 'weather', 'icon', 'summary', 'temperature', 'feels_like',
          'soil_temperature', 'wind_chill', 'dew_point', 'surface_temperature',
          'wind', 'cloud_cover', 'pressure', 'precipitation', 'probability',
          'cape', 'evaporation', 'irradiance', 'lftx', 'ozone', 'uv_index',
          'humidity', 'snow_depth', 'sunshine_duration', 'visibility'}

DAILY = {'day', 'weather', 'icon', 'summary', 'predictability', 'all_day',
         'morning', 'afternoon', 'evening', 'astro', 'statistics'}

ALL_DAY = {'weather', 'icon', 'temperature', 'temperature_min',
           'temperature_max', 'feels_like', 'feels_like_min', 'feels_like_max',
           'soil_temperature', 'soil_temperature_min', 'soil_temperature_max',
           'wind_chill', 'wind_chill_min', 'wind_chill_max', 'dew_point',
           'dew_point_min', 'dew_point_max', 'surface_temperature',
           'surface_temperature_min', 'surface_temperature_max', 'wind',
           'cloud_cover', 'pressure', 'precipitation', 'probability',
           'ozone', 'humidity', 'snow_depth', 'visibility'}

PART_DAY = {'weather', 'icon', 'temperature', 'feels_like', 'soil_temperature',
            'wind_chill', 'dew_point', 'surface_temperature', 'wind',
            'cloud_cover', 'pressure', 'precipitation', 'probability',
            'ozone', 'humidity', 'snow_depth', 'visibility'}
ASTRO = {'sun', 'moon'}

SUN = {'rise', 'set', 'always_up', 'always_down'}

MOON = {'rise', 'set', 'always_up', 'always_down', 'phase'}

STATS = {'temperature', 'wind', 'precipitation'}

STATS_TEMP = {'avg', 'avg_min', 'avg_max', 'record_min', 'record_max'}
STATS_WIND = {'avg_speed', 'avg_angle', 'avg_dir', 'max_speed', 'max_gust'}
STATS_PREC = {'avg', 'probability'}
ALERTS = {'event', 'onset', 'expires', 'sender', 'certainty', 'severity',
          'headline', 'description'}
