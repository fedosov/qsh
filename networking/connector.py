# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

import base64
import logging

from PySide import QtNetwork, QtCore

from config import *

logger = logging.getLogger(__name__)


class Connector():

	""" Processing network messages
	"""
	def __init__(self):
		self.known_hosts_updated_callback = lambda: None
		self.got_image_callback = lambda: None
		self.receiving_start_callback = lambda: None
		self.sending_end_callback = lambda: None
		self.clearKnownHosts()

		self.max_socket_read_iterations = 500

		# UDP
		self.socket_udp = QtNetwork.QUdpSocket()
		self.socket_udp.bind(APP_BROADCAST_PORT, QtNetwork.QUdpSocket.ReuseAddressHint)
		logger.debug("socket_bound")
		self.socket_udp.readyRead.connect(self.udpReadyRead)

		# TCP
		self.socket_tcp = QtNetwork.QTcpServer()
		self.socket_tcp.incomingConnection = self.tcpIncomingConnection
		self.socket_tcp.listen(address=QtNetwork.QHostAddress("0.0.0.0"), port=APP_PORT)

	def clearKnownHosts(self):
		self.known_hosts = dict()
		self.known_hosts_updated_callback()

	def updateKnownHosts(self):
		self.markKnownHostsAsDead()
		QtCore.QTimer.singleShot(500, self.deleteAllDeadKnownHosts)
		self.helloAll()

	def markKnownHostsAsDead(self):
		for key in self.known_hosts.keys():
			self.known_hosts[key]["alive"] = False

	def deleteAllDeadKnownHosts(self):
		for key in self.known_hosts.keys():
			if not self.known_hosts[key]["alive"]:
				del self.known_hosts[key]

	# TCP

	def tcpIncomingConnection(self, socket_descriptor):
		self.receiving_start_callback()
		self.receive_thread = ReceiveThread(socket_descriptor, self.max_socket_read_iterations)
		self.receive_thread.start()
		if self.got_image_callback:
			self.receive_thread.complete.connect(self.got_image_callback)

	def submitScreen(self, host, port, data):
		self.submit_thread = SubmitThread(host, port, data)
		self.submit_thread.start()
		if self.sending_end_callback:
			self.submit_thread.complete.connect(self.sending_end_callback)

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
				if data_uuid != unicode(APP_UUID) or APP_DEBUG:

					# greeting from other node
					if data_msg == APP_HELLO_MSG:
						username = data_fields[2]
						flag = data_fields[3]
						port = data_fields[4]
						logger.debug("got_greeting_[%s][%s]" % (data_uuid, "%s:%s" % (sender.toString(), port)))
						self.known_hosts[data_uuid] = \
						{
							'host': sender,
						    'port': int(port),
						    'username': base64.decodestring(username),
						    'alive': True
						}
						self.known_hosts_updated_callback()
						# and so, be friendly
						if flag == 'reply':
							self.helloAll(flag='silent')
							logger.debug("hello_all_silent")

					# goodbye from other node
					elif data_msg == APP_BYE_MSG:
						port = data_fields[2]
						logger.debug("got_goodbye_[%s][%s]" % (data_uuid, "%s:%s" % (sender.toString(), port)))
						del self.known_hosts[data_uuid]
						self.known_hosts_updated_callback()

	def helloAll(self, flag='reply'):
		""" Broadcast Hello to everyone in the network
		flag: reply|silent -- determine whether you want to receive response greetings from other mates
		"""
		self.socket_udp.writeDatagram("%s|%s|%s|%s|%s" % (APP_HELLO_MSG, APP_UUID, base64.encodestring(AppConfig.get_username().encode("utf-8")), flag, APP_PORT), QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast), APP_BROADCAST_PORT)
		logger.debug("hello_all")

	def byeAll(self):
		""" Broadcast Bye to everyone in the network
		"""
		self.socket_udp.writeDatagram("%s|%s|%s" % (APP_BYE_MSG, APP_UUID, APP_PORT), QtNetwork.QHostAddress(QtNetwork.QHostAddress.Broadcast), APP_BROADCAST_PORT)
		logger.debug("bye_all")


class SubmitThread(QtCore.QThread):

	""" Submitting screenshot
	"""
	complete = QtCore.Signal()

	def __init__(self, host, port, data):
		QtCore.QThread.__init__(self)
		self.host = host
		self.port = port
		self.data = data

	def run(self):
		socket = QtNetwork.QTcpSocket()

		socket.connectToHost(self.host, self.port)
		if not socket.waitForConnected(500):
			# retry connection
			socket.connectToHost(self.host, self.port)
			if not socket.waitForConnected(500):
				logger.info("--> TCP connection timeout")
				self.complete.emit()
				return

		data_stream = QtCore.QDataStream(socket)
		data_stream.setVersion(QtCore.QDataStream.Qt_4_8)
		data_stream.writeUInt32(self.data.size())
		data_stream.writeString(unicode(APP_UUID))
		data_stream.unsetDevice()

		socket.write(self.data.data())
		socket.flush()

		while socket.bytesToWrite() > 0:
			if socket.state() == socket.ConnectedState:
				socket.waitForBytesWritten(100)
			else:
				logger.debug("--> TCP host suddenly disconnected")
				self.complete.emit()
				return

		logger.debug("--> TCP written %i bytes" % self.data.size())

		socket.disconnectFromHost()
		logger.debug("--> TCP disconnected")
		self.complete.emit()


class ReceiveThread(QtCore.QThread):

	""" Receiving screenshot
	"""
	complete = QtCore.Signal(str, QtCore.QByteArray)

	def __init__(self, socket_descriptor, max_socket_read_iterations=100):
		QtCore.QThread.__init__(self)
		self.socket_descriptor = socket_descriptor
		self.max_socket_read_iterations = max_socket_read_iterations

	def run(self):
		logger.debug("<-- TCP connection")
		socket = QtNetwork.QTcpSocket()
		socket.setSocketDescriptor(self.socket_descriptor)

		socket.waitForReadyRead(1000)

		data_stream = QtCore.QDataStream(socket)
		data_stream.setVersion(QtCore.QDataStream.Qt_4_8)
		data_size = data_stream.readUInt32()
		data_uuid = data_stream.readString()
		data_stream.unsetDevice()

		logger.debug("<-- TCP incoming data size: %i bytes" % data_size)

		data = QtCore.QByteArray()

		read_iterations = 0

		while data.size() < data_size and read_iterations < self.max_socket_read_iterations:
			data_read = socket.readAll()
			logger.debug("<-- READ %i bytes" % data_read.size())
			data.append(data_read)
			read_iterations += 1
			socket.waitForReadyRead(100)

		logger.debug("<-- TCP read %i bytes" % data.size())

		if data.size() != data_size:
			# broken data received
			data.clear()

		self.complete.emit(data_uuid, data)


