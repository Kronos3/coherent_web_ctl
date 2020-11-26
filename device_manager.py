from abc import ABC, abstractmethod
from enum import IntEnum, auto
from typing import List, Callable, Dict, Optional, Tuple

from log import logger


class DeviceEvent(IntEnum):
    HARDWARE_INIT = auto()
    HARDWARE_CLEANUP = auto()
    SWITCH_ON = auto()
    SWITCH_OFF = auto()
    GET_STATE = auto()


class Device(ABC):
    events: Dict[DeviceEvent, Callable[[object], object]]

    def __init__(self):
        self.events = {}

        self.register_event(DeviceEvent.HARDWARE_INIT, self.hardware_init)
        self.register_event(DeviceEvent.HARDWARE_CLEANUP, self.hardware_cleanup)

    def register_event(self, event: DeviceEvent, callback: Callable[[object], object]):
        self.events[event] = callback

    @abstractmethod
    def hardware_init(self): ...

    @abstractmethod
    def hardware_cleanup(self): ...

    def dispatch(self, event: DeviceEvent, args) -> Tuple[bool, object]:
        if event in self.events:
            return True, self.events[event](args)

        logger.error("Event %s is not handled by %s" % (event, self))
        return False, None


class DeviceManager(ABC):
    @abstractmethod
    def register_device(self, name: str, device: Device): ...

    @abstractmethod
    def get_device_id(self, device: Device) -> int: ...

    @abstractmethod
    def get_device_by_id(self, _id: int) -> Optional[Device]: ...

    @abstractmethod
    def get_device(self, name: str) -> Optional[Device]: ...


class HardwareDeviceManager(DeviceManager):
    name_to_devices: Dict[str, Device]
    device_to_id: Dict[Device, int]
    id_to_device: List[Device]
    id_counter: int

    def __init__(self):
        self.name_to_devices = {}
        self.device_to_id = {}
        self.id_to_device = []

        self.id_counter = 0

    def register_device(self, name: str, device: Device) -> int:
        """
        Add a device to the registry
        :param name: key to query device by
        :param device: device to register
        :return: unique id of device, -1 for invalid
        """

        if name in self.name_to_devices and device != self.name_to_devices[name]:
            logger.warning("Device with name '%s' is already registered as %s" % (name, self.name_to_devices[name]))
            return -1

        if name in self.name_to_devices and device == self.name_to_devices[name]:
            logger.warning("Duplicated register of the same device %s: %s" % (name, device))
            return -1

        device_id = self.id_counter
        logger.debug("Registering hardware device '%s' as %s (id %d)" % (name, device, device_id))

        self.name_to_devices[name] = device
        self.device_to_id[device] = device_id
        self.id_to_device.append(device)
        self.id_counter += 1

        return device_id

    def get_device_id(self, device: Device) -> int:
        if device not in self.device_to_id:
            logger.error("Device %s is not a registered device" % device)
            return -1

        return self.device_to_id[device]

    def get_device_by_id(self, _id: int) -> Optional[Device]:
        if _id < 0:
            logger.error("Invalid device ID %d" % _id)
            return None
        if _id >= len(self.id_to_device):
            logger.error("Device with ID %d is not registered" % _id)
            return None

        return self.id_to_device[_id]

    def get_device(self, name: str) -> Optional[Device]:
        """
        Get a device registered with a key
        :param name: key of the device
        :return: Device with key, None if not found
        """

        if name not in self.name_to_devices:
            logger.error("Device with name '%s' is not registered" % name)
            return None

        return self.name_to_devices[name]
