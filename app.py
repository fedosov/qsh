# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov"

import sys
import PySide
from PySide import QtGui, QtCore
from PySide.QtGui import *

class ScreenViewWindow(QDialog):
	def __init__(self, parent=None):
		super(ScreenViewWindow, self).__init__(parent)
		self.setWindowTitle(u"Просмотр экрана")
		self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		self.initTrayIcon()

		self.imgPreview = QLabel()
		self.imgPreview.setFixedSize(320, 240)
		self.updateScreenshot()

		self.btnPush = QPushButton(u"Отправка картинки")
		self.btnPush.clicked.connect(self.pushScreen)
		self.btnPull = QPushButton(u"Загрузка картинки")
		self.btnPull.clicked.connect(self.pullScreen)

		layout = QVBoxLayout()
		layout.addWidget(self.imgPreview)
		layout.addWidget(self.btnPush)
		layout.addWidget(self.btnPull)
		self.setLayout(layout)

	def updateScreenshot(self):
		desktop_size = QtGui.QApplication.desktop().size()
		pix = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId())
		pix = pix.copy(0, 0, desktop_size.width(), desktop_size.height()).scaledToWidth(320, QtCore.Qt.SmoothTransformation)
		self.imgPreview.setPixmap(pix)

	def pullScreen(self):
		"""Получить экран"""
		print "PULL!"

	def pushScreen(self):
		"""Отправить экран"""
		self.updateScreenshot()
		print "PUSH!"

	def initTrayIcon(self):
		"""Инициализация иконки в системном трее"""
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
