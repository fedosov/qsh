# -*- coding: utf-8 -*-
from PySide.QtCore import SIGNAL

__author__ = "Mikhail Fedosov"

import sys
import PySide
from PySide import QtGui, QtCore, QtNetwork
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

		buttonBox = QtGui.QDialogButtonBox()
		self.btnPush = QPushButton(u"Отправка картинки")
		self.btnPush.clicked.connect(self.pushScreen)
		buttonBox.addButton(self.btnPush, QtGui.QDialogButtonBox.ActionRole)
		self.btnPull = QPushButton(u"Загрузка картинки")
		self.btnPull.clicked.connect(self.pullScreen)
		buttonBox.addButton(self.btnPull, QtGui.QDialogButtonBox.ActionRole)

		self.socket = QtNetwork.QUdpSocket(self)
		self.socket.bind(7740)
		self.socket.readyRead.connect(self.socketReadyRead)

		screenBA = QtCore.QByteArray()
		screenBuf = QtCore.QBuffer(screenBA)
		screenBuf.open(QtCore.QBuffer.WriteOnly)
		self.screen.save(screenBuf, "JPG", 0)
		print type(screenBuf.data()), len(screenBuf.data())
		self.socket.writeDatagram(screenBuf.data(), QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast), 7740)

		layout = QVBoxLayout()
		layout.addWidget(self.imgPreview)
		layout.addWidget(buttonBox)
		self.setLayout(layout)

	def socketReadyRead(self):
		print "socketReadyRead"
		while self.socket.hasPendingDatagrams():
			print "IN!", self.socket.pendingDatagramSize()
			(data, sender, senderPort) = self.socket.readDatagram(self.socket.pendingDatagramSize())
			print sender, senderPort, len(data)
#			screenBA = QtCore.QByteArray()
#			screenBuf = QtCore.QBuffer(screenBA)
#			screenBuf.open(QtCore.QBuffer.WriteOnly)
#			screenBuf.setData(data)
			self.screen = QtGui.QPixmap()
			self.screen.loadFromData(data, "JPG")
			self.imgPreview.setPixmap(self.screen)


	def updateScreenshot(self):
		"""Снять и обновить скриншот своего компьютера"""
		desktop_size = QtGui.QApplication.desktop().size()
		self.screen = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId())
		self.screen = self.screen.copy(0, 0, desktop_size.width(), desktop_size.height()).scaledToWidth(120, QtCore.Qt.SmoothTransformation)
		self.imgPreview.setPixmap(self.screen)

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
