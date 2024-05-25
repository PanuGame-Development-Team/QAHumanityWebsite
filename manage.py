from main import app
from flask_migrate import Migrate,upgrade,migrate
# from flask_script import Manager,Server
from model import *
mig = Migrate(app,db)
with app.app_context():
    upgrade()
    migrate()