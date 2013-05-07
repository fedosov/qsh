# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

import logging

from PySide import QtNetwork

from qsh import *


class Connector():
	""" Processing network messages
	"""
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.known_hosts = set()
		self.known_hosts_updated_callback = None
		self.socket_udp = QtNetwork.QUdpSocket()
		self.socket_udp.bind(APP_BROADCAST_PORT, QtNetwork.QUdpSocket.ReuseAddressHint)
		self.logger.debug("socket_bound")
		self.socket_udp.readyRead.connect(self.udpReadyRead)

	def udpReadyRead(self):
		""" Incoming UDP message (datagram)
		"""
		while self.socket_udp.hasPendingDatagrams():
			(data, sender, senderPort) = self.socket_udp.readDatagram(self.socket_udp.pendingDatagramSize())
			self.logger.debug("[%s] <-- `%s`" % (APP_UUID, data))
			if "|" in data:
				data_fields = unicode(data).split("|")
				data_msg, data_uuid = data_fields[0], data_fields[1]

				# message received from Qsh and app UUID differs
				if data_uuid != unicode(APP_UUID):

					# greeting from other node
					if data_msg == APP_HELLO_MSG:
						flag = data_fields[2]
						port = data_fields[3]
						self.logger.debug("got_greeting_[%s][%s]" % (data_uuid, "%s:%s" % (sender.toString(), port)))
						self.known_hosts.add((data_uuid, sender, port))
						if self.known_hosts_updated_callback:
							self.known_hosts_updated_callback()
						# and so, be friendly
						if flag == 'reply':
							#time.sleep(1)
							self.helloTo(sender, flag='silent')
							self.logger.debug("hello_mate")

					# goodbye from other node
					elif data_msg == APP_BYE_MSG:
						port = data_fields[2]
						self.logger.debug("got_goodbye_[%s][%s]" % (data_uuid, "%s:%s" % (sender.toString(), port)))
						self.known_hosts.remove((data_uuid, sender, port))
						if self.known_hosts_updated_callback:
							self.known_hosts_updated_callback()

	def helloAll(self):
		""" Broadcast Hello to everyone in the network
		"""
		self.helloTo(QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast))
		self.logger.debug("hello_all")

	def helloTo(self, address, flag='reply'):
		""" Hello to your teammate

		flag: reply|silent -- determine whether you want to receive response greetings from other mates
		"""
		self.socket_udp.writeDatagram("%s|%s|%s|%s" % (APP_HELLO_MSG, APP_UUID, flag, APP_PORT), address, APP_BROADCAST_PORT)

	def byeAll(self):
		""" Broadcast Bye to everyone in the network
		"""
		self.socket_udp.writeDatagram("%s|%s|%s" % (APP_BYE_MSG, APP_UUID, APP_PORT), QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast), APP_BROADCAST_PORT)
		self.logger.debug("bye_all")


# FYI:

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

