import logging
import unittest

from brainiak import log

LOG_FORMAT = "%(asctime)s - %(filename)s:%(lineno)d - %(name)s - %(levelname)s - %(message)s"


class LogTestCase(unittest.TestCase):

    def setUp(self):
        reload(log)

    def test_initial_attributes_values(self):
        self.assertEquals(log.handlers, [])
        self.assertEquals(log.logger, None)
        self.assertEquals(log.format, LOG_FORMAT)

    def test_create_handlers(self):
        self.assertEquals(log.handlers, [])
        log._create_handlers()
        self.assertEquals(len(log.handlers), 2)
        self.assertIsInstance(log.handlers[0], logging.handlers.WatchedFileHandler)
        self.assertIsInstance(log.handlers[1], logging.handlers.SysLogHandler)

    def test_retrieve_loggers(self):
        self.assertEquals(log.logger, None)
        loggers = log._retrieve_loggers()
        loggers_names = [logger.name for logger in loggers]
        self.assertIsInstance(log.logger, logging.Logger)
        self.assertEquals(log.logger.name, "brainiak")
        self.assertEquals(len(loggers), 4)
        self.assertIn("tornado.access", loggers_names)
        self.assertIn("tornado.application", loggers_names)
        self.assertIn("tornado.general", loggers_names)
        self.assertIn(log.logger, loggers)

    def test_initialize(self):
        self.assertEquals(log.logger, None)
        self.assertEquals(log.handlers, [])
        log.initialize()
        self.assertEquals(log.logger.handlers, log.handlers)
