from device import Switch, Board
from log import logger


class DummySwitch(Switch):
    def __init__(self, pin_number: int, name: str):
        super().__init__(pin_number, name)

    def hardware_init(self):
        logger.debug("Initializing switch %s on pin %d" % (self.name, self.pin))
        self.sync()

    def hardware_cleanup(self):
        self.off()
        logger.debug("Cleaned up %s" % self)

    def sync(self):
        logger.debug("Turning %s %s" % (self.name, "ON" if self.state else "OFF"))


class DummyBoard(Board):
    def hardware_init(self):
        logger.info("Initializing board to defaults")
        logger.debug("Setting mode to GPIO.BOARD")
        self.initialized = True
