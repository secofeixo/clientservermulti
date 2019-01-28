import logging
from enum import Enum

from socketServer import socketServer

class typeServer(Enum):
  SOCKET = "SOCKET"
  ZMQ = "ZMQ"
  RABBITMQ = "RABBITMQ"

class FactoryServer():
  @classmethod
  def create_server(self, typeServer):
    logger = logging.getLogger()
    serverToReturn = None
    if (typeServer == typeServer.SOCKET):
      serverToReturn = socketServer()
    else:
      logger.error('factoryServer.py. create_server. type of server not defined: %s', typeServer)
    return serverToReturn
