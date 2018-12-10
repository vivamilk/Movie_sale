import os


# DEBUG = True
SECRET_KEY = "SECRET"

# SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
# SQLALCHEMY_TRACK_MODIFICATIONS = False

DATABASE_SQLITE = os.path.abspath(os.path.dirname(__file__)) + '/database.db'


# choose whether to use MySQL or SQLite
# DATABASE_OPTION = 'SQLite'
DATABASE_OPTION = 'MySQL'

# please change to your MySQL configuration here
DATABASE_MYSQL_CONFIG = {
    'host': "127.0.0.1",
    'user': "luozm",
    'password': "luo123123",
    'database': "web_movie"
}
