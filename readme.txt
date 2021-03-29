#Author Gowthamprakash Y


Attached script runs with Python 3.7

Requires below libraries:-
bottle - 0.12.17
gevent - 1.4.0
gevent-websocket - 0.10.1
simplejson - 3.16.0
sqlalchemy - 1.3.1

project directory contains:-
Coderepo- which has team wise code snippets
db- contain sqlite db file
templates- which holds all related js and html files
wsgidav - this is a python library which is deprecated and not available on pipy.org. So added from my local installations for use

dbcon.py - SQLalchamy database connection class for database sessions
index.py - works as server and takes CRUD RESTAPI calls
webdav.py - Call to import wsgidav library

Code was built using Pycharm IDE and runs locally through pycharm.

Not tested with any other platforms.
