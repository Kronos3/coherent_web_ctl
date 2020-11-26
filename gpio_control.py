from typing import List

import RPi.GPIO as GPIO
from log import logger
from device_manager import Device, DeviceEvent


class Board(Device):
    initialized: bool
    devices: List[Device]

    def __init__(self):
        super().__init__()

        self.initialized = False
        self.devices = []

    def hardware_init(self):
        logger.info("Initializing board to defaults")
        logger.debug("Setting mode to GPIO.BOARD")
        GPIO.setmode(GPIO.BOARD)

        self.initialized = True

    def add_hardware(self, device: Device):
        if not self.initialized:
            logger.warning("Attempting to add hardware before the board has been initialized")
            self.hardware_init()

        logger.info("Adding device to board: %s" % device)
        self.devices.append(device)

    def hardware_cleanup(self):
        """
        Cleanup all of the devices
        """

        logger.debug("Cleaning up devices")
        if self.initialized:
            for device in self.devices:
                device.hardware_cleanup()


class Switch(Device):
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

    def hardware_init(self):
        logger.debug("Initializing switch %s on pin %d" % (self.name, self.pin))
        GPIO.setup(self.pin, GPIO.OUT)
        self.sync()

    def get_state(self):
        return self.state

    def hardware_cleanup(self):
        self.off()
        logger.debug("Cleaned up %s" % self)

    def sync(self):
        logger.debug("Turning %s %s" % (self.name, "ON" if self.state else "OFF"))
        GPIO.output(self.pin, self.state)

    def on(self):
        if not self.state:
            self.state = True
            self.sync()

    def off(self):
        if self.state:
            self.state = False
            self.sync()

    def __repr__(self) -> str:
        return "Switch(%s): [%s]" % (self.name, "ON" if self.state else "OFF")
