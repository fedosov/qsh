# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov"

import sys
import PySide
from PySide import QtGui
from PySide.QtCore import *
from PySide.QtGui import *

class ScreenViewWindow(QDialog):
	def __init__(self, parent=None):
		super(ScreenViewWindow, self).__init__(parent)
		self.setWindowTitle(u"Просмотр экрана")
		self.initTrayIcon()

		self.imgPreview = QtGui.QPixmap("trayico.png")

		self.btnPush = QtGui.QPushButton(u"Отправка картинки")
		self.btnPush.clicked.connect(self.pushScreen)
		self.btnPull = QtGui.QPushButton(u"Загрузка картинки")
		self.btnPull.clicked.connect(self.pullScreen)

		layout = QVBoxLayout()
		#layout.addWidget(self.imgPreview)
		layout.addWidget(self.btnPush)
		layout.addWidget(self.btnPull)
		self.setLayout(layout)

	def pullScreen(self):
		"""Получить экран"""
		print "PULL!"

	def pushScreen(self):
		"""Отправить экран"""
		print "PUSH!"

	def initTrayIcon(self):
		"""Инициализация иконки в системном трее"""
		self.trayIconIcon = PySide.QtGui.QIcon("trayico.png")

		self.actionSendScreenshot = QtGui.QAction(u"Отправить экран", self, triggered=self.pushScreen)
		self.actionQuit = QtGui.QAction(u"Выход", self, triggered=QtGui.qApp.quit)

		self.trayIconMenu = QtGui.QMenu(self)
		self.trayIconMenu.addAction(self.actionSendScreenshot)
		self.trayIconMenu.addAction(self.actionQuit)

		self.trayIcon = PySide.QtGui.QSystemTrayIcon(self)
		self.trayIcon.setIcon(self.trayIconIcon)
		self.trayIcon.setContextMenu(self.trayIconMenu)
		self.trayIcon.show()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	windowScreenView = ScreenViewWindow()
	windowScreenView.show()
	sys.exit(app.exec_())
