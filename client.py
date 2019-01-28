# -*- coding: utf-8 -*-
import logging
import socket
import os
import queue
import namedPipe
import time
from multiprocessing import Process

MAX_NUM_PROCESSES = 10

logging.basicConfig(format='%(asctime)s. %(levelname)s. %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

class clientOperations:
    def __init__(self):
        self.logger = logging.getLogger()
        self.lines = []
        self.childs = []
        self.numChilds = 0
        self.pipe = namedPipe.namedPipe('blueliv_client')
        self.old_pipe_value = ''
        self.write_results = True
        self.num_proceses = MAX_NUM_PROCESSES

    def read_file(self):
        self.logger.info("Reading opeartions file")
        file = open('operations.txt')
        self.lines = file.readlines()
        self.lines = [x.strip() for x in self.lines]
        file.close()

    def child_process(self, line, child):
        # Create the child process to read the message and run the operation
        # logger.info("Child %s", line)
        retry = True
        while retry:
            waitResponse = True
            bConnected = False
            response = None
            iNumTrys = 0

            retry = False
            while not bConnected and (iNumTrys < 5):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                try:
                    s.connect(("127.0.0.1", 9999))
                    bConnected = True
                    waitResponse = True
                except socket.error as exc:
                    self.logger.error(str(child) + " => Error connecting to server " + str(line) + ". Error:" + str(exc))
                    waitResponse = False
                    time.sleep(0.05)
                    iNumTrys += 1
                    s.close()

            while waitResponse:
                try:
                    bytes = s.send(line.encode())
                except:
                    continue

                if (bytes != len(line)):
                    # TODO: retry to send again the message
                    continue
                else:
                    try:
                        response = s.recv(128).decode()
                    except socket.error as err:
                        self.logger.error("%i. %s. Error receiving response. %s", child, str(line), err.strerror)
                        retry = True
                        bConnected = False
                        break

                    response = str(line) + " = " + str(response)
                    self.logger.debug(str(child) + " => Response " + str(response))
                    # file_results.write(line + " = " + response + "\n")
                    # pipe.send_message_to_parent()
                    waitResponse = False
            if bConnected:
                s.shutdown(1)
                s.close()
            s = None
        self.pipe.send_message_to_parent(response)

    def manage_children_finished(self, message_child):
        #sChilds = message_child
        pidChilds = message_child.split("\n")
        # print(pidChilds)
        for spidChild in pidChilds:
            if spidChild.find("=") != -1 and self.write_results:
                self.file_results.write(spidChild + "\n")
                continue
            if (spidChild != ''):
                try:
                    pidChild = int(spidChild)
                except:
                    continue
                # self.logger.debug("Message child: %s. int: %i", message_child, pidChild)
                bFound = False
                iIdx = 0
                for x in self.childs:
                    if (x.pid == pidChild):
                        bFound = True
                        break
                    iIdx = iIdx + 1
                if bFound:
                    proces = self.childs[iIdx]
                    self.logger.debug("Message finishing child: %i", pidChild)
                    proces.kill()
                    proces.join()
                    proces.close()
                    proces = None
                    del self.childs[iIdx]
                else:
                    pass

    def read_pipe(self, old_pipe_value):
        while True:
            self.pipe.open_named_pipe()

            if self.pipe is not None:
                message_child = self.pipe.read_from_pipe()
                if message_child is None:
                    break
                message_child = message_child.decode()
                if old_pipe_value != '':
                    message_child = old_pipe_value + message_child
                    old_pipe_value = ''

                if (not message_child.endswith("\n")):
                    i = message_child.rfind("\n")
                    old_pipe_value = message_child[i:]
                    message_child = message_child[:i]

                if message_child:
                    try:
                        self.manage_children_finished(message_child)
                    except OSError as err:
                        self.logger.error("Error killing child process: %s. Err: %s", message_child, err.strerror)
                        break
                else:
                    break
            else:
                break
        return old_pipe_value

    def run(self):
        self.pipe.create_named_pipe()
        self.read_file()
        self.old_pipe_value = ''
        self.file_results = open('results_operations.txt','w')
        for line in self.lines:
            while (len(self.childs) > MAX_NUM_PROCESSES):
                self.logger.debug("Waiting for processes to be removed")
                time.sleep(0.05)
                self.old_pipe_value = self.read_pipe(self.old_pipe_value)
            p = Process(target=self.child_process, args=[line, self.numChilds])
            p.start()
            self.childs.append(p)

            self.old_pipe_value = self.read_pipe(self.old_pipe_value)
            self.numChilds += 1
            if (self.numChilds % 500 == 0):
                self.logger.info("%i", self.numChilds)

        self.file_results.close()
        self.logger.info("Finished")


def main():
    client = clientOperations()
    client.run()

if __name__ == "__main__":
    main()
