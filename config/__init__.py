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

	@classmethod
	def get_heartbeat_interval(cls):
		d = shelve.open(args.config)
		# default: 5000
		# minimum: 1000
		heartbeat_interval = max(1000, int(d.get("app.heartbeat_interval", 5000)))
		d.close()
		return heartbeat_interval

	@classmethod
	def set_heartbeat_interval(cls, value):
		d = shelve.open(args.config)
		d["app.heartbeat_interval"] = str(value)
		d.close()


parser = argparse.ArgumentParser(description="QSH")
parser.add_argument("--tcp-port", dest="tcp_port", default=7740, type=int, help="TCP port")
parser.add_argument("--udp-port", dest="udp_port", default=7741, type=int, help="broadcast (UDP) port")
parser.add_argument("--config", dest="config", default=AppConfig.get_config_path(), type=str, help="config file location")
parser.add_argument("--loglevel", dest="loglevel", default="ERROR", type=str, help="logging level (DEBUG, INFO, ERROR)")
parser.add_argument("--debug", dest="debug", default=False, type=bool, help="debug")
args = parser.parse_args()

APP_DEBUG = args.debug
APP_PORT = args.tcp_port
APP_BROADCAST_PORT = args.udp_port
APP_UUID = uuid.uuid4()
APP_HELLO_MSG = "QSH_HELLO"
APP_BYE_MSG = "QSH_BYE"

SCREEN_IMAGE_TYPE = "PNG"
SCREEN_IMAGE_QUALITY = 40

logging.basicConfig(level=getattr(logging, args.loglevel))