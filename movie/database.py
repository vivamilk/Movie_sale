import os
import csv
import pymysql
import sqlite3
import click
import datetime
import random
from flask import current_app, g
from flask.cli import with_appcontext
from movie.utils import imdb_link_to_imdb_id, check_null, genres_to_list


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        if current_app.config['DATABASE_OPTION'] == 'MySQL':
            g.db = pymysql.connect(

            )
        elif current_app.config['DATABASE_OPTION'] == 'SQLite':
            g.db = sqlite3.connect(
                current_app.config['DATABASE_SQLITE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            # g.db.row_factory = sqlite3.Row
            g.db.execute('PRAGMA foreign_keys = ON')
        else:
            raise NotImplementedError
    return g.db, g.db.cursor()


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    if current_app.config['DATABASE_OPTION'] == 'MySQL':
        init_db()
    elif current_app.config['DATABASE_OPTION'] == 'SQLite':
        init_db_sqlite()
    else:
        raise NotImplementedError

    click.echo('Initialized the database.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def init_db():
    """Clear existing data and create new tables."""
    db, cur = get_db()

    with current_app.open_resource('schema.sql') as f:
        cur.executescript(f.read().decode('utf8'))


def init_db_sqlite():
    """Clear existing data and create new tables."""

    # delete db file if exist
    if os.path.isfile(current_app.config['DATABASE_SQLITE']):
        os.remove(current_app.config['DATABASE_SQLITE'])

    db, cur = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    # sample customer data
    cur.execute('insert into users values (?,?,?,?)',
                (1, 'test', 'pbkdf2:sha256:50000$Eh6bXq9p$f1d73e42b410a6ab463cc597ecaece0ed2de5253f9a87835416c732b0a74981e', False))
    cur.execute('insert into customer values (?,?,?,?,?)',
                (None, 1, 'brian', 'pittsburgh', '4121231234'))

    cur.execute('insert into users values (?,?,?,?)',
                (2, 'admin1', 'pbkdf2:sha256:50000$Eh6bXq9p$f1d73e42b410a6ab463cc597ecaece0ed2de5253f9a87835416c732b0a74981e', True))
    cur.execute('insert into manager values (?,?,?,?,?,?)',
                (None, 2, True, 'manager1', 'manager1@gamil.com', 6000))

    cur.execute('insert into users values (?,?,?,?)',
                (3, 'admin2', 'pbkdf2:sha256:50000$Eh6bXq9p$f1d73e42b410a6ab463cc597ecaece0ed2de5253f9a87835416c732b0a74981e', True))
    cur.execute('insert into manager values (?,?,?,?,?,?)',
                (None, 3, False, 'senior_manager1', 's_manager1@gamil.com', 9000))

    cur.execute('insert into store values (?,?,?)',
                (None, 'us_store@gmail.com', 'US'))
    cur.execute('insert into store values (?,?,?)',
                (None, 'uk_store@gmail.com', 'UK'))
    cur.execute('insert into management values (?,?)',
                (1, 1))

    # import data from csv
    base_path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(base_path, 'static/movie_metadata_original.csv'), encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for record in reader:
            movie_data = [
                record['Media ID'],
                record['Title'].replace('\n', ' '),
                record['Summary'].replace('\n', ' '),
                record['Year'],
                record['Content Rating'],
                record['Rating'],
                imdb_link_to_imdb_id(record['MetaDB Link']),
            ]
            genre_list = genres_to_list(record['Genres'])
            movie_data = check_null(movie_data)
            try:
                # movie
                cur.execute('insert into movie values (?,?,?,?,?,?,?)', movie_data)
                # genres
                for genre in genre_list:
                    cur.execute('insert into genres values (?,?)', (movie_data[0], genre))
                # stock
                for store_id in range(1, 3):
                    sale_price = random.randint(700, 1900)
                    cost = sale_price - random.randint(200, 500)
                    amount = random.randint(100, 300)
                    cur.execute('insert into stock values (?,?,?,?,?,?)',
                                (store_id, movie_data[0], amount, amount, sale_price/100, cost/100))
            except sqlite3.IntegrityError:
                print('IntegrityError: movieID {}'.format(movie_data[0]))

    # sample transactions
    dt = datetime.datetime.now() + datetime.timedelta(-100)
    cur.execute('insert into transactions values (?,?,?,?,?,?,?)',
                (None, 1, dt.strftime("%Y-%m-%d %H:%M:%S"), '89U78003ES8880109', 1, 4, 1))
    dt = datetime.datetime.now() + datetime.timedelta(-90)
    cur.execute('insert into transactions values (?,?,?,?,?,?,?)',
                (None, 2, dt.strftime("%Y-%m-%d %H:%M:%S"), '89U78003ES8880109', 1, 5, 1))
    dt = datetime.datetime.now() + datetime.timedelta(-80)
    cur.execute('insert into transactions values (?,?,?,?,?,?,?)',
                (None, 2, dt.strftime("%Y-%m-%d %H:%M:%S"), '45U78043ES4578010', 1, 6, 2))
    dt = datetime.datetime.now() + datetime.timedelta(-70)
    cur.execute('insert into transactions values (?,?,?,?,?,?,?)',
                (None, 1, dt.strftime("%Y-%m-%d %H:%M:%S"), '15U34504ES4546097', 1, 7, 2))
    db.commit()
    db.close()


if __name__ == '__main__':
    pass
