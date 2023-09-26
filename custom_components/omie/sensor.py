import json
import logging
import requests
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ATTR_ATTRIBUTION

_LOGGER = logging.getLogger(__name__)

DOMAIN = "omie_spot"

def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([OMIESpotSensor()], True)

class OMIESpotSensor(SensorEntity):
    def __init__(self):
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return "OMIE Spot Data"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        try:
            response = requests.get("https://www.omie.es/sites/default/files/dados/NUEVA_SECCION/INT_PBC_EV_H_ACUM.TXT")

            if response.status_code == 200:
                content = response.text
                current_datetime = datetime.now()
                hour = current_datetime.hour + 1
                formatted_hour = str(hour)
                formatted_datetime = current_datetime.strftime("%d/%m/%Y;{};".format(formatted_hour))

                lines = content.split('\n')

                found_line = None
                for line in lines:
                    if line.startswith(formatted_datetime):
                        found_line = line
                        break

                if found_line:
                    values = found_line.split(';')
                    desired_value = values[3].strip()
                    desired_value_float = float(desired_value.replace(',', '.'))

                    self._state = desired_value_float / 1000
                else:
                    _LOGGER.error("Not found.")
            else:
                _LOGGER.error(f"Failed to retrieve data. Status code: {response.status_code}")

        except Exception as e:
            _LOGGER.error(f"An error occurred: {str(e)}")
