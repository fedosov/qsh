# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"
__doc__ = u"Quick share for teams"

import sys
import logging

# PySide
from PySide.QtGui import *
from PySide import QtGui, QtCore

# QSH
from networking.connector import Connector
from config import AppConfig, SCREEN_IMAGE_TYPE, SCREEN_IMAGE_QUALITY
from dialogs import ConfigurationDialog, ScreenViewDialog, MainTrayIcon

logger = logging.getLogger(__name__)


class QSH(QApplication):

	def __init__(self, *args, **kwargs):
		super(QSH, self).__init__(*args, **kwargs)
		self.setQuitOnLastWindowClosed(False)

		# signals
		self.aboutToQuit.connect(self.beforeQuit)

		# dialogs
		self.screenViewDialog = ScreenViewDialog(self)

		# networking
		self.connector = Connector()

		# tray
		self.trayIcon = MainTrayIcon(self, callbacks=
		{
			"quit": self.quit,
			"configuration": self.showConfigurationDialog,
			"incoming": self.showScreenViewDialog
		})
		self.trayIcon.middle_click_callback = self.trayIconMiddleClick

		# networking callbacks
		self.connector.known_hosts_updated_callback = self.trayIcon.updateMenu
		self.connector.got_image_callback = self.processReceivedImage
		self.connector.receiving_start_callback = self.trayIcon.setIconLoading
		self.connector.sending_end_callback = self.trayIcon.setIconDefault

		# hi there!
		self.connector.updateKnownHosts()

		# periodically check whether hosts alive
		self.helloAllTimer = QtCore.QTimer(self)
		self.connect(self.helloAllTimer, QtCore.SIGNAL("timeout()"), self.connector.updateKnownHosts)
		self.helloAllTimer.start(AppConfig.get_heartbeat_interval())

	def trayIconMiddleClick(self):
		self.trayIcon.icon.setContextMenu(None)
		if not self.screenViewDialog.isVisible():
			if self.trayIcon.incomingTotal:
				self.trayIcon.actionShowScreenViewDialog.trigger()
		else:
			self.screenViewDialog.close()

	def processReceivedImage(self, data_uuid=None, data=None):
		""" Show received screenshot
		"""
		if data_uuid and data.size():
			receivedImagesCount = self.screenViewDialog.processReceivedImage(data_uuid=data_uuid,
			                                                                 data=data,
			                                                                 known_hosts=self.connector.known_hosts)
			self.trayIcon.incomingTotal += receivedImagesCount
			if self.screenViewDialog.isVisible():
				self.screenViewDialog.showWindow()
			else:
				self.trayIcon.incomingUnread += receivedImagesCount
			self.trayIcon.updateMenu()

		self.trayIcon.setIconDefault()

	def shareScreen(self, host, port):
		""" Send screenshot
		"""
		self.trayIcon.setIconLoading()

		# capture screenshot
		screenBA = QtCore.QByteArray()
		screenBuf = QtCore.QBuffer(screenBA)
		screenBuf.open(QtCore.QBuffer.WriteOnly)
		QPixmap.grabWindow(self.desktop().winId()).save(screenBuf, SCREEN_IMAGE_TYPE, SCREEN_IMAGE_QUALITY)

		self.connector.submitScreen(host, port, screenBA)

	def showConfigurationDialog(self):
		self.config_dialog = ConfigurationDialog(self)
		self.config_dialog.showNormal()
		self.config_dialog.activateWindow()
		self.config_dialog.raise_()

	def showScreenViewDialog(self):
		self.trayIcon.incomingUnread = 0
		self.trayIcon.updateMenu()
		self.trayIcon.setIconDefault()
		self.screenViewDialog.showWindow()

	def beforeQuit(self):
		self.connector.byeAll()


if __name__ == '__main__':
	app = QSH(sys.argv)
	sys.exit(app.exec_())
