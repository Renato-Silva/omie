
"""Custom Integration for Omie with Portugal and Spain Sensors."""

import asyncio
import logging
from datetime import timedelta
import requests

import voluptuous as vol
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, SENSOR_PORTUGAL, SENSOR_SPAIN, DEFAULT_NAME, OMIE_URL

# Set up the logger
_LOGGER = logging.getLogger(__name__)

# Configuration options
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=15)

# Validation schema for the configuration entries
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


# Example data fetch function (replace with actual Omie API call)
async def async_fetch_data():
    """Fetch data for the Omie Integration."""
    try:


        response = requests.get(OMIE_URL)

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
                desired_value_pt = values[3].strip()
                desired_value_es = values[2].strip()
                desired_value_float_pt = float(desired_value_pt.replace(',', '.'))
                desired_value_float_es = float(desired_value_es.replace(',', '.'))

                portugal_price = desired_value_float_pt / 1000
                spain_price = desired_value_float_es / 1000

                return {SENSOR_PORTUGAL: portugal_price, SENSOR_SPAIN: spain_price}

            else:
                _LOGGER.error("Not found.")
        else:
            _LOGGER.error(f"Failed to retrieve data. Status code: {response.status_code}")
    except Exception as e:
        raise UpdateFailed(f"Error fetching data: {e}") from e

async def async_setup(hass, config):
    """Set up the custom Omie integration."""

    # Get the user-defined configuration
    conf = config.get(DOMAIN)

    # Create a data coordinator to manage data updates
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=conf.get(CONF_NAME),
        update_method=async_fetch_data,
        update_interval=DEFAULT_UPDATE_INTERVAL,
    )

    # Fetch initial data
    await coordinator.async_refresh()

    # Create and add the Portugal and Spain sensor entities
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][SENSOR_PORTUGAL] = OmieSensor(coordinator, SENSOR_PORTUGAL)
    hass.data[DOMAIN][SENSOR_SPAIN] = OmieSensor(coordinator, SENSOR_SPAIN)

    # Register components with Home Assistant
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True




