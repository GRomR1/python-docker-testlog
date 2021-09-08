from datetime import datetime
import logging
import sys
import os
import time
from time import gmtime
# https://stackoverflow.com/questions/63501504/python-logging-iso8601-timestamp-with-milliseconds-and-timezone-using-config-fi
# import pytz
#
# class MyFormatter(logging.Formatter):
#     # override the converter in logging.Formatter
#     converter = datetime.fromtimestamp
#
#     # override formatTime in logging.Formatter
#     def formatTime(self, record, datefmt=None, timezone="UTC"):
#         return self.converter(record.created, tz=pytz.timezone(timezone)).isoformat()

logging.Formatter.converter = gmtime
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# console = logging.StreamHandler()
# LOGGER.addHandler(console)
#
# formatter = MyFormatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# console.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03dZ - %(name)s - %(levelname)s - %(message)s',
                    datefmt="%Y-%m-%dT%H:%M:%S"
                    )


if __name__ == '__main__':
    time.sleep(5)
    LOGGER.debug('sys.argv[0] is %s', sys.argv[0])
    LOGGER.info('sys.executable is %s', sys.executable)
    LOGGER.warning('os.getcwd is %s', os.getcwd())

    LOGGER.error("The app has run")

    try:
        1 / 0
    except ZeroDivisionError:
        LOGGER.exception("Deliberate divide by zero traceback")

    try:
        while True:
            LOGGER.debug(f"Time is {datetime.now()}")
            LOGGER.debug(f"Time is {datetime.now()}. With multiline (first):\n"
                          "new line (second)\n"
                          "another line (third)")
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit) as e:
        LOGGER.critical("Has stopped", exc_info=True)
