# -*- coding: utf-8 -*-
__author__ = "Mikhail Fedosov <tbs.micle@gmail.com>"

import gntp.notifier

growl = gntp.notifier.GrowlNotifier(
	applicationName="QSH",
	notifications=["Incoming screenshots"],
	defaultNotifications=["Incoming screenshots"],
)
growl.register()
