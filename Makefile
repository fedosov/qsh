BASE = .

default: clean build

clean:
	rm -rf build dist

build:
	python setup-mac.py py2app
	hdiutil create -srcfolder dist/qsh.app dist/qsh.dmg

.phony: default