# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

import datetime

# PySide
from PySide.QtGui import *
from PySide import QtGui, QtCore

# QSH
from config import APP_UUID, SCREEN_IMAGE_TYPE


class ScreenViewDialog(QDialog):

	def __init__(self, application, parent=None):
		super(ScreenViewDialog, self).__init__(parent)

		self.application = application
		self.setWindowTitle(u"QSH" % APP_UUID)
		self.resize(160, 120)
		self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))

		self.desktopWidget = QDesktopWidget()
		self.screenGeometry = self.desktopWidget.screenGeometry()

		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)
		self.setLayout(layout)

	def processReceivedImage(self, data_uuid, data, known_hosts):
		""" Show received screenshot
		"""
		screen_preview_box = QFrame()
		screen_preview_box.setLayout(QVBoxLayout())
		screen_preview = QLabel()
		screen_preview.setFixedHeight(120)
		screen = QtGui.QPixmap()
		screen.loadFromData(data, SCREEN_IMAGE_TYPE)
		screen_preview.original_pixmap = screen.copy()
		screen = screen.scaledToHeight(120, QtCore.Qt.SmoothTransformation)
		screen_preview.setPixmap(screen)
		screen_preview.installEventFilter(ScreenClickEventFilter(self))
		screen_preview.setCursor(QtCore.Qt.PointingHandCursor)

		# add screen label (sender, date)
		screen_preview_box.layout().addWidget(screen_preview)
		screen_preview_label_text = "Unknown user"
		screen_preview_label = QLabel()
		if data_uuid in known_hosts.keys():
			screen_preview_label_text = known_hosts[data_uuid]["username"]
		screen_preview_label_text = "%s @ %s" % (screen_preview_label_text, datetime.datetime.now().strftime("%H:%M"))
		screen_preview_label.setText(screen_preview_label_text)
		screen_preview_label.setFont(QFont("Tahoma", 10))
		screen_preview_box.layout().addWidget(screen_preview_label)

		# growl.notify(
		# 	noteType="Incoming screenshots",
		# 	title="QSH: Screenshot received",
		# 	description=screen_preview_label_text,
		# 	sticky=False,
		# 	priority=1,
		# )

		# remove button
		screen_preview_remove = QPushButton("Remove")
		screen_preview_remove.screen_preview_box = screen_preview_box
		screen_preview_remove.clicked.connect(self.screenPreviewRemoveClicked)
		screen_preview_box.layout().addWidget(screen_preview_remove)

		self.layout().addWidget(screen_preview_box)

		# QtCore.QTimer.singleShot(0, self.showWindow)

	def showWindow(self):
		self.show()
		self.raise_()
		self.activateWindow()
		QtCore.QTimer.singleShot(0, self.updateWindowPositionAndSize)

	def updateWindowPositionAndSize(self):
		self.resize(self.minimumSizeHint())
		self.move(self.screenGeometry.width() / 2 - self.width() / 2,
		          self.screenGeometry.height() - 400)

	def screenPreviewShow(self, screen_preview):
		""" Screen 'show' button click
		"""
		assert isinstance(screen_preview, QLabel)
		screen_preview.screen_preview_fs = QLabel()
		# copy and resize original image
		screen_preview.screen_preview_fs.setPixmap(
			screen_preview.original_pixmap.copy().scaled(
				self.screenGeometry.width(),
				self.screenGeometry.height(),
				QtCore.Qt.KeepAspectRatio,
				QtCore.Qt.SmoothTransformation
			)
		)
		# show fullscreen
		screen_preview.screen_preview_fs.showFullScreen()
		screen_preview.screen_preview_fs.raise_()
		screen_preview.screen_preview_fs.activateWindow()

	def screenPreviewRemoveClicked(self):
		""" Screen 'remove' button click
		"""
		screen_preview_box = self.sender().screen_preview_box
		assert isinstance(screen_preview_box, QFrame)
		screen_preview_box.deleteLater()
		self.application.incomingTotal -= 1
		self.application.updateTrayIconMenu()
		if self.application.incomingTotal == 0:
			self.close()
		else:
			QtCore.QTimer.singleShot(0, self.showWindow)


class ScreenClickEventFilter(QtCore.QObject):

	def eventFilter(self, obj, event):
		""" Screenshot preview clicked
		"""
		parent = self.parent()
		assert isinstance(parent, ScreenViewDialog)
		if event.type() == QtCore.QEvent.MouseButtonPress:
			parent.screenPreviewShow(obj)
			return True
		if event.type() == QtCore.QEvent.MouseButtonRelease:
			if obj.screen_preview_fs:
				obj.screen_preview_fs.deleteLater()
			return True
		else:
			return QtCore.QObject.eventFilter(self, obj, event)
