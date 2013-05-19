# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"
__doc__ = u"Quick share for teams"

import sys
import logging
import datetime

# PySide
from PySide.QtGui import *
from PySide import QtGui, QtCore

# QSH
from networking.connector import Connector
from config import AppConfig, APP_UUID, SCREEN_IMAGE_TYPE, SCREEN_IMAGE_QUALITY

logger = logging.getLogger(__name__)


class ScreenViewWindow(QDialog):

	def __init__(self, parent=None):
		super(ScreenViewWindow, self).__init__(parent)

		self.connector = None

		self.setWindowTitle(u"Screen view" % APP_UUID)
		self.resize(640, 120)
		self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		self.initTrayIcon()

		# Net init
		self.connector = Connector()
		self.connector.helloAll()
		self.connector.known_hosts_updated_callback = self.updateTrayIconMenu
		self.connector.got_image_callback = self.showReceivedImage

		layout = QHBoxLayout()
		self.setLayout(layout)

	def closeEvent(self, event):
		self.connector.byeAll()
		event.accept()

	def showReceivedImage(self, data_uuid, data):
		""" Show received screenshot
		"""
		screen_preview_box = QFrame()
		screen_preview_box.setLayout(QVBoxLayout())
		screen_preview = QLabel()
		screen_preview.setFixedHeight(120)
		screen = QtGui.QPixmap()
		screen.loadFromData(data, SCREEN_IMAGE_TYPE)
		screen = screen.scaledToHeight(120, QtCore.Qt.SmoothTransformation)
		screen_preview.setPixmap(screen)

		screen_preview_box.layout().addWidget(screen_preview)
		screen_preview_label_text = "Unknown user"
		screen_preview_label = QLabel()
		if data_uuid in self.connector.known_hosts.keys():
			screen_preview_label_text = self.connector.known_hosts[data_uuid]["username"]
		screen_preview_label_text = "%s @ %s" % (screen_preview_label_text, datetime.datetime.now().strftime("%H:%M"))
		screen_preview_label.setText(screen_preview_label_text)
		screen_preview_label.setFont(QFont("Tahoma", 10))
		screen_preview_box.layout().addWidget(screen_preview_label)

		self.layout().addWidget(screen_preview_box)
		#
		self.show()
		self.raise_()
		self.activateWindow()

	def updateScreenshot(self):
		""" Capture screenshot
		"""
		desktop_size = app.desktop().size()
		self.screen = QtGui.QPixmap.grabWindow(app.desktop().winId())
		self.screen = self.screen.copy(0, 0, desktop_size.width(), desktop_size.height())

	def shareScreen(self, host, port):
		self.updateScreenshot()
		screenBA = QtCore.QByteArray()
		screenBuf = QtCore.QBuffer(screenBA)
		screenBuf.open(QtCore.QBuffer.WriteOnly)
		self.screen.save(screenBuf, SCREEN_IMAGE_TYPE, SCREEN_IMAGE_QUALITY)
		self.connector.submitScreen(host, port, screenBA)

	def config(self):
		config_dialog = ConfigDialog(self)
		config_dialog.showNormal()
		config_dialog.activateWindow()
		config_dialog.raise_()

	def initTrayIcon(self):
		""" Tray icon initialisation
		"""
		self.trayIconIcon = QIcon("resources/img/menu_bar_extras_icon.png")
		self.trayIconIcon.addPixmap("resources/img/menu_bar_extras_icon_alt.png", QIcon.Selected)

		self.actionQuit = QAction(u"Quit", self, triggered=self.close)
		self.actionConfig = QAction(u"Configuration", self, triggered=self.config)

		self.trayIconMenu = QMenu(self)
		self.updateTrayIconMenu()

		self.trayIcon = QSystemTrayIcon(self)
		self.trayIcon.setIcon(self.trayIconIcon)
		self.trayIcon.setContextMenu(self.trayIconMenu)
		self.trayIcon.show()

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

		if self.connector and self.connector.known_hosts:
			for host_uuid, host_data in self.connector.known_hosts.iteritems():
				if host_data["username"]:
					host_str = "%s - [%s:%s]" % (host_data["username"].decode("utf-8"), host_data["host"].toString(), host_data["port"])
				else:
					host_str = "[%s:%s]" % (host_data["host"].toString(), host_data["port"])
				self.trayIconMenu.addAction(QAction(host_str, self, triggered=lambda: self.shareScreen(host_data["host"], host_data["port"])))
			self.trayIconMenu.addSeparator()
		self.trayIconMenu.addAction(self.actionConfig)
		self.trayIconMenu.addAction(self.actionQuit)


class ConfigDialog(QDialog):

	def __init__(self, parent=None):
		super(ConfigDialog, self).__init__(parent)

		self.setWindowTitle(u"QSH config")
		self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))

		layout = QVBoxLayout()

		layout.addWidget(QtGui.QLabel("Username:"))
		self.editUsername = QtGui.QLineEdit(AppConfig.get_username())
		layout.addWidget(self.editUsername)

		buttonBox = QtGui.QDialogButtonBox()
		self.btnCancel = QPushButton(u"Cancel")
		self.btnCancel.clicked.connect(self.close)
		buttonBox.addButton(self.btnCancel, QtGui.QDialogButtonBox.RejectRole)
		self.btnSave = QPushButton(u"Save")
		self.btnSave.clicked.connect(self.save)
		buttonBox.addButton(self.btnSave, QtGui.QDialogButtonBox.AcceptRole)
		layout.addWidget(buttonBox)

		self.setLayout(layout)

	def save(self):
		AppConfig.set_username(self.editUsername.text())
		self.parent().updateTrayIconMenu()
		self.parent().connector.helloAll()
		self.close()


class ScreenDialog(QDialog):

	def __init__(self, parent=None):
		super(ScreenDialog, self).__init__(parent)

		self.setStyleSheet("{ background: #ff0000; }")
		self.setWindowTitle(u"Screen dialog")


if __name__ == '__main__':
	app = QApplication(sys.argv)
	windowScreenView = ScreenViewWindow()
	windowScreenView.show()
	sys.exit(app.exec_())
