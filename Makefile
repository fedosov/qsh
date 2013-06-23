BASE = .

default: clean build

clean:
	rm -rf build dist

build:
	python setup-mac.py py2app

.phony: default