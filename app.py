# -*- coding: utf-8 -*-
from PySide.QtCore import SIGNAL

__author__ = "Mikhail Fedosov"

import sys
import PySide
from PySide import QtGui, QtCore, QtNetwork
from PySide.QtGui import *

APP_PORT = 7740
SCREEN_IMAGE_TYPE = "JPG"
SCREEN_IMAGE_QUALITY = 40

class ScreenViewWindow(QDialog):
	def __init__(self, parent=None):
		super(ScreenViewWindow, self).__init__(parent)
		self.setWindowTitle(u"Просмотр экрана")
		self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		self.initTrayIcon()

		self.imgPreview = QLabel()
		self.imgPreview.setFixedSize(640, 480)
		self.updateScreenshot()

		buttonBox = QtGui.QDialogButtonBox()
		self.btnPush = QPushButton(u"Отправка картинки")
		self.btnPush.clicked.connect(self.pushScreen)
		buttonBox.addButton(self.btnPush, QtGui.QDialogButtonBox.ActionRole)
		self.btnPull = QPushButton(u"Загрузка картинки")
		self.btnPull.clicked.connect(self.pullScreen)
		buttonBox.addButton(self.btnPull, QtGui.QDialogButtonBox.ActionRole)

		self.socket = QtNetwork.QUdpSocket(self)
		self.socket.bind(APP_PORT)
		self.socket.readyRead.connect(self.socketReadyRead)

		self.submitScreen()

		layout = QVBoxLayout()
		layout.addWidget(self.imgPreview)
		layout.addWidget(buttonBox)
		self.setLayout(layout)

	def submitScreen(self):
		# Creating screen image buffer
		screenBA = QtCore.QByteArray()
		screenBuf = QtCore.QBuffer(screenBA)
		screenBuf.open(QtCore.QBuffer.WriteOnly)
		# Saving screen to image
		self.screen.save(screenBuf, SCREEN_IMAGE_TYPE, SCREEN_IMAGE_QUALITY)
		screenData = screenBuf.data()
		ptr = 0
		# UDP datagram size
		packet_size = 800
		sent_packets = 0
		while ptr < QtCore.QByteArray(screenData).size():
			self.socket.writeDatagram(screenData.mid(ptr, packet_size), QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast), APP_PORT)
			ptr += packet_size
			sent_packets += 1
		print "SENT %i BYTES, %i PACKETS" % (len(screenData), sent_packets)


	def socketReadyRead(self):
		print "socketReadyRead"
		allData = QtCore.QByteArray()
		recv_packets = 0
		while self.socket.hasPendingDatagrams():
			#print "IN <<", self.socket.pendingDatagramSize()
			(data, sender, senderPort) = self.socket.readDatagram(self.socket.pendingDatagramSize())
			allData += data
			recv_packets += 1
		print "RECEIVED %i BYTES, %i PACKETS" % (len(allData), recv_packets)
		self.screen = QtGui.QPixmap()
		self.screen.loadFromData(allData, SCREEN_IMAGE_TYPE)
		self.imgPreview.setPixmap(self.screen)


	def updateScreenshot(self):
		"""Снять и обновить скриншот своего компьютера"""
		desktop_size = QtGui.QApplication.desktop().size()
		self.screen = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId())
		self.screen = self.screen.copy(0, 0, desktop_size.width(), desktop_size.height()).scaledToWidth(640, QtCore.Qt.SmoothTransformation)
		#self.imgPreview.setPixmap(self.screen)

	def pullScreen(self):
		"""Получить экран"""
		print "PULL!"

	def pushScreen(self):
		"""Отправить экран"""
		self.updateScreenshot()
		self.submitScreen()
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
