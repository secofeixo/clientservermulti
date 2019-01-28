#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import errno
import logging


class namedPipe:
    def __init__(self, name):
        self.logger = logging.getLogger()
        self.namePipe = name
        self.pipe = None

    def create_named_pipe(self):
        self.logger.debug('pipe name: %s', self.namePipe)
        if os.path.exists(self.namePipe):
            os.unlink(self.namePipe)
        if not os.path.exists(self.namePipe):
            os.mkfifo(self.namePipe)

    def open_named_pipe(self):
        # self.logger.debug('pipe name: %s', self.namePipe)
        if (self.pipe is None):
            try:
                self.pipe = os.open(self.namePipe, os.O_RDONLY | os.O_NONBLOCK)
                self.logger.debug('Pipe %s openened', self.namePipe)
            except OSError as err:
                if err.errno == errno.ENOENT:
                    self.pipe = None
                else:
                    raise err

    def send_message_to_parent(self, message = None):
        try:
            w = os.open(self.namePipe, os.O_WRONLY | os.O_NONBLOCK)
        except OSError as exc:
            if exc.errno == errno.ENXIO:
                w = None
            else:
                raise

        if w is not None:
            try:
                if (message is not None):
                    os.write(w, (message + "\n").encode())
                os.write(w, (str(os.getpid()) + "\n").encode())
            except OSError as exc:
                if exc.errno == errno.EPIPE:
                    pass
                else:
                    raise
            os.close(w)


    def read_from_pipe(self):
        message_child = None
        try:
            message_child = os.read(self.pipe,100)
        except OSError as exc:
            if exc.errno == errno.EAGAIN or exc.errno == errno.EWOULDBLOCK:
                message_child = None
                # self.logger.error("Error reading from pipe: %s", exc.strerror)
            else:
                raise
        return message_child


