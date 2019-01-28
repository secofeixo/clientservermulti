# -*- coding: utf-8 -*-
import logging
import socket
import os
import errno

import parseOperation
import namedPipe

class childServer():
    def __init__(self, clientsocket, address, pipe_name):
        self.logger = logging.getLogger()
        self.clientaddress = address
        self.socket = clientsocket
        self.pipe_name = pipe_name
        self.pipe = namedPipe.namedPipe(pipe_name)

    def run(self):
        message = self.socket.recv(1024).decode('utf-8')
        if (message != ''):
            self.logger.debug("childServer. Message received %s.", message)
            try:
                po = parseOperation.parse_operation()
                result = po.parse(message)
                self.socket.send(str(result).encode())
                self.socket.shutdown(1)
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None
        self.pipe.send_message_to_parent()
        # self.socket.shutdown(socket.SHUT_RDWR)
