# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"
__doc__ = u"Quick share for teams"

import sys
import logging

from PySide.QtGui import *
from PySide import QtGui, QtCore

from networking.connector import Connector

logger = logging.getLogger(__name__)


class ScreenViewWindow(QDialog):
	def __init__(self, parent=None):
		super(ScreenViewWindow, self).__init__(parent)

		self.connector = None

		self.setWindowTitle(u"Screen view")
		self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		self.initTrayIcon()

		# Net init
		self.connector = Connector()
		self.connector.helloAll()
		self.connector.known_hosts_updated_callback = self.updateTrayIconMenu

		layout = QVBoxLayout()

		# Screenshot thumbnail
		self.imgPreview = QLabel()
		self.imgPreview.setFixedSize(640, 480)
		self.updateScreenshot()
		layout.addWidget(self.imgPreview)

		# Command buttons
		buttonBox = QtGui.QDialogButtonBox()
		self.btnPush = QPushButton(u"Push screen")
		self.btnPush.clicked.connect(self.pushScreen)
		buttonBox.addButton(self.btnPush, QtGui.QDialogButtonBox.ActionRole)
		self.btnPull = QPushButton(u"Pull screen")
		self.btnPull.clicked.connect(self.pullScreen)
		buttonBox.addButton(self.btnPull, QtGui.QDialogButtonBox.ActionRole)
		layout.addWidget(buttonBox)

		# Status label
		self.statusLabel = QLabel(u"Статус")
		layout.addWidget(self.statusLabel)

		self.setLayout(layout)

	def closeEvent(self, event):
		self.connector.byeAll()
		event.accept()

	def updateScreenshot(self):
		""" Capture screenshot
		"""
		desktop_size = app.desktop().size()
		self.screen = QtGui.QPixmap.grabWindow(app.desktop().winId())
		self.screen = self.screen.copy(0, 0, desktop_size.width(), desktop_size.height()).scaledToWidth(640, QtCore.Qt.SmoothTransformation)
		self.imgPreview.setPixmap(self.screen)

	def pullScreen(self):
		""" Get screen
		"""
		logger.debug("pull_screen")
		# TODO

	def pushScreen(self):
		""" Send screen
		"""
		logger.debug("push_screen")
		self.updateScreenshot()
		logger.debug("update_screenshot")
		# TODO
		#self.submitScreen()

	def initTrayIcon(self):
		""" Tray icon initialisation
		"""
		self.trayIconIcon = QIcon("resources/img/menu_bar_extras_icon.png")
		self.trayIconIcon.addPixmap("resources/img/menu_bar_extras_icon_alt.png", QIcon.Selected)

		self.actionSendScreenshot = QAction(u"Push screen", self, triggered=self.pushScreen)
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

		self.trayIconMenu.addAction(self.actionSendScreenshot)
		self.trayIconMenu.addSeparator()
		if self.connector and self.connector.known_hosts:
			for host in self.connector.known_hosts:
				self.trayIconMenu.addAction("%s:%s" % (host[1].toString(), host[2]))
			self.trayIconMenu.addSeparator()
		self.trayIconMenu.addAction(self.actionQuit)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	windowScreenView = ScreenViewWindow()
	windowScreenView.show()
	sys.exit(app.exec_())
