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


class SerialUtil:
    def __init__(self, port='virtual', baudrate=9600, timeout=None, logger=None, trigger_interval=2,
                 trigger='5', responses=('1', '2', '3', '4'), read_size=1):
        # TODO virtual port doesn't work
        """
        If using a virtual port, serial_util.close_virtual_port() needs to be called once finished.
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
        self.trigger = trigger
        self.responses = responses
        self.read_size = read_size
        self.port = port
        if port == 'virtual':
            self.sending = True
            self.virtual_ser_name = ''
            self._virtual_sender(baudrate, timeout, trigger_interval)
        else:
            self.serial = serial.Serial(port, baudrate, timeout=timeout)
        self.serial.flushInput()

    def close_virtual_port(self):
        if self.port == 'virtual':
            self.sending = False

    def wait_for_a_trigger(self):
        buff = []
        while True:
            char = self.serial.read(self.read_size)
            self.logger.info('Received from serial port: ' + char)
            if char in self.responses:
                buff.append(char)
            elif char == self.trigger:
                return buff

    def wait_for_triggers(self, number):
        responses = []
        for i in range(0, number):
            responses.append(self.wait_for_a_trigger())
        return responses

    def _virtual_sender(self, baudrate, timeout, trigger_interval):

        def _sender_thread():
            master, slave = pty.openpty()
            self.virtual_ser_name = os.ttyname(slave)
            index = 0
            while self.sending:
                os.write(master, self.trigger)
                time.sleep(float(trigger_interval)/2)
                if index == len(self.responses):
                    index = 0
                os.write(master, self.responses[index])
                index += 1
                time.sleep(trigger_interval/2)

        th = threading.Thread(target=_sender_thread)
        th.start()
        # while True:
        #     if len(self.virtual_ser_name) > 0:
        #         print self.virtual_ser_name
        #         self.serial = serial.Serial(self.virtual_ser_name, baudrate, timeout=timeout)
        #         return

if __name__ == '__main__':
    su = SerialUtil()
    print su.virtual_ser_name
    time.sleep(100)
    su.close_virtual_port()
