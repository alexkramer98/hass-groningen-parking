"""The Groningen Parking component."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, API_BASE
from .services import register_services

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Groningen Parking component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Groningen Parking from a config entry."""
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Register services
    await register_services(hass, entry)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return True