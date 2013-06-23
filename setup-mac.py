# -*- coding: utf-8 -*-

from setuptools import setup

setup(
	app=["app.py"],
    name="qsh",
	options=\
	{
		"py2app":
		{
			"argv_emulation": True,
			"includes": ["PySide"],
		    "plist":
			{
				"CFBundleIdentifier": "org.qsh",
			    "CFBundleShortVersionString": "0.1.0",
			    "LSUIElement": True
		    }
		}
	},
    data_files=["resources"],
	setup_requires=["py2app"]
)