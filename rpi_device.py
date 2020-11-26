from device import Switch, Board
import RPi.GPIO as GPIO
from log import logger


class RPiSwitch(Switch):
    def __init__(self, pin_number: int, name: str):
        super().__init__(pin_number, name)

    def hardware_init(self):
        logger.debug("Initializing switch %s on pin %d" % (self.name, self.pin))
        GPIO.setup(self.pin, GPIO.OUT)
        self.sync()

    def hardware_cleanup(self):
        self.off()
        logger.debug("Cleaned up %s" % self)

    def sync(self):
        logger.debug("Turning %s %s" % (self.name, "ON" if self.state else "OFF"))
        GPIO.output(self.pin, self.state)


class RPiBoard(Board):
    def hardware_init(self):
        logger.info("Initializing board to defaults")
        logger.debug("Setting mode to GPIO.BOARD")
        GPIO.setmode(GPIO.BOARD)

        self.initialized = True
