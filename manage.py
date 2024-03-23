from main import app
from flask_migrate import Migrate
# from flask_script import Manager,Server
from model import *
migrate = Migrate(app,db)