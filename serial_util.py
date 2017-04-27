#
# Utilities for handling fMRI serial port triggers
# Author: Meng Du
# April 2017
#

import serial
import logging
import os
import pty
import threading
import time

_ser_name = ''


class SerialUtil:
    def __init__(self, port='virtual', baudrate=9600, timeout=None, logger=None, trigger_interval=2,
                 trigger='5', responses=('1', '2', '3', '4'), read_size=1):
        """
        
        :param port: 
        :param baudrate: 
        :param timeout: 
        :param logger: 
        :param trigger_interval: 
        :param trigger: 
        :param responses: 
        :param read_size: 
        """
        self.logger = logging.getLogger(logger)
        logging.basicConfig(format='%(asctime)s %(message)s')
        self.trigger = trigger
        self.responses = responses
        self.read_size = read_size
        if port == 'virtual':
            self._virtual_sender(baudrate, timeout, trigger_interval)
        else:
            self.serial = serial.Serial(port, baudrate, timeout=timeout)
        self.serial.flushInput()

    def __del__(self):
        if port == 'virtual':
            

    def wait_for_trigger(self):
        buff = []
        while True:
            char = self.serial.read(self.read_size)
            self.logger.info('Received from serial port: ' + char)
            if char in self.responses:
                buff.append(char)
            elif char == self.trigger:
                return buff

    def _virtual_sender(self, baudrate, timeout, trigger_interval):
        global _ser_name

        def _sender_thread():
            global _ser_name
            master, slave = pty.openpty()
            _ser_name = os.ttyname(slave)
            index = 0
            while True:
                os.write(master, self.trigger)
                time.sleep(float(trigger_interval)/2)
                if index == len(self.responses):
                    index = 0
                os.write(master, self.responses[index])
                index += 1
                time.sleep(trigger_interval/2)

        th = threading.Thread(target=_sender_thread)
        th.start()
        while True:
            if len(_ser_name) > 0:
                self.serial = serial.Serial(_ser_name, baudrate, timeout=timeout)
                return

su = SerialUtil(read_size=10, timeout=0.1)
print su.wait_for_trigger(), su.wait_for_trigger(), su.wait_for_trigger()

