# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

import logging

from qsh import *

from PySide import QtNetwork

class Connector():
	"""Processing network messages"""
	def __init__(self):
		self.known_hosts = set()
		self.socket_udp = QtNetwork.QUdpSocket()
		self.socket_udp.bind(APP_BROADCAST_PORT)
		logging.debug("socket_bound")
		self.socket_udp.readyRead.connect(self.udpReadyRead)

	def udpReadyRead(self):
		"""Incoming UDP message (datagram)"""
		while self.socket_udp.hasPendingDatagrams():
			(data, sender, senderPort) = self.socket_udp.readDatagram(self.socket_udp.pendingDatagramSize())
			if "|" in data:
				data_fields = unicode(data).split("|")
				data_msg, data_uuid = data_fields[0], data_fields[1]

				# message received from Qsh and app UUID differs
				if data_uuid != unicode(APP_UUID):

					# greeting from other node
					if data_msg == APP_HELLO_MSG:
						logging.debug("got_greeting_[%s][%s]" % (data_uuid, sender.toString()))
						self.known_hosts.add((data_uuid, sender))

					# goodbye from other node
					elif data_msg == APP_BYE_MSG:
						logging.debug("got_goodbye_[%s][%s]" % (data_uuid, sender.toString()))
						self.known_hosts.remove((data_uuid, sender))

	def helloAll(self):
		"""Broadcast Hello to everyone in the network"""
		self.socket_udp.writeDatagram("%s|%s" % (APP_HELLO_MSG, APP_UUID), QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast), APP_BROADCAST_PORT)
		logging.debug("hello_all")

	def byeAll(self):
		"""Broadcast Bye to everyone in the network"""
		self.socket_udp.writeDatagram("%s|%s" % (APP_BYE_MSG, APP_UUID), QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast), APP_BROADCAST_PORT)
		logging.debug("bye_all")

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

