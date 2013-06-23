# Quick Screen Share (QSH)

### Screen sharing over the network in a single click.

> "Hey, quick, come here, look at what's on my screen!" — never again.

![](http://i.imgur.com/HR6okiQ.png)

You can:

* show buggy HTML page to your teammate;
* blazingly fast send on screen photos;
* ask what is going on in a certain code, giving context at the speed of light.

## Screenshots

![](http://i.imgur.com/cwK5Rtu.png)

## Download

### [QSH for OS X](https://dl.dropboxusercontent.com/u/26256/qsh/qsh.app.tgz)

## Setup

### Environment

```
$ brew install qt pyside
$ cp -r /usr/local/lib/python2.7/site-packages/PySide env/lib/python2.7/site-packages/
```

### Slow connection test

```
$ sudo ipfw add pipe 1 all from any to any && sudo ipfw pipe 1 config bw 512Kbit/s delay 50ms
...
$ sudo ipfw flush
```

## OS X Build

```
$ pip install py2app
$ make
```

## Authors

**Mikhail Fedosov**

+ [http://github.com/fedosov](http://github.com/fedosov)

## License

> Copyright © 2012 Fedosov Mikhail (tbs.micle@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions 
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED 
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
IN THE SOFTWARE.