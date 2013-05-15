# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

import uuid
import logging
import argparse

parser = argparse.ArgumentParser(description='QSH')
parser.add_argument('--tcp-port', dest='tcp_port', default=7740, type=int, help='TCP port')
parser.add_argument('--udp-port', dest='udp_port', default=7741, type=int, help='broadcast (UDP) port')
args = parser.parse_args()

APP_PORT = args.tcp_port
APP_BROADCAST_PORT = args.udp_port
APP_UUID = uuid.uuid4()
APP_HELLO_MSG = "QSH_HELLO"
APP_BYE_MSG = "QSH_BYE"

SCREEN_IMAGE_TYPE = "JPG"
SCREEN_IMAGE_QUALITY = 40

logging.basicConfig(level=logging.DEBUG)