# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov"
__maintainer__ = "Mikhail Fedosov"
__email__ = "tbs.micle@gmail.com"
__doc__ = u"Quick share for teams"

import sys
import PySide
from __init__ import *
from PySide.QtGui import *
from PySide.QtCore import SIGNAL
from PySide import QtGui, QtCore, QtNetwork
from connector import Connector

class ScreenViewWindow(QDialog):
	def __init__(self, parent=None):
		super(ScreenViewWindow, self).__init__(parent)
		self.setWindowTitle(u"Просмотр экрана")
		self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		self.initTrayIcon()

		layout = QVBoxLayout()

		# Screenshot thumbnail
		self.imgPreview = QLabel()
		self.imgPreview.setFixedSize(640, 480)
		self.updateScreenshot()
		layout.addWidget(self.imgPreview)

		# Command buttons
		buttonBox = QtGui.QDialogButtonBox()
		self.btnPush = QPushButton(u"Отправка картинки")
		self.btnPush.clicked.connect(self.pushScreen)
		buttonBox.addButton(self.btnPush, QtGui.QDialogButtonBox.ActionRole)
		self.btnPull = QPushButton(u"Загрузка картинки")
		self.btnPull.clicked.connect(self.pullScreen)
		buttonBox.addButton(self.btnPull, QtGui.QDialogButtonBox.ActionRole)
		layout.addWidget(buttonBox)

		# Status label
		self.statusLabel = QLabel(u"Статус")
		layout.addWidget(self.statusLabel)

		self.setLayout(layout)

		self.connector = Connector()
		self.connector.helloAll()

	def updateScreenshot(self):
		"""Capture screenshot"""
		desktop_size = QtGui.QApplication.desktop().size()
		self.screen = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId())
		self.screen = self.screen.copy(0, 0, desktop_size.width(), desktop_size.height()).scaledToWidth(640, QtCore.Qt.SmoothTransformation)
		self.imgPreview.setPixmap(self.screen)

	def pullScreen(self):
		"""Get screen"""
		print "PULL!"

	def pushScreen(self):
		"""Send screen"""
		self.updateScreenshot()
		#self.submitScreen()
		print "PUSH!"

	def initTrayIcon(self):
		"""Tray icon initialisation"""
		self.trayIconIcon = QIcon("trayico.png")

		self.actionSendScreenshot = QAction(u"Отправить экран", self, triggered=self.pushScreen)
		self.actionQuit = QAction(u"Выход", self, triggered=QtGui.qApp.quit)

		self.trayIconMenu = QMenu(self)
		self.trayIconMenu.addAction(self.actionSendScreenshot)
		self.trayIconMenu.addAction(self.actionQuit)

		self.trayIcon = QSystemTrayIcon(self)
		self.trayIcon.setIcon(self.trayIconIcon)
		self.trayIcon.setContextMenu(self.trayIconMenu)
		self.trayIcon.show()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	windowScreenView = ScreenViewWindow()
	windowScreenView.show()
	sys.exit(app.exec_())
