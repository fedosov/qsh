# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"
__doc__ = u"Quick share for teams"

import sys
import logging
import datetime

import gntp.notifier

# PySide
from PySide.QtGui import *
from PySide import QtGui, QtCore

# QSH
from networking.connector import Connector
from config import AppConfig, APP_UUID, SCREEN_IMAGE_TYPE, SCREEN_IMAGE_QUALITY

logger = logging.getLogger(__name__)

growl = gntp.notifier.GrowlNotifier(
	applicationName="QSH",
	notifications=["Incoming screenshots"],
	defaultNotifications=["Incoming screenshots"],
)
growl.register()


class ScreenViewWindow(QDialog):

	def __init__(self, parent=None):
		super(ScreenViewWindow, self).__init__(parent)

		self.connector = None

		self.setWindowTitle(u"QSH" % APP_UUID)
		self.resize(160, 120)
		self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		#self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

		self.initTrayIcon()

		self.screen_geometry = app.desktop().screenGeometry()

		# Net init
		self.connector = Connector()
		self.connector.helloAll()
		self.connector.known_hosts_updated_callback = self.updateTrayIconMenu
		self.connector.got_image_callback = self.showReceivedImage

		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)
		self.setLayout(layout)

	def closeEvent(self, event):
		self.connector.byeAll()
		event.accept()

	def showReceivedImage(self, data_uuid, data):
		""" Show received screenshot
		"""
		if not (data_uuid and data.size()):
			# empty sender UUID or empty data (image)
			return

		screen_preview_box = QFrame()
		screen_preview_box.setLayout(QVBoxLayout())
		screen_preview = QLabel()
		screen_preview.setFixedHeight(120)
		screen = QtGui.QPixmap()
		screen.loadFromData(data, SCREEN_IMAGE_TYPE)
		screen_preview.original_pixmap = screen.copy()
		screen = screen.scaledToHeight(120, QtCore.Qt.SmoothTransformation)
		screen_preview.setPixmap(screen)

		# add screen label (sender, date)
		screen_preview_box.layout().addWidget(screen_preview)
		screen_preview_label_text = "Unknown user"
		screen_preview_label = QLabel()
		if data_uuid in self.connector.known_hosts.keys():
			screen_preview_label_text = self.connector.known_hosts[data_uuid]["username"]
		screen_preview_label_text = "%s @ %s" % (screen_preview_label_text, datetime.datetime.now().strftime("%H:%M"))
		screen_preview_label.setText(screen_preview_label_text)
		screen_preview_label.setFont(QFont("Tahoma", 10))
		screen_preview_box.layout().addWidget(screen_preview_label)

		growl.notify(
			noteType="Incoming screenshots",
			title="QSH: Screenshot received",
			description=screen_preview_label_text,
			sticky=False,
			priority=1,
		)

		# show button (TODO: show on screen click)
		screen_preview_show = QPushButton("Show")
		screen_preview_show.screen_preview = screen_preview
		screen_preview_show.clicked.connect(self.screenPreviewShowClicked)
		screen_preview_box.layout().addWidget(screen_preview_show)

		# remove button
		screen_preview_remove = QPushButton("Remove")
		screen_preview_remove.screen_preview_box = screen_preview_box
		screen_preview_remove.clicked.connect(self.screenPreviewRemoveClicked)
		screen_preview_box.layout().addWidget(screen_preview_remove)

		self.layout().addWidget(screen_preview_box)

		app.processEvents()
		QtCore.QTimer.singleShot(0, self.showWindow)

	def showWindow(self):
		self.show()
		self.raise_()
		self.activateWindow()
		QtCore.QTimer.singleShot(0, self.updateWindowPositionAndSize)

	def updateWindowPositionAndSize(self):
		self.resize(self.minimumSizeHint())
		self.move(self.screen_geometry.width() / 2 - self.width() / 2,
		          self.screen_geometry.height() - 400)

	def screenPreviewShowClicked(self):
		""" Screen 'show' button click
		"""
		screen_preview = self.sender().screen_preview
		assert isinstance(screen_preview, QLabel)
		screen_preview.screen_preview_fs = QLabel()
		# copy and resize original image
		screen_preview.screen_preview_fs.setPixmap(
			screen_preview.original_pixmap.copy().scaled(self.screen_geometry.width(),
			                                             self.screen_geometry.height(),
			                                             QtCore.Qt.KeepAspectRatio,
			                                             QtCore.Qt.SmoothTransformation)
		)
		# show fullscreen
		screen_preview.screen_preview_fs.showFullScreen()
		screen_preview.screen_preview_fs.raise_()
		screen_preview.screen_preview_fs.activateWindow()
		# close on doubleclick
		screen_preview.screen_preview_fs.mouseDoubleClickEvent = lambda x: screen_preview.screen_preview_fs.deleteLater()

	def screenPreviewRemoveClicked(self):
		""" Screen 'remove' button click
		"""
		screen_preview_box = self.sender().screen_preview_box
		assert isinstance(screen_preview_box, QFrame)
		screen_preview_box.deleteLater()
		QtCore.QTimer.singleShot(0, self.showWindow)

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


if __name__ == '__main__':
	app = QApplication(sys.argv)
	windowScreenView = ScreenViewWindow()
	#windowScreenView.show()
	sys.exit(app.exec_())
