# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

# PySide
from PySide import QtCore
from PySide.QtGui import *

# QSH
from config import AppConfig


class MainTrayIcon(QtCore.QObject):

	def __init__(self, parent, callbacks):
		super(MainTrayIcon, self).__init__(parent)

		# state
		self.incomingTotal = 0
		self.incomingUnread = 0

		self.parent = parent

		self.pixmaps = dict()
		self.pixmaps["unread"] = QPixmap("resources/img/menu_bar_extras_icon__unread.png")
		self.pixmaps["unread_alt"] = QPixmap("resources/img/menu_bar_extras_icon__unread_alt.png")

		self.icons = dict()
		self.icons["default"] = QIcon("resources/img/menu_bar_extras_icon.png")
		self.icons["default"].addPixmap("resources/img/menu_bar_extras_icon_alt.png", QIcon.Selected)
		self.icons["loading"] = QIcon("resources/img/menu_bar_extras_icon__loading.png")
		self.icons["loading"].addPixmap("resources/img/menu_bar_extras_icon__loading_alt.png", QIcon.Selected)

		self.actionQuit = QAction(u"Quit", self.parent, triggered=callbacks["quit"])
		self.actionShowConfigurationDialog = QAction(u"Configuration", self.parent, triggered=callbacks["configuration"])
		self.actionShowScreenViewDialog = QAction(self.parent, triggered=callbacks["incoming"])

		self.menu = QMenu()
		self.updateMenu()

		self.icon = QSystemTrayIcon(self.parent)
		self.setIconDefault()
		self.icon.setContextMenu(self.menu)
		self.icon.show()

	def showMessage(self, title, message):
		self.icon.showMessage(title, message)

	def updateMenu(self):
		self.menu.clear()

		# DEBUG (app UUID in tray icon popup menu):
		from config import APP_UUID
		username = AppConfig.get_username()
		if username:
			self.actionMe = QAction(unicode(username), self.parent)
		else:
			self.actionMe = QAction(unicode(APP_UUID), self.parent)
		self.actionMe.setDisabled(True)
		self.menu.addAction(self.actionMe)
		self.menu.addSeparator()

		# known hosts list
		if self.parent.connector and self.parent.connector.known_hosts:
			for host_uuid, host_data in self.parent.connector.known_hosts.iteritems():
				if host_data["username"]:
					host_str = "%s - [%s:%s]" % (host_data["username"].decode("utf-8"), host_data["host"].toString(), host_data["port"])
				else:
					host_str = "[%s:%s]" % (host_data["host"].toString(), host_data["port"])
				self.menu.addAction(QAction(host_str, self.parent, triggered=lambda: self.parent.shareScreen(host_data["host"], host_data["port"])))
			self.menu.addSeparator()

		# incoming data
		self.actionShowScreenViewDialog.setDisabled(self.incomingTotal == 0)
		self.actionShowScreenViewDialog.setText("(%i) Incoming" % self.incomingUnread if self.incomingUnread else "Incoming")
		self.menu.addAction(self.actionShowScreenViewDialog)
		self.menu.addSeparator()

		self.menu.addAction(self.actionShowConfigurationDialog)
		self.menu.addAction(self.actionQuit)

	def setIconDefault(self):
		if self.incomingUnread > 0:
			self.setIconUnread(self.incomingUnread)
		else:
			self.icon.setIcon(self.icons["default"])

	def setIconLoading(self):
		self.icon.setIcon(self.icons["loading"])

	def setIconUnread(self, count=1):
		font = QFont("Tahoma", 8, QFont.Bold)
		font.setStyleHint(QFont.SansSerif)
		font.setStyleStrategy(QFont.PreferQuality)

		new_icon_pixmap = self.pixmaps["unread"].copy()
		painter = QPainter(new_icon_pixmap)
		painter.setFont(font)
		painter.drawText(0, 3, 14, 16, QtCore.Qt.AlignRight, str(count))
		painter.end()

		new_icon = QIcon(new_icon_pixmap)

		new_icon_alt_pixmap = self.pixmaps["unread_alt"].copy()
		painter = QPainter(new_icon_alt_pixmap)
		painter.setFont(font)
		painter.setPen(QPen(QColor(255, 255, 255)))
		painter.drawText(0, 3, 15, 16, QtCore.Qt.AlignRight, str(count))
		painter.end()

		new_icon.addPixmap(new_icon_alt_pixmap, QIcon.Selected)

		self.icon.setIcon(new_icon)
