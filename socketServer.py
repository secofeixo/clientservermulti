#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import socket
import os
import signal
import errno

import factoryServer
import namedPipe
from childServer import childServer
from multiprocessing import Process

PIPE_NAME = 'blueliv_fifo'

class socketServer():
    def __init__(self):
        self.logger = logging.getLogger()
        self.context = None
        self.socket = None
        self.type = factoryServer.typeServer.SOCKET
        self.HOST = 'localhost'
        self.PORT = 9999
        self.pipe = namedPipe.namedPipe(PIPE_NAME)

    def child_process(self, clientsocket, address):
        # os.close(self.read)
        childServerObj = childServer(clientsocket, address, PIPE_NAME)
        childServerObj.run()

    def open_named_pipe(self):
        self.pipe.open_named_pipe()

    def read_from_pipe(self):
        return self.pipe.read_from_pipe()

    def kill_children_from_message(self, message_child):
        sChilds = message_child.decode()
        pidChilds = sChilds.split("\n")
        # print(pidChilds)
        for spidChild in pidChilds:
            if (spidChild != ''):
                pidChild = int(spidChild)
                # self.logger.debug("Message child: %s. int: %i", message_child, pidChild)
                bFound = False
                iIdx = 0
                # print(self.childs)
                for x in self.childs:
                    # print(str(x.pid))
                    if (x.pid == pidChild):
                        bFound = True
                        break
                    iIdx = iIdx + 1
                if bFound:
                    proces = self.childs[iIdx]
                    # self.logger.debug("Message finishing child: %s. int: %i", message_child, pidChild)
                    proces.kill()
                    proces.join()
                    proces.close()
                    proces = None
                    del self.childs[iIdx]
                else:
                    # self.logger.debug("Process not found %i", pidChild)
                    pass

                # os.waitpid(pidChild, 0)
                # os.kill(pidChild, signal.SIGKILL)

    def remove_children_finished(self):
        while True:
            self.open_named_pipe()

            if self.pipe is not None:
                message_child = self.pipe.read_from_pipe()

                if message_child:
                    try:
                        self.kill_children_from_message(message_child)
                    except OSError as err:
                        self.logger.error("Error killing child process: %s. Err: %s", message_child, err.strerror)
                        break
                else:
                    break
            else:
                break

    def create_child(self, clientsocket, address):
        p = Process(target=self.child_process, args=(clientsocket, address))
        p.start()
        self.childs.append(p)

    def create_named_pipe(self):
        self.pipe.create_named_pipe()

    def init(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.HOST, self.PORT))
        self.socket.listen(1)

        self.logger.info("Listening on port %i", self.PORT)

        self.create_named_pipe()

        # list saving the pid of the alive child process
        self.childs = []

        while True:
            try:
                (clientsocket, address) = self.socket.accept()
            except KeyboardInterrupt:
                self.logger.info("socketServer. init. KeyboardInterrupt received, stopping…")
                break
            # self.logger.info("Connection accepted from %s", address)

            try:
                self.create_child(clientsocket, address)
            except OSError as err:
                self.logger.debug('socketServer. Exception creating process: %s', err.strerror)
                # print(err)
                # clientsocket.send(b"KO")
                break

            self.remove_children_finished()

        # We never get here but clean up anyhow
        self.socket.close()
        self.logger.info("socketServer. init. exiting")
