from main import app
import sys
import os
from flask_migrate import Migrate,upgrade,migrate,init,revision
# from flask_script import Manager,Server
from model import *
mig = Migrate(app,db)
with app.app_context():
    if sys.argv[1] == "upgrade":
        upgrade()
        migrate()
    elif sys.argv[1] == "init":
        init()
    elif sys.argv[1] == "reinit":
        os.system("rm -r ./migrations")
        init()
    elif sys.argv[1] == "revision":
        revision()