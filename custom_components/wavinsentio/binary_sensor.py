"""Wavin Sentio binary sensor platform: per-room dehumidification request."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import WavinSentioDataCoordinator
from .const import CONF_DEVICE_NAME, DOMAIN
from .sentio_api import Room


def dehumidification_requested(raw_value) -> bool | None:
    """Translate the raw ``dehumidifierState`` value into on/off.

    The possible values of ``dehumidifierState`` are NOT documented, so this is
    a placeholder rule: it is on for ``True`` or for a string ending in ``_ON``
    (e.g. ``DEHUMIDIFIER_STATE_ON``) and off for any other value. Adjust only
    this function once the real values are known. The raw value is always
    available unchanged in the ``dehumidifier_state`` attribute.
    """
    if raw_value is None:
        return None
    if isinstance(raw_value, bool):
        return raw_value
    return str(raw_value).upper().endswith("_ON")


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the Wavin Sentio binary sensors."""
    dataservice = hass.data[DOMAIN].get("coordinator" + entry.data[CONF_DEVICE_NAME])

    if not dataservice:
        return

    # Only rooms whose data contains the field get an entity.
    async_add_entities(
        WavinSentioDehumidificationSensor(dataservice, room)
        for room in dataservice.get_rooms()
        if getattr(room, "dehumidifierState", None) is not None
    )


class WavinSentioDehumidificationSensor(CoordinatorEntity, BinarySensorEntity):
    """Whether the Sentio system requests dehumidification for a room (read-only)."""

    def __init__(self, dataservice: WavinSentioDataCoordinator, room: Room) -> None:
        """Initialize the binary sensor."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._room_id = room.id
        self._room_name = room.titlePersonalized

    def _raw_value(self):
        room = self._dataservice.get_room(self._room_id)
        return None if room is None else getattr(room, "dehumidifierState", None)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._room_name} Dehumidification"

    @property
    def is_on(self) -> bool | None:
        """Return true if dehumidification is requested."""
        return dehumidification_requested(self._raw_value())

    @property
    def extra_state_attributes(self):
        """Return the raw API value unchanged."""
        return {"dehumidifier_state": self._raw_value()}

    @property
    def unique_id(self):
        """Return the ID of this entity."""
        return f"{self._dataservice.device_name}-{self._room_id}-dehumidification"

    @property
    def device_info(self):
        """Return device info; same device as the room's climate entity."""
        return {
            "identifiers": {(DOMAIN, self._room_id)},
            "name": self._room_name,
            "manufacturer": "Wavin",
            "model": "Sentio",
        }
