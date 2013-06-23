# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

import os
import uuid
import shelve
import logging
import argparse

from PySide.QtGui import QDesktopServices


class AppConfig:

	@classmethod
	def get_config_path(cls):
		config_path = os.path.join(QDesktopServices.storageLocation(QDesktopServices.DataLocation), "qsh")
		if not os.path.exists(config_path):
			os.makedirs(config_path)
		return os.path.join(config_path, "config")

	@classmethod
	def get_username(cls):
		d = shelve.open(args.config)
		username = d.get("app.username", "")
		d.close()
		return username

	@classmethod
	def set_username(cls, value):
		d = shelve.open(args.config)
		d["app.username"] = value
		d.close()


parser = argparse.ArgumentParser(description="QSH")
parser.add_argument("--tcp-port", dest="tcp_port", default=7740, type=int, help="TCP port")
parser.add_argument("--udp-port", dest="udp_port", default=7741, type=int, help="broadcast (UDP) port")
parser.add_argument("--config", dest="config", default=AppConfig.get_config_path(), type=str, help="config file location")
args = parser.parse_args()

APP_PORT = args.tcp_port
APP_BROADCAST_PORT = args.udp_port
APP_UUID = uuid.uuid4()
APP_HELLO_MSG = "QSH_HELLO"
APP_BYE_MSG = "QSH_BYE"

SCREEN_IMAGE_TYPE = "PNG"
SCREEN_IMAGE_QUALITY = 40

logging.basicConfig(level=logging.DEBUG)