"""Services for the Groningen Parking component."""
from zoneinfo import ZoneInfo

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
import requests
import logging
import datetime
from functools import partial
from .const import DOMAIN, API_BASE, CONF_LICENSE_PLATE
import base64

_LOGGER = logging.getLogger(__name__)

async def register_services(hass: HomeAssistant, entry: ConfigEntry):
    """Register services for the component."""

    services = {
        "get_balance": async_get_balance,
        "has_reservation": async_has_reservation,
        "park": async_park,
        "unpark": async_unpark,
    }

    for service_name, service_func in services.items():
        async def service_wrapper(call: ServiceCall, handler=service_func):
            """Wraps the service handler to include the config entry."""
            return await handler(hass, call, entry)

        hass.services.async_register(
            DOMAIN,
            service_name,
            service_wrapper,
            supports_response=True
        )

async def get_reservation(response, entry: ConfigEntry):
    return next(
        (reservation for reservation in response["Permits"][0]["PermitMedias"][0]["ActiveReservations"]
         if reservation["LicensePlate"]["Value"] == entry.data.get(CONF_LICENSE_PLATE)),
        None
    )

async def async_get_balance(hass: HomeAssistant, call: ServiceCall, entry: ConfigEntry):
    """Handle the get_balance service."""
    response = await login(hass, entry)

    return {
        "balance_minutes": response["Permits"][0]["PermitMedias"][0]["Balance"]
    }

async def async_has_reservation(hass: HomeAssistant, call: ServiceCall, entry: ConfigEntry):
    """Handle the has_reservation service."""
    response = await login(hass, entry)
    has_reservation = await get_reservation(response, entry) is not None

    return {
        "has_reservation": has_reservation
    }

async def async_park(hass: HomeAssistant, call: ServiceCall, entry: ConfigEntry):
    """Handle the park service."""
    response = await login(hass, entry)
    token = response["Token"]
    encoded_token = base64.b64encode(token.encode('ascii')).decode('ascii')

    now = datetime.datetime.now(ZoneInfo("Europe/Amsterdam"))

    datetime_from = now.replace(second=0, microsecond=0).isoformat(sep='T', timespec='milliseconds')
    datetime_till = now.replace(hour=23, minute=59, second=0, microsecond=0).isoformat(sep='T', timespec='milliseconds')

    await handle_api_call(hass, '/reservation/create', {
        "DateFrom": datetime_from,
        "DateUntil": datetime_till,
        "LicensePlate": {
            "Value": entry.data.get(CONF_LICENSE_PLATE),
        },
        "permitMediaCode": entry.data.get(CONF_USERNAME),
        "permitMediaTypeID": "1"
    }, {
        "Authorization": f"Token {encoded_token}"
    })

    return {}


async def async_unpark(hass: HomeAssistant, call: ServiceCall, entry: ConfigEntry):
    """Handle the unpark service."""
    response = await login(hass, entry)
    reservation_id = (await get_reservation(response, entry))["ReservationID"]
    token = response["Token"]
    encoded_token = base64.b64encode(token.encode('ascii')).decode('ascii')

    await handle_api_call(hass, '/reservation/end', {
        "ReservationID": reservation_id,
        "permitMediaCode": entry.data.get(CONF_USERNAME),
        "permitMediaTypeID": "1"
    }, {
        "Authorization": f"Token {encoded_token}"
    })

    return {}

def make_api_call(url: str, data: dict, headers: dict = None):
    """Make synchronous API call."""
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

async def handle_api_call(hass: HomeAssistant, endpoint: str, data: dict, headers: dict = None):
    """Handle the API call with error handling."""
    url = f"{API_BASE}/{endpoint}"

    try:
        # Run the requests call in an executor
        func = partial(make_api_call, url, data, headers)
        result = await hass.async_add_executor_job(func)
        return result

    except requests.exceptions.RequestException as ex:
        _LOGGER.error("API request for %s failed: %s", endpoint, str(ex))
        raise

async def login(hass: HomeAssistant, entry: ConfigEntry):
    return await handle_api_call(hass, "/login", {
        "identifier": entry.data[CONF_USERNAME],
        "loginMethod": "Pas",
        "permitMediaTypeID": 1,
        "password": entry.data[CONF_PASSWORD],
    })

