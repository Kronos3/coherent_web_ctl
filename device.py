from abc import ABC, abstractmethod
from enum import IntEnum, auto
from typing import List, Dict, Callable, Union, Tuple
from log import logger


class DeviceEvent(IntEnum):
    METADATA = auto()
    HARDWARE_INIT = auto()
    HARDWARE_CLEANUP = auto()
    SWITCH_ON = auto()
    SWITCH_OFF = auto()
    GET_STATE = auto()


class Device(ABC):
    events: Dict[DeviceEvent, Callable[[Union[Tuple[any, ...], any]], any]]

    def __init__(self):
        self.events = {}

        self.register_event(DeviceEvent.HARDWARE_INIT, self.hardware_init)
        self.register_event(DeviceEvent.HARDWARE_CLEANUP, self.hardware_cleanup)

    def register_event(self, event: DeviceEvent, callback: Callable[[Union[Tuple[any, ...], any]], any]):
        self.events[event] = callback

    @abstractmethod
    def hardware_init(self): ...

    @abstractmethod
    def hardware_cleanup(self): ...

    def check_dispatch(self, event: DeviceEvent) -> bool:
        return event in self.events

    def dispatch(self, event: DeviceEvent, args=None) -> Tuple[bool, object]:
        if self.check_dispatch(event):
            try:
                return True, self.events[event](args)
            except Exception as e:
                logger.error(e)
                return False, e

        logger.error("Event %s is not handled by %s" % (event, self))
        return False, None


class Board(Device, ABC):
    initialized: bool
    devices: List[Device]

    def __init__(self):
        super().__init__()

        self.initialized = False
        self.devices = []

    def add_hardware(self, device: Device):
        if not self.initialized:
            logger.warning("Attempting to add hardware before the board has been initialized")
            self.hardware_init()

        logger.info("Adding device to board: %s" % device)
        self.devices.append(device)
        device.hardware_init()

    def hardware_cleanup(self):
        """
        Cleanup all of the devices
        """

        logger.debug("Cleaning up devices")
        if self.initialized:
            for device in self.devices:
                device.hardware_cleanup()


class Switch(Device, ABC):
    name: str
    pin: int
    state: bool

    def __init__(self, pin_number: int, name: str):
        super().__init__()

        self.pin = pin_number
        self.name = name
        self.state = False

        self.register_event(DeviceEvent.SWITCH_ON, self.on)
        self.register_event(DeviceEvent.SWITCH_OFF, self.off)
        self.register_event(DeviceEvent.GET_STATE, self.get_state)
        self.register_event(DeviceEvent.METADATA, self.get_metadata)

    def get_metadata(self, *_args):
        return {
            'name': self.name,
            'pin': self.pin,
            'state': self.state
        }

    def get_state(self, *_args):
        return self.state

    def on(self, *_args):
        if not self.state:
            self.state = True
            self.sync()

    def off(self, *_args):
        if self.state:
            self.state = False
            self.sync()

    @abstractmethod
    def sync(self): ...

    def __repr__(self) -> str:
        return "Switch(%s): [%s]" % (self.name, "ON" if self.state else "OFF")
