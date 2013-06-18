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
		self.application.updateTrayIconMenu()
		self.application.connector.helloAll()
		self.close()
