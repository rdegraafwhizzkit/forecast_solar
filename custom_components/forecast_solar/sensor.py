"""
https://doc.forecast.solar/doku.php?id=api:estimate

configuration.yaml

sensor:
  - platform: forecast_solar
#    api_key: dummy
    latitude: 52.336389266521266
    longitude: 5.317898716089767
    declination: 10
    azimuth: 0  # -180 = north, -90 = east, 0 = south, 90 = west, 180 = north
    kilo_watt_peak: 10
    resources:
      - watts
      - watt_hours_period
      - watt_hours
      - watt_hours_day
"""
from datetime import timedelta
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_RESOURCES, CONF_API_KEY, CONF_LONGITUDE, CONF_LATITUDE
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from urllib.request import urlopen, Request
import homeassistant.helpers.config_validation as cv
import json
import logging
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

BASE_URL_PUBLIC = 'https://api.forecast.solar/estimate/{latitude}/{longitude}/{declination}/{azimuth}/{kilo_watt_peak}'
BASE_URL_PRIVATE = 'https://api.forecast.solar/{api_key}/estimate/{latitude}/{longitude}/{declination}/{azimuth}/{kilo_watt_peak}'

MIN_TIME_BETWEEN_UPDATES = timedelta(hours=1)

MDI_FLASH = 'mdi:flash'
SENSOR_PREFIX = 'Forecast Solar '
SENSOR_TYPES = {
    'watts': ['Watts (power) average for the period', 'Watt', MDI_FLASH],
    'watt_hours_period': ['Watt hours (energy) for the period', 'Wh', MDI_FLASH],
    'watt_hours': ['Watt hours (energy) summarized over the day', 'Wh', MDI_FLASH],
    'watt_hours_day': ['Watt hours (energy) summarized for each day', 'Wh', MDI_FLASH]
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_API_KEY, default=''): cv.string,
    vol.Required(CONF_LATITUDE): cv.latitude,
    vol.Required(CONF_LONGITUDE): cv.longitude,
    vol.Required('declination'): vol.Range(0, 90),
    vol.Required('azimuth'): vol.Range(-180, 180),
    vol.Required('kilo_watt_peak'): cv.positive_int,
    vol.Required(CONF_RESOURCES): vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)])
})


def setup_platform(hass, config, add_entities, discovery_info=None):  # noqa
    try:
        data_provider = ForecastSolarAPI(config)  # Re-use data provider
        add_entities([ForecastSolarSensor(data_provider, resource.lower()) for resource in config[CONF_RESOURCES]])
        return True
    except Exception as ex:
        _LOGGER.error(ex)
        return False


class ForecastSolarAPI(object):

    def __init__(self, config):
        api_key = config[CONF_API_KEY]
        self._url = (BASE_URL_PRIVATE if api_key else BASE_URL_PUBLIC).format(**{
            'latitude': config[CONF_LATITUDE],
            'longitude': config[CONF_LONGITUDE],
            'declination': config['declination'],
            'azimuth': config['azimuth'],
            'kilo_watt_peak': config['kilo_watt_peak'],
            'api_key': api_key
        })

        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        request = Request(url=self._url)
        request.add_header('Accept', 'application/json')
        self.data = json.loads(urlopen(request).read())


class ForecastSolarSensor(Entity):

    def __init__(self, data_provider, sensor_type):
        self._data_provider = data_provider
        self.type = sensor_type
        self._name = SENSOR_PREFIX + SENSOR_TYPES[self.type][0]
        self._unit_of_measurement = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = None
        self._attrs = {'values': []}

        self.update()

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attrs

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    def update(self):
        self._data_provider.update()
        self._attrs['values'] = [
            {'time': t, 'value': v} for t, v in self._data_provider.data.get('result', {}).get(self.type, {}).items()
        ]
