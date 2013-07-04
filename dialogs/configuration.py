# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

# PySide
from PySide import QtGui
from PySide.QtGui import *

from config import AppConfig


class ConfigurationDialog(QDialog):

	def __init__(self, application, parent=None):
		super(ConfigurationDialog, self).__init__(parent)

		self.application = application
		self.setWindowTitle(u"QSH config")
		self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))

		layout = QVBoxLayout()

		layout.addWidget(QtGui.QLabel("Username:"))
		self.editUsername = QtGui.QLineEdit(AppConfig.get_username())
		layout.addWidget(self.editUsername)

		layout.addWidget(QtGui.QLabel("Heartbeat interval (ms):"))
		self.editHeartbeatInterval = QtGui.QLineEdit(str(AppConfig.get_heartbeat_interval()))
		layout.addWidget(self.editHeartbeatInterval)

		buttonBox = QtGui.QDialogButtonBox()
		self.btnCancel = QPushButton(u"Cancel")
		self.btnCancel.clicked.connect(self.close)
		buttonBox.addButton(self.btnCancel, QtGui.QDialogButtonBox.RejectRole)
		self.btnSave = QPushButton(u"Save")
		self.btnSave.clicked.connect(self.save)
		buttonBox.addButton(self.btnSave, QtGui.QDialogButtonBox.AcceptRole)
		layout.addWidget(buttonBox)

		self.setLayout(layout)

	def save(self):
		AppConfig.set_username(self.editUsername.text())
		try:
			AppConfig.set_heartbeat_interval(int(self.editHeartbeatInterval.text()))
		except ValueError:
			pass
		self.application.updateTrayIconMenu()
		self.application.helloAllTimer.stop()
		self.application.helloAllTimer.start(AppConfig.get_heartbeat_interval())
		self.application.connector.helloAll()
		self.close()
