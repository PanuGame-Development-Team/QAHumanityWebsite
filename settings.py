import os
APP_NAME = "Humanity Website"
APP_VERSION = "1.2-240602-stable-rev1"
TEACHERS = ["高宇","李红红","仇巧云","吴尚卿"]
APP_SECRETKEY = "7B6X8SRPUVHCQCYXQS5BT7BK2DDVDVR16HXF1XMIMIQ24TX6B4KEZKUFCVSV3X4P"
APP_CONFIG = {"SQLALCHEMY_DATABASE_URI":"sqlite:///db.sqlite3",
              "SQLALCHEMY_TRACK_MODIFICATIONS":False}
DEBUG = False
HOST = "127.0.0.1"
PORT = 12472
mdmodules = ["markdown.extensions.extra","markdown.extensions.codehilite","markdown.extensions.tables","markdown.extensions.toc"]
mdconfigs = {}
ABDIR = os.path.dirname(__file__)
DANGERARGS = ["onclick","oncontextmenu","ondblclick","onmousedown","onmouseenter","onmouseleave","onmousemove","onmouseover","onmouseout","onmouseup","onkeydown","onkeypress","onkeyup","onabort","onbeforeunload","onerror","onhashchange","onload","onpageshow","onpagehide","onresize","onscroll","onunload","onblur","onchange","onfocus","onfocusin","onfocusout","oninput","onreset","onsearch","onselect","onsubmit","oncopy","oncut","onpaste","onafterprint","onbeforeprint","ondrag","ondragend","ondragenter","ondragleave","ondragover","ondragstart","ondrop","onabort","oncanplay","oncanplaythrough","ondurationchange","onemptied","onended","onerror","onloadeddata","onloadedmetadata","onloadstart","onpause","onplay","onplaying","onprogress","onratechange","onseeked","onseeking","onstalled","onsuspend","ontimeupdate","onvolumechange","onwaiting","animationend","animationiteration","animationstart","transitionend","onmessage","onmousewheel","ononline","onoffline","onpopstate","onshow","onstorage","ontoggle","onwheel","visibilitychange"]