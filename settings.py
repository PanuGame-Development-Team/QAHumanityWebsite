import os
APP_NAME = "Humanity Website"
APP_VERSION = "1.1-240525-RC2"
TEACHERS = ["高宇","李红红","仇巧云"]
APP_SECRETKEY = "7B6X8SRPUVHCQCYXQS5BT7BK2DDVDVR16HXF1XMIMIQ24TX6B4KEZKUFCVSV3X4P"
APP_CONFIG = {"SQLALCHEMY_DATABASE_URI":"sqlite:///db.sqlite3",
              "SQLALCHEMY_TRACK_MODIFICATIONS":False}
DEBUG = False
HOST = "127.0.0.1"
PORT = 12472
mdmodules = ["markdown.extensions.extra","markdown.extensions.codehilite","markdown.extensions.tables","markdown.extensions.toc"]
mdconfigs = {}
ABDIR = os.path.dirname(__file__)