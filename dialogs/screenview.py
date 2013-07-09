# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

import datetime

# PySide
from PySide.QtGui import *
from PySide import QtGui, QtCore

# QSH
from config import APP_UUID, SCREEN_IMAGE_TYPE


class ScreenViewDialog(QWidget):

	def __init__(self, application, parent=None):
		super(ScreenViewDialog, self).__init__(parent)

		self.application = application
		self.setWindowTitle(u"QSH" % APP_UUID)
		self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.installEventFilter(ScreenViewDialogEventFilter(self))

		self.desktopWidget = QDesktopWidget()
		self.screenGeometry = self.desktopWidget.screenGeometry()

		self.inFullScreenMode = False

		layout = QHBoxLayout()
		layout.setContentsMargins(0, 10, 0, 0)
		layout.setSpacing(0)
		self.setLayout(layout)

	def processReceivedImage(self, data_uuid, data, known_hosts):
		""" Show received screenshot
		"""
		screen = QtGui.QPixmap()
		screen.loadFromData(data, SCREEN_IMAGE_TYPE)
		if screen.isNull():
			# received broken image data
			return 0

		frameScreenPreview = QFrame()
		frameScreenPreview.setLayout(QVBoxLayout())

		imageScreenPreview = QLabel()
		imageScreenPreview.original_pixmap = screen.copy()
		screen = screen.scaledToHeight(100, QtCore.Qt.SmoothTransformation)
		imageScreenPreview.setFixedSize(screen.width(), 100)
		imageScreenPreview.setPixmap(screen)
		imageScreenPreview.installEventFilter(ScreenClickEventFilter(self))
		imageScreenPreview.setCursor(QtCore.Qt.PointingHandCursor)
		imageScreenPreview.setStyleSheet("""
		QLabel {
			border: 2px solid transparent;
			border-radius: 3px;
		}
		QLabel:hover {
			border-color: #fff;
		}
		""")
		frameScreenPreview.layout().addWidget(imageScreenPreview)

		# add screen label (sender, date)
		labelScreenPreviewText = "Unknown user"
		labelScreenPreview = QLabel()
		labelScreenPreview.setStyleSheet("QLabel { color: #FFF; }")
		if data_uuid in known_hosts.keys():
			labelScreenPreviewText = known_hosts[data_uuid]["username"]
		labelScreenPreviewText = "%s @ %s" % (labelScreenPreviewText, datetime.datetime.now().strftime("%H:%M"))
		labelScreenPreview.setText(labelScreenPreviewText)
		labelScreenPreview.setFont(QFont("Tahoma", 10))
		frameScreenPreview.layout().addWidget(labelScreenPreview)

		self.application.trayIcon.showMessage("QSH: Screenshot received", labelScreenPreviewText)

		# remove button
		buttonScreenPreviewRemove = QPushButton("remove")
		buttonScreenPreviewRemove.screen_preview_box = frameScreenPreview
		buttonScreenPreviewRemove.clicked.connect(self.screenPreviewRemoveClicked)
		buttonScreenPreviewRemove.setStyleSheet("""
		QPushButton {
			background-color: rgba(0, 0, 0, 50);
			border-bottom-left-radius: 5px;
			color: #fff;
			font-size: 10px;
			padding: 3px 4px;
		}
		QPushButton:hover {
			background-color: rgba(0, 0, 0, 150);
		}
		""")
		buttonScreenPreviewRemove.setParent(imageScreenPreview)
		buttonScreenPreviewRemove.show()
		buttonScreenPreviewRemove.move(imageScreenPreview.geometry().width() - buttonScreenPreviewRemove.geometry().width(), 0)

		self.layout().addWidget(frameScreenPreview)
		QtCore.QTimer.singleShot(0, self.updateWindowPositionAndSize)

		return 1

	def showWindow(self):
		self.show()
		self.raise_()
		self.activateWindow()
		QtCore.QTimer.singleShot(0, self.updateWindowPositionAndSize)

	def updateWindowPositionAndSize(self):
		self.resize(self.minimumSizeHint())
		iconCenter = self.application.trayIcon.icon.geometry().center()
		iconBottom = self.application.trayIcon.icon.geometry().bottomLeft()
		self.move(iconCenter.x() - self.width() / 2, iconBottom.y() + 0)

	def paintEvent(self, event):
		windowBrush = QBrush(QColor(0, 0, 0, 190))

		painter = QPainter(self)
		painter.setRenderHints(QPainter.Antialiasing, QPainter.HighQualityAntialiasing)

		windowShapePath = QPainterPath()
		windowShapePath.setFillRule(QtCore.Qt.WindingFill)
		# triangle
		triangleCenter = self.width() / 2
		windowShapePath.moveTo(triangleCenter - 6, 8)
		windowShapePath.lineTo(triangleCenter, 0)
		windowShapePath.lineTo(triangleCenter + 6, 8)
		windowShapePath.closeSubpath()
		# rounded window
		windowShapePath.addRoundedRect(0, 8, self.width(), self.height() - 8, 8.0, 8.0)

		painter.setClipPath(windowShapePath)
		painter.setBrush(windowBrush)
		painter.drawRect(-1, -1, self.width() + 2, self.height() + 2)

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
		self.application.trayIcon.incomingTotal -= 1
		self.application.trayIcon.updateMenu()
		if self.application.trayIcon.incomingTotal == 0:
			self.close()
		else:
			QtCore.QTimer.singleShot(0, self.showWindow)


class ScreenViewDialogEventFilter(QtCore.QObject):

	def eventFilter(self, obj, event):
		""" Popup window lost focus (need to close)
		"""
		try:
			assert isinstance(obj, ScreenViewDialog)
			if event.type() == QtCore.QEvent.WindowDeactivate and not self.parent().inFullScreenMode:
				self.parent().close()
		except AssertionError:
			pass
		return QtCore.QObject.eventFilter(self, obj, event)


class ScreenClickEventFilter(QtCore.QObject):

	def eventFilter(self, obj, event):
		""" Screenshot preview clicked
		"""
		parent = self.parent()
		try:
			assert isinstance(parent, ScreenViewDialog)
			if event.type() == QtCore.QEvent.MouseButtonPress:
				parent.inFullScreenMode = True
				parent.screenPreviewShow(obj)
				return True
			if event.type() == QtCore.QEvent.MouseButtonRelease:
				if hasattr(obj, "screen_preview_fs") and obj.screen_preview_fs:
					parent.inFullScreenMode = False
					try:
						QtCore.QTimer.singleShot(0, obj.screen_preview_fs.deleteLater)
					except RuntimeError:
						# screen preview already deleted
						pass
		except AssertionError:
			pass
		return QtCore.QObject.eventFilter(self, obj, event)
