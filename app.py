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
from dialogs import ConfigurationDialog, ScreenViewDialog
from config import AppConfig, SCREEN_IMAGE_TYPE, SCREEN_IMAGE_QUALITY

logger = logging.getLogger(__name__)


class QSH(QApplication):

	def __init__(self, *args, **kwargs):
		super(QSH, self).__init__(*args, **kwargs)
		self.setQuitOnLastWindowClosed(False)

		# state
		self.incomingTotal = 0
		self.incomingUnread = 0

		# signals
		self.aboutToQuit.connect(self.beforeQuit)

		# dialogs
		self.screenViewDialog = ScreenViewDialog(self)

		# networking
		self.connector = Connector()
		self.connector.known_hosts_updated_callback = self.updateTrayIconMenu
		self.connector.got_image_callback = self.processReceivedImage
		self.connector.receiving_start_callback = self.trayIconSetIconLoading
		self.connector.sending_end_callback = self.trayIconSetIconDefault

		# tray
		self.initTrayIcon()
		self.updateTrayIconMenu()

		# hi there!
		self.helloAll()

		self.helloAllTimer = QtCore.QTimer(self)
		self.connect(self.helloAllTimer, QtCore.SIGNAL("timeout()"), self.helloAll)
		self.helloAllTimer.start(AppConfig.get_heartbeat_interval())

	def processReceivedImage(self, data_uuid=None, data=None):
		""" Show received screenshot
		"""
		if data_uuid and data.size():
			receivedImagesCount = self.screenViewDialog.processReceivedImage(data_uuid=data_uuid,
			                                                                 data=data,
			                                                                 known_hosts=self.connector.known_hosts)
			self.incomingTotal += receivedImagesCount
			if self.screenViewDialog.isVisible():
				self.screenViewDialog.showWindow()
			else:
				self.incomingUnread += receivedImagesCount
			self.updateTrayIconMenu()

		self.trayIconSetIconDefault()

	def initTrayIcon(self):
		""" Tray icon initialisation
		"""
		self.trayIconIcon = QIcon("resources/img/menu_bar_extras_icon.png")
		self.trayIconIcon.addPixmap("resources/img/menu_bar_extras_icon_alt.png", QIcon.Selected)

		self.trayIconLoading = QIcon("resources/img/menu_bar_extras_icon__loading.png")
		self.trayIconLoading.addPixmap("resources/img/menu_bar_extras_icon__loading_alt.png", QIcon.Selected)

		self.trayIconUnread = QIcon("resources/img/menu_bar_extras_icon__unread.png")
		self.trayIconUnread.addPixmap("resources/img/menu_bar_extras_icon__unread_alt.png", QIcon.Selected)

		self.actionQuit = QAction(u"Quit", self, triggered=self.quit)
		self.actionShowConfigurationDialog = QAction(u"Configuration", self, triggered=self.showConfigurationDialog)
		self.actionShowScreenViewDialog = QAction(self, triggered=self.showScreenViewDialog)

		self.trayIconMenu = QMenu()
		self.updateTrayIconMenu()

		self.trayIcon = QSystemTrayIcon(self)
		self.trayIconSetIconDefault()
		self.trayIcon.setContextMenu(self.trayIconMenu)
		self.trayIcon.show()

	def trayIconSetIconDefault(self):
		if self.incomingUnread > 0:
			self.trayIconSetIconUnread(self.incomingUnread)
		else:
			self.trayIcon.setIcon(self.trayIconIcon)

	def trayIconSetIconLoading(self):
		self.trayIcon.setIcon(self.trayIconLoading)

	def trayIconSetIconUnread(self, count=1):
		self.trayIcon.setIcon(self.trayIconUnread)

	def updateTrayIconMenu(self):
		self.trayIconMenu.clear()

		# DEBUG (app UUID in tray icon popup menu):
		from config import APP_UUID
		username = AppConfig.get_username()
		if username:
			trayIconMenuUUIDAction = QAction(unicode(username), self)
		else:
			trayIconMenuUUIDAction = QAction(unicode(APP_UUID), self)
		trayIconMenuUUIDAction.setDisabled(True)
		self.trayIconMenu.addAction(trayIconMenuUUIDAction)
		self.trayIconMenu.addSeparator()

		# known hosts list
		if self.connector and self.connector.known_hosts:
			for host_uuid, host_data in self.connector.known_hosts.iteritems():
				if host_data["username"]:
					host_str = "%s - [%s:%s]" % (host_data["username"].decode("utf-8"), host_data["host"].toString(), host_data["port"])
				else:
					host_str = "[%s:%s]" % (host_data["host"].toString(), host_data["port"])
				self.trayIconMenu.addAction(QAction(host_str, self, triggered=lambda: self.shareScreen(host_data["host"], host_data["port"])))
			self.trayIconMenu.addSeparator()

		# incoming data
		self.actionShowScreenViewDialog.setDisabled(self.incomingTotal == 0)
		self.actionShowScreenViewDialog.setText("(%i) Incoming" % self.incomingUnread if self.incomingUnread else "Incoming")
		self.trayIconMenu.addAction(self.actionShowScreenViewDialog)
		self.trayIconMenu.addSeparator()

		self.trayIconMenu.addAction(self.actionShowConfigurationDialog)
		self.trayIconMenu.addAction(self.actionQuit)

	def updateScreenshot(self):
		""" Capture screenshot
		"""
		desktop_size = self.desktop().size()
		self.screen = QtGui.QPixmap.grabWindow(self.desktop().winId())
		self.screen = self.screen.copy(0, 0, desktop_size.width(), desktop_size.height())

	def shareScreen(self, host, port):
		""" Send screenshot
		"""
		self.trayIconSetIconLoading()
		self.updateScreenshot()
		screenBA = QtCore.QByteArray()
		screenBuf = QtCore.QBuffer(screenBA)
		screenBuf.open(QtCore.QBuffer.WriteOnly)
		self.screen.save(screenBuf, SCREEN_IMAGE_TYPE, SCREEN_IMAGE_QUALITY)
		self.connector.submitScreen(host, port, screenBA)

	def showConfigurationDialog(self):
		self.config_dialog = ConfigurationDialog(self)
		self.config_dialog.showNormal()
		self.config_dialog.activateWindow()
		self.config_dialog.raise_()

	def showScreenViewDialog(self):
		self.incomingUnread = 0
		self.updateTrayIconMenu()
		self.trayIconSetIconDefault()
		self.screenViewDialog.showWindow()

	def helloAll(self):
		""" Anybody here?
		"""
		self.connector.clearKnownHosts()
		self.connector.helloAll()

	def beforeQuit(self):
		self.connector.byeAll()


if __name__ == '__main__':
	app = QSH(sys.argv)
	sys.exit(app.exec_())
