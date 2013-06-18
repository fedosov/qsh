# -*- coding: utf-8 -*-

from setuptools import setup

setup(
	app=["app.py"],
	options=\
	{
		"py2app":
		{
			"argv_emulation": True,
			"includes": ["PySide"],
		    "plist":
			{
				"CFBundleIdentifier": "org.qsh",
			    "LSUIElement": True
		    }
		}
	},
    data_files=["resources"],
	setup_requires=["py2app"]
)