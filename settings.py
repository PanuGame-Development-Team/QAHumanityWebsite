APP_NAME = "Humanity Website"
APP_VERSION = "1.0-240323-RC3-repack1"
TEACHERS = ["高宇","李红红","仇巧云"]
APP_SECRETKEY = "7B6X8SRPUVHCQCYXQS5BT7BK2DDVDVR16HXF1XMIMIQ24TX6B4KEZKUFCVSV3X4P"
APP_CONFIG = {"SQLALCHEMY_DATABASE_URI":"sqlite:///db.sqlite3",
              "SQLALCHEMY_TRACK_MODIFICATIONS":False}
DEBUG = True
HOST = "127.0.0.1"
PORT = 12472
mdmodules = ["markdown.extensions.extra","markdown.extensions.codehilite","markdown.extensions.tables","markdown.extensions.toc"]
mdconfigs = {}