"""Switch platform for Wavin Sentio integration in Home Assistant."""

import time

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .sentio_api import StandbyMode, VacationMode

from . import WavinSentioDataCoordinator
from .const import CONF_DEVICE_NAME, DOMAIN

# The cloud may keep returning the old config for a short while after a write.
# The written state is shown for at most this many seconds, or until the
# polled data confirms it.
OPTIMISTIC_TIMEOUT = 30


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up Wavin Sentio switch entities from a config entry."""
    dataservice = hass.data[DOMAIN].get("coordinator"+entry.data[CONF_DEVICE_NAME])

    if not dataservice:
        return

    entities = []
    entities.append(WavinSentioStandbySwitchEntity(dataservice))
    entities.append(WavinSentioVacationSwitchEntity(dataservice))
    async_add_entities(entities)


class WavinSentioOptimisticSwitch(CoordinatorEntity, SwitchEntity):
    """Switch that shows the written state until the polled data confirms it."""

    _pending = None  # (target state, monotonic deadline)

    def _actual_is_on(self):
        """Return the state according to the last polled data."""
        raise NotImplementedError

    @property
    def is_on(self):
        """Return true if the switch is on (optimistic while a write is unconfirmed)."""
        actual = self._actual_is_on()
        if self._pending is not None:
            target, deadline = self._pending
            if actual == target or time.monotonic() > deadline:
                self._pending = None
            else:
                return target
        return actual

    async def _async_write(self, write, target):
        """Await the write call, show the target state, then poll immediately."""
        await write()
        self._pending = (target, time.monotonic() + OPTIMISTIC_TIMEOUT)
        self.async_write_ha_state()
        # async_refresh (not async_request_refresh) so the debouncer cannot skip it.
        await self.coordinator.async_refresh()


class WavinSentioStandbySwitchEntity(WavinSentioOptimisticSwitch):
    """Switch entity for controlling the standby mode of a Wavin Sentio device."""

    def __init__(self, dataservice: WavinSentioDataCoordinator) -> None:
        """Initialize the Wavin Sentio Standby Switch entity."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._name = "Standby"
        self._attr_device_class = SwitchDeviceClass.SWITCH

    @property
    def name(self) -> str:
        """Return the display name of this switch."""
        return self._name

    def _actual_is_on(self):
        """Return true if the mode equals standby."""
        return self._dataservice.get_device().lastConfig.sentio.standbyMode == StandbyMode.STANDBY_MODE_ON

    async def async_turn_on(self, **kwargs):
        """Turn on the standby mode."""
        await self._async_write(self._dataservice.turn_on_standby, True)

    async def async_turn_off(self, **kwargs):
        """Turn off the standby mode."""
        await self._async_write(self._dataservice.turn_off_standby, False)

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return str(self._dataservice.get_device().name ) + "-Standby"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for this entity."""
        return DeviceInfo(
            identifiers= {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._dataservice.get_device().name)
            },
            name = self._dataservice.get_device().lastConfig.sentio.titlePersonalized,
            manufacturer = "Wavin",
            model = "Sentio",
        )

class WavinSentioVacationSwitchEntity(WavinSentioOptimisticSwitch):
    """Switch entity for controlling the vacation mode of a Wavin Sentio device."""

    def __init__(self, dataservice: WavinSentioDataCoordinator) -> None:
        """Initialize the Wavin Sentio Vacation Switch entity."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._name = "Vacation"
        self._attr_device_class = SwitchDeviceClass.SWITCH

    @property
    def name(self) -> str:
        """Return the display name of this switch."""
        return self._name

    def _actual_is_on(self):
        """Return true if the mode equals Vacation."""
        return self._dataservice.get_device().lastConfig.sentio.vacationSettings.vacationMode == VacationMode.VACATION_MODE_ON

    async def async_turn_on(self, **kwargs):
        """Turn on the vacation mode."""
        await self._async_write(self._dataservice.turn_on_vacation_mode_device, True)

    async def async_turn_off(self, **kwargs):
        """Turn off the standby mode."""
        await self._async_write(self._dataservice.turn_off_vacation_mode_device, False)

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return str(self._dataservice.get_device().name ) + "-Vacation"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for this entity."""
        return DeviceInfo(
            identifiers= {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._dataservice.get_device().name)
            },
            name = self._dataservice.get_device().lastConfig.sentio.titlePersonalized,
            manufacturer = "Wavin",
            model = "Sentio",
            serial_number = self._dataservice.get_device().serialNumber,
            sw_version = self._dataservice.get_device().firmwareInstalled,
        )
