import time
from typing import TextIO

LOG_FILE = "hardware.log"


class Log:
    path: str
    file: TextIO

    def __init__(self, logfile: str):
        self.path = logfile
        self.file = open(self.path, "a+")

        self.info("=============================", log_level=0)
        self.info("Opening log file %s" % self.path)

    def get_path(self) -> str:
        return self.path

    @staticmethod
    def _get_timestamp() -> str:
        return time.strftime("[%Y-%m-%d %H:%M:%S %Z]")

    def _print_message(self, method: str, message: str, log_level: int):
        self.file.write("[%s] (%s)[%d] %s\n" % (self._get_timestamp(), method, log_level, message))
        self.file.flush()

    def info(self, message, log_level=1):
        self._print_message("info", message, log_level)

    def error(self, message, log_level=0):
        self._print_message("error", message, log_level)

    def warning(self, message, log_level=1):
        self._print_message("warn", message, log_level)

    def debug(self, message, log_level=10):
        self._print_message("debug", message, log_level)


logger = Log(LOG_FILE)
