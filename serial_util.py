#
# Utilities for handling fMRI serial port triggers
# Author: Meng Du
# April 2017
#

import serial
import logging


class SerialUtil:
    def __init__(self, port, baudrate, timeout=None, logger=None,
                 trigger='5', responses=('1', '2', '3', '4'), read_size=1):
        self.serial = serial.Serial(port, baudrate, timeout=timeout)
        self.serial.flushInput()
        self.logger = logging.getLogger(logger)
        logging.basicConfig(format='%(asctime)s %(message)s')
        self.trigger = trigger
        self.responses = responses
        self.read_size = read_size

    def wait_for_trigger(self):
        buff = []
        while True:
            char = self.serial.read(self.read_size)
            self.logger.info('Received from serial port: ' + char)
            if char in self.responses:
                buff.append(char)
            elif char == self.trigger:
                return buff
