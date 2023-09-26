from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CURRENCY_EURO
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.discovery import async_discover

from .const import SENSOR_PORTUGAL, SENSOR_SPAIN

class OmieSensor(Entity):
    def __init__(self, coordinator, sensor_name):
        """Initialize the Omie price sensor."""
        self._coordinator = coordinator
        self._sensor_name = sensor_name

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Omie {self._sensor_name.capitalize()} Price"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._coordinator.data.get(self._sensor_name)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        return CURRENCY_EURO

# Discovery code should not be placed here; it should be in your __init__.py

    async def async_update(self):
        """Update the sensor's state."""
        try:
            await self._coordinator.async_request_refresh()
        except UpdateFailed as e:
            # Handle failed data update (e.g., connection error)
            self._coordinator.last_update_success = False