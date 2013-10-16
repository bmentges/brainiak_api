from logging.handlers import WatchedFileHandler, SysLogHandler
from syslog import LOG_LOCAL3
import logging

from brainiak.settings import LOG_FILEPATH, LOG_LEVEL, LOG_NAME

handlers = []
logger = None
format = u"%(asctime)s - %(filename)s:%(lineno)d - %(name)s - %(levelname)s - %(message)s"


__doc__ = """
This module provides access to Brainiak's loggers and log handlers.

Objects:
- handlers: list of LogHandlers used by the module
- format: used by the logging.Formatter instances
- logger: to be used by the applications

Methods:
- initialize()

How to use:

(1) Initialize loggers (e.g. while starting the server):

    from brainiak import log
    log.initialize()

(2) Log info, debug, error, warnings, etc:

    from brainiak import log
    log.logger.error("Error msg")
    log.logger.debug("Debug msg")

Requirements:

brainiak.settings must define:
- LOG_FILEPATH (e.g. "/tmp/brainiak.log")
- LOG_LEVEL (e.g. logging.info)
- LOG_NAME (e.g. "brainiak")

"""


def get_logger():
    return logger


def _create_handlers(filename=LOG_FILEPATH, level=LOG_LEVEL):
    formatter = logging.Formatter(format)

    # WatchedFileHandler watches the file it is logging to.
    # If the file changes, it is closed and reopened using the file name.
    file_handler = WatchedFileHandler(filename)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Used by internal log monitoring applications
    syslog_handler = SysLogHandler(facility=LOG_LOCAL3)
    syslog_handler.setFormatter(formatter)
    syslog_handler.setLevel(level)

    global handlers
    handlers = [file_handler, syslog_handler]

    return handlers


def _retrieve_loggers():
    # per-request logging for Tornado's HTTP Servers
    access_logger = logging.getLogger("tornado.access")

    # errors from application code (e.g. uncaught exceptions from callbacks)
    app_logger = logging.getLogger("tornado.application")

    # General-purpose logging from Tornado itself
    gen_logger = logging.getLogger("tornado.general")

    # Stomp logger imported by dad library
    stomp_logger = logging.getLogger("stomp.py")

    # Brainiak application logger
    global logger
    logger = logging.getLogger(LOG_NAME)

    return [access_logger, app_logger, gen_logger, stomp_logger, logger]


def initialize(level=LOG_LEVEL):
    handlers = _create_handlers()
    loggers = _retrieve_loggers()

    for handler in handlers:
        for logger in loggers:
            logger.addHandler(handler)
            logger.setLevel(level)


if __name__ == "__main__":
    initialize()
