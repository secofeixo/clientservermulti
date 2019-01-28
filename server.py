#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import argparse
import factoryServer

logging.basicConfig(format='%(asctime)s. %(levelname)s. %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
loggerGS = logging.getLogger()

def main():
    # create the server
    server = factoryServer.FactoryServer.create_server(factoryServer.typeServer.SOCKET)
    if (server is None):
        loggerGS.error('Server not created')
        return

    server.init()

if __name__ == "__main__":
    main()
