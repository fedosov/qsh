# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

import uuid
import logging

APP_PORT = 7740
APP_BROADCAST_PORT = 7741
APP_UUID = uuid.uuid4()
APP_HELLO_MSG = "QSH_HELLO"
APP_BYE_MSG = "QSH_BYE"

SCREEN_IMAGE_TYPE = "JPG"
SCREEN_IMAGE_QUALITY = 40

logging.basicConfig(level=logging.DEBUG)