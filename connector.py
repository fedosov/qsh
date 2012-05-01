# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov"
__maintainer__ = "Mikhail Fedosov"
__email__ = "tbs.micle@gmail.com"
__doc__ = u"Networking"

from __init__ import *
from PySide import QtNetwork

class Connector():
	"""Processing network messages"""
	def __init__(self):
		self.known_hosts = []
		self.socket_udp = QtNetwork.QUdpSocket()
		self.socket_udp.bind(APP_BROADCAST_PORT)
		self.socket_udp.readyRead.connect(self.udpReadyRead)

	def udpReadyRead(self):
		"""Incoming UDP message (datagram)"""
		while self.socket_udp.hasPendingDatagrams():
			(data, sender, senderPort) = self.socket_udp.readDatagram(self.socket_udp.pendingDatagramSize())
			if "|" in data:
				data_fields = unicode(data).split("|")
				data_msg, data_uuid = data_fields[0], data_fields[1]
				# сообщение получено от Qsh и UUID приложения отличается от собственного (чужое сообщение)
				if data_msg == APP_HELLO_MSG and data_uuid != unicode(APP_UUID):
					self.known_hosts.append(sender)

	def helloAll(self):
		"""Broadcast Hello to everyone in the network"""
		self.socket_udp.writeDatagram("%s|%s" % (APP_HELLO_MSG, APP_UUID), QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast), APP_BROADCAST_PORT)


# JUST INFO:

#	def submitScreen(self):
#		# Creating screen image buffer
#		screenBA = QtCore.QByteArray()
#		screenBuf = QtCore.QBuffer(screenBA)
#		screenBuf.open(QtCore.QBuffer.WriteOnly)
#		# Saving screen to image
#		self.screen.save(screenBuf, SCREEN_IMAGE_TYPE, SCREEN_IMAGE_QUALITY)
#		screenData = screenBuf.data()
#		ptr = 0
#		# UDP datagram size
#		packet_size = 800
#		sent_packets = 0
#		while ptr < QtCore.QByteArray(screenData).size():
#			self.socket.writeDatagram(screenData.mid(ptr, packet_size), QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast), APP_PORT)
#			ptr += packet_size
#			sent_packets += 1
#		print "SENT %i BYTES, %i PACKETS" % (len(screenData), sent_packets)

#	def socketReadyRead(self):
#		print "socketReadyRead"
#		allData = QtCore.QByteArray()
#		recv_packets = 0
#		while self.socket.hasPendingDatagrams():
#			#print "IN <<", self.socket.pendingDatagramSize()
#			(data, sender, senderPort) = self.socket.readDatagram(self.socket.pendingDatagramSize())
#			allData += data
#			recv_packets += 1
#		print "RECEIVED %i BYTES, %i PACKETS" % (len(allData), recv_packets)
#		self.screen = QtGui.QPixmap()
#		self.screen.loadFromData(allData, SCREEN_IMAGE_TYPE)
#		self.imgPreview.setPixmap(self.screen)

