# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

# PySide
from PySide import QtCore
from PySide.QtGui import *

# QSH
from config import AppConfig


class MainTrayIcon(object):

	def __init__(self, parent):
		# state
		self.incomingTotal = 0
		self.incomingUnread = 0

		self.parent = parent

		self.trayIconIcon = QIcon("resources/img/menu_bar_extras_icon.png")
		self.trayIconIcon.addPixmap("resources/img/menu_bar_extras_icon_alt.png", QIcon.Selected)

		self.trayIconLoading = QIcon("resources/img/menu_bar_extras_icon__loading.png")
		self.trayIconLoading.addPixmap("resources/img/menu_bar_extras_icon__loading_alt.png", QIcon.Selected)

		self.trayIconUnreadPixmap = QPixmap("resources/img/menu_bar_extras_icon__unread.png")
		self.trayIconUnreadAltPixmap = QPixmap("resources/img/menu_bar_extras_icon__unread_alt.png")

		self.actionQuit = QAction(u"Quit", self.parent, triggered=self.parent.quit)
		self.actionShowConfigurationDialog = QAction(u"Configuration", self.parent, triggered=self.parent.showConfigurationDialog)
		self.actionShowScreenViewDialog = QAction(self.parent, triggered=self.parent.showScreenViewDialog)

		self.trayIconMenu = QMenu()
		self.updateTrayIconMenu()

		self.trayIcon = QSystemTrayIcon(self.parent)
		self.trayIconSetIconDefault()
		self.trayIcon.setContextMenu(self.trayIconMenu)
		self.trayIcon.show()

	def updateTrayIconMenu(self):
		self.trayIconMenu.clear()

		# DEBUG (app UUID in tray icon popup menu):
		from config import APP_UUID
		username = AppConfig.get_username()
		if username:
			trayIconMenuUUIDAction = QAction(unicode(username), self.parent)
		else:
			trayIconMenuUUIDAction = QAction(unicode(APP_UUID), self.parent)
		trayIconMenuUUIDAction.setDisabled(True)
		self.trayIconMenu.addAction(trayIconMenuUUIDAction)
		self.trayIconMenu.addSeparator()

		# known hosts list
		if self.parent.connector and self.parent.connector.known_hosts:
			for host_uuid, host_data in self.parent.connector.known_hosts.iteritems():
				if host_data["username"]:
					host_str = "%s - [%s:%s]" % (host_data["username"].decode("utf-8"), host_data["host"].toString(), host_data["port"])
				else:
					host_str = "[%s:%s]" % (host_data["host"].toString(), host_data["port"])
				self.trayIconMenu.addAction(QAction(host_str, self.parent, triggered=lambda: self.parent.shareScreen(host_data["host"], host_data["port"])))
			self.trayIconMenu.addSeparator()

		# incoming data
		self.actionShowScreenViewDialog.setDisabled(self.incomingTotal == 0)
		self.actionShowScreenViewDialog.setText("(%i) Incoming" % self.incomingUnread if self.incomingUnread else "Incoming")
		self.trayIconMenu.addAction(self.actionShowScreenViewDialog)
		self.trayIconMenu.addSeparator()

		self.trayIconMenu.addAction(self.actionShowConfigurationDialog)
		self.trayIconMenu.addAction(self.actionQuit)

	def trayIconSetIconDefault(self):
		if self.incomingUnread > 0:
			self.trayIconSetIconUnread(self.incomingUnread)
		else:
			self.trayIcon.setIcon(self.trayIconIcon)

	def trayIconSetIconLoading(self):
		self.trayIcon.setIcon(self.trayIconLoading)

	def trayIconSetIconUnread(self, count=1):
		font = QFont("Tahoma", 8, QFont.Bold)
		font.setStyleHint(QFont.SansSerif)
		font.setStyleStrategy(QFont.PreferQuality)

		new_icon_pixmap = self.trayIconUnreadPixmap.copy()
		painter = QPainter(new_icon_pixmap)
		painter.setFont(font)
		painter.drawText(0, 3, 14, 16, QtCore.Qt.AlignRight, str(count))
		painter.end()

		new_icon = QIcon(new_icon_pixmap)

		new_icon_alt_pixmap = self.trayIconUnreadAltPixmap.copy()
		painter = QPainter(new_icon_alt_pixmap)
		painter.setFont(font)
		painter.setPen(QPen(QColor(255, 255, 255)))
		painter.drawText(0, 3, 15, 16, QtCore.Qt.AlignRight, str(count))
		painter.end()

		new_icon.addPixmap(new_icon_alt_pixmap, QIcon.Selected)

		self.trayIcon.setIcon(new_icon)
