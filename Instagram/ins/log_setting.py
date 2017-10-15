import logging
import sys


class logger(object):
    def __init__(self, logname='', filename='', level=''):
        self.logger = logging.getLogger(logname)
        self.formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
        self.file_handler = logging.FileHandler(filename)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(level)

    def debug(self, msg):
        self.logger.debug(msg)
    def info(self, msg):
        self.logger.info(msg)
    def warn(self, msg):
        self.logger.warn(msg)
    def error(self, msg):
        self.logger.error(msg)
    def fatal(self, msg):
        self.logger.fatal(msg)
    def critical(self, msg):
        self.logger.critical(msg)




