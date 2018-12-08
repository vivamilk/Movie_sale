import os


DEBUG = True
SECRET_KEY = "SECRET"

# SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
# SQLALCHEMY_TRACK_MODIFICATIONS = False

DATABASE_OPTION = 'SQLite'
DATABASE_SQLITE = os.path.abspath(os.path.dirname(__file__)) + '/database.db'
