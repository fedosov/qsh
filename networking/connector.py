# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

import logging

from PySide import QtNetwork, QtCore

from qsh import *

logger = logging.getLogger(__name__)


class Connector():

	""" Processing network messages
	"""
	def __init__(self):
		self.known_hosts = set()
		self.known_hosts_updated_callback = None

		# UDP
		self.socket_udp = QtNetwork.QUdpSocket()
		self.socket_udp.bind(APP_BROADCAST_PORT, QtNetwork.QUdpSocket.ReuseAddressHint)
		logger.debug("socket_bound")
		self.socket_udp.readyRead.connect(self.udpReadyRead)

		# TCP
		self.socket_tcp = QtNetwork.QTcpServer()
		self.socket_tcp.incomingConnection = self.tcpIncomingConnection
		self.socket_tcp.listen(address=QtNetwork.QHostAddress("0.0.0.0"), port=APP_PORT)

	# TCP

	def tcpIncomingConnection(self, socket_descriptor):
		logger.debug("<-- TCP connection")
		socket = QtNetwork.QTcpSocket()
		socket.setSocketDescriptor(socket_descriptor)
		socket.waitForReadyRead(1000)
		data = QtCore.QByteArray(socket.readAll())
		logger.debug("<-- TCP read %i bytes" % data.size())
		# TODO: show image

	def submitScreen(self, host, port, data):
		socket = QtNetwork.QTcpSocket()

		socket.connectToHost(host, port)
		logger.debug("--> TCP connect...")
		if not socket.waitForConnected(1000):
			logger.info("--> TCP connection timeout")
			return

		socket.write(data)

		if not socket.waitForBytesWritten():
			logger.error("--> TCP write error: %s" % socket.error())
			return
		logger.debug("--> TCP data written %i bytes" % data.size())

		socket.disconnectFromHost()
		logger.debug("--> TCP disconnected")

	# UDP

	def udpReadyRead(self):
		""" Incoming UDP message (datagram)
		"""
		while self.socket_udp.hasPendingDatagrams():
			(data, sender, senderPort) = self.socket_udp.readDatagram(self.socket_udp.pendingDatagramSize())
			logger.debug("[%s] <-- `%s`" % (APP_UUID, data))
			if "|" in data:
				data_fields = unicode(data).split("|")
				data_msg, data_uuid = data_fields[0], data_fields[1]

				# message received from Qsh and app UUID differs
				if data_uuid != unicode(APP_UUID):

					# greeting from other node
					if data_msg == APP_HELLO_MSG:
						flag = data_fields[2]
						port = data_fields[3]
						logger.debug("got_greeting_[%s][%s]" % (data_uuid, "%s:%s" % (sender.toString(), port)))
						self.known_hosts.add((data_uuid, sender, int(port)))
						if self.known_hosts_updated_callback:
							self.known_hosts_updated_callback()
						# and so, be friendly
						if flag == 'reply':
							self.helloAll(flag='silent')
							logger.debug("hello_all_silent")

					# goodbye from other node
					elif data_msg == APP_BYE_MSG:
						port = data_fields[2]
						logger.debug("got_goodbye_[%s][%s]" % (data_uuid, "%s:%s" % (sender.toString(), port)))
						self.known_hosts.remove((data_uuid, sender, int(port)))
						if self.known_hosts_updated_callback:
							self.known_hosts_updated_callback()

	def helloAll(self, flag='reply'):
		""" Broadcast Hello to everyone in the network
		flag: reply|silent -- determine whether you want to receive response greetings from other mates
		"""
		self.socket_udp.writeDatagram("%s|%s|%s|%s" % (APP_HELLO_MSG, APP_UUID, flag, APP_PORT), QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast), APP_BROADCAST_PORT)
		logger.debug("hello_all")

	def byeAll(self):
		""" Broadcast Bye to everyone in the network
		"""
		self.socket_udp.writeDatagram("%s|%s|%s" % (APP_BYE_MSG, APP_UUID, APP_PORT), QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast), APP_BROADCAST_PORT)
		logger.debug("bye_all")


# FYI:

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

