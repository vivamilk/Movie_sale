from flask import Flask
from flask_login import LoginManager
# from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config')
# db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


from movie import views, models, database, api
database.init_app(app)
