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

		pix = QPixmap("trayico.png")
		pix = pix.copy(0, 0, 16, 16).scaled(320, 240, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
		self.imgPreview = QLabel()
		self.imgPreview.setFixedSize(320, 240)
		self.imgPreview.setPixmap(pix)
		#self.imgPreview = QtGui.QWidget()
		#self.imgPreview.setFixedSize(500, 500)
		#self.imgPreview.setP
		#image = QtGui.QImage("trayico.png")
		#self.imgPreview.pa

		self.btnPush = QPushButton(u"Отправка картинки")
		self.btnPush.clicked.connect(self.pushScreen)
		self.btnPull = QPushButton(u"Загрузка картинки")
		self.btnPull.clicked.connect(self.pullScreen)

		layout = QVBoxLayout()
		layout.addWidget(self.imgPreview)
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
