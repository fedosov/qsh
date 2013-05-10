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
from qsh import APP_UUID, SCREEN_IMAGE_TYPE, SCREEN_IMAGE_QUALITY

logger = logging.getLogger(__name__)


class ScreenViewWindow(QDialog):

	def __init__(self, parent=None):
		super(ScreenViewWindow, self).__init__(parent)

		self.connector = None

		self.setWindowTitle(u"Screen view [%s]" % APP_UUID)
		self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		self.initTrayIcon()

		# Net init
		self.connector = Connector()
		self.connector.helloAll()
		self.connector.known_hosts_updated_callback = self.updateTrayIconMenu
		self.connector.got_image_callback = self.showReceivedImage

		layout = QVBoxLayout()

		# Screenshot thumbnail
		self.imgPreview = QLabel()
		self.imgPreview.setFixedSize(640, 480)
		self.updateScreenshot()
		layout.addWidget(self.imgPreview)

		self.setLayout(layout)

	def closeEvent(self, event):
		self.connector.byeAll()
		event.accept()

	def showReceivedImage(self, data):
		""" Show received screenshot
		"""
		screen = QtGui.QPixmap()
		screen.loadFromData(data, SCREEN_IMAGE_TYPE)
		self.imgPreview.setPixmap(screen)
		#
		self.show()
		self.raise_()
		self.activateWindow()

	def updateScreenshot(self):
		""" Capture screenshot
		"""
		desktop_size = app.desktop().size()
		self.screen = QtGui.QPixmap.grabWindow(app.desktop().winId())
		self.screen = self.screen.copy(0, 0, desktop_size.width(), desktop_size.height()).scaledToWidth(640, QtCore.Qt.SmoothTransformation)

	def shareScreen(self, host, port):
		self.updateScreenshot()
		screenBA = QtCore.QByteArray()
		screenBuf = QtCore.QBuffer(screenBA)
		screenBuf.open(QtCore.QBuffer.WriteOnly)
		self.screen.save(screenBuf, SCREEN_IMAGE_TYPE, SCREEN_IMAGE_QUALITY)
		self.connector.submitScreen(host, port, screenBA)

	def initTrayIcon(self):
		""" Tray icon initialisation
		"""
		self.trayIconIcon = QIcon("resources/img/menu_bar_extras_icon.png")
		self.trayIconIcon.addPixmap("resources/img/menu_bar_extras_icon_alt.png", QIcon.Selected)

		self.actionQuit = QAction(u"Quit", self, triggered=self.close)

		self.trayIconMenu = QMenu(self)
		self.updateTrayIconMenu()

		self.trayIcon = QSystemTrayIcon(self)
		self.trayIcon.setIcon(self.trayIconIcon)
		self.trayIcon.setContextMenu(self.trayIconMenu)
		self.trayIcon.show()

	def updateTrayIconMenu(self):
		self.trayIconMenu.clear()

		# DEBUG (app UUID in tray icon popup menu):
		from qsh import APP_UUID
		trayIconMenuUUIDAction = QAction(unicode(APP_UUID), self)
		trayIconMenuUUIDAction.setDisabled(True)
		self.trayIconMenu.addAction(trayIconMenuUUIDAction)
		self.trayIconMenu.addSeparator()

		if self.connector and self.connector.known_hosts:
			for host in self.connector.known_hosts:
				host_str = "%s:%s" % (host[1].toString(), host[2])
				self.trayIconMenu.addAction(QAction(host_str, self, triggered=lambda: self.shareScreen(host[1], host[2])))
			self.trayIconMenu.addSeparator()
		self.trayIconMenu.addAction(self.actionQuit)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	windowScreenView = ScreenViewWindow()
	windowScreenView.show()
	sys.exit(app.exec_())
