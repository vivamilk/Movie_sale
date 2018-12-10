import os
import csv
from mysql import connector
import sqlite3
import click
import datetime
import random
from os import system
from flask import current_app, g
from flask.cli import with_appcontext
from movie.utils import imdb_link_to_imdb_id, check_null, genres_to_list


def setup_sql_placeholder():
    db_option = current_app.config['DATABASE_OPTION']
    if db_option == 'MySQL':
        paramstyle = connector.paramstyle
    elif db_option == 'SQLite':
        paramstyle = sqlite3.paramstyle
    else:
        raise NotImplementedError

    if paramstyle == 'qmark':
        placeholder = "?"
    elif paramstyle == 'pyformat':
        placeholder = "%s"
    else:
        raise Exception("Unexpected paramstyle: %s" % paramstyle)
    return placeholder


def sql_translator(sql_query: str, ph_from="?"):
    """Translate placeholder in SQL query if the format is wrong"""
    placeholder = g.placeholder
    if placeholder in sql_query:
        return sql_query
    else:
        return sql_query.replace(ph_from, placeholder)


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        if current_app.config['DATABASE_OPTION'] == 'MySQL':
            from config import DATABASE_MYSQL_CONFIG
            g.db = connector.connect(**DATABASE_MYSQL_CONFIG)
        elif current_app.config['DATABASE_OPTION'] == 'SQLite':
            g.db = sqlite3.connect(
                current_app.config['DATABASE_SQLITE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            # g.db.row_factory = sqlite3.Row
            g.db.execute('PRAGMA foreign_keys = ON')
        else:
            raise NotImplementedError
        g.placeholder = setup_sql_placeholder()

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

    command = """mysql -u %s -p"%s" --host %s --port %s %s < %s""" % ("luozm", "luo123123", "localhost", 3306, "web_movie", 'movie/mysql_schema.sql')
    system(command)
    conn, cur = get_db()

    init_sample_data(conn, cur)


def init_db_sqlite():
    """Clear existing data and create new tables."""

    # delete db file if exist
    if os.path.isfile(current_app.config['DATABASE_SQLITE']):
        os.remove(current_app.config['DATABASE_SQLITE'])

    conn, cur = get_db()
    with current_app.open_resource('schema.sql') as f:
        conn.executescript(f.read().decode('utf8'))

    init_sample_data(conn, cur)


def init_sample_data(conn, cur):

    # sample customer data
    cur.execute(sql_translator('insert into users values (?,?,?,?)'),
                (1, 'test', 'pbkdf2:sha256:50000$Eh6bXq9p$f1d73e42b410a6ab463cc597ecaece0ed2de5253f9a87835416c732b0a74981e', False))
    cur.execute(sql_translator('insert into customer values (?,?,?,?,?)'),
                (None, 1, 'brian', 'pittsburgh', '4121231234'))

    cur.execute(sql_translator('insert into users values (?,?,?,?)'),
                (2, 'admin1', 'pbkdf2:sha256:50000$Eh6bXq9p$f1d73e42b410a6ab463cc597ecaece0ed2de5253f9a87835416c732b0a74981e', True))
    cur.execute(sql_translator('insert into manager values (?,?,?,?,?,?)'),
                (None, 2, False, 'manager1', 'manager1@gamil.com', 6000))

    cur.execute(sql_translator('insert into users values (?,?,?,?)'),
                (3, 'admin2', 'pbkdf2:sha256:50000$Eh6bXq9p$f1d73e42b410a6ab463cc597ecaece0ed2de5253f9a87835416c732b0a74981e', True))
    cur.execute(sql_translator('insert into manager values (?,?,?,?,?,?)'),
                (None, 3, True, 'senior_manager1', 's_manager1@gamil.com', 9000))

    cur.execute(sql_translator('insert into store values (?,?,?)'),
                (None, 'pa_us_store@gmail.com', 'PA, US'))
    cur.execute(sql_translator('insert into store values (?,?,?)'),
                (None, 'ca_us_store@gmail.com', 'CA, US'))
    cur.execute(sql_translator('insert into management values (?,?)'),
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
                cur.execute(sql_translator('insert into movie values (?,?,?,?,?,?,?)'), movie_data)
                # genres
                for genre in genre_list:
                    cur.execute(sql_translator('insert into genres values (?,?)'), (movie_data[0], genre))
                # stock
                for store_id in range(1, 3):
                    sale_price = random.randint(700, 1900)
                    cost = sale_price - random.randint(200, 500)
                    amount = random.randint(100, 300)
                    cur.execute(sql_translator('insert into stock values (?,?,?,?,?,?)'),
                                (store_id, movie_data[0], amount, amount, sale_price/100, cost/100))
            except sqlite3.IntegrityError:
                print('IntegrityError: movieID {}'.format(movie_data[0]))
            except connector.errors.IntegrityError:
                print('IntegrityError: movieID {}'.format(movie_data[0]))
            except connector.errors.DataError:
                print(movie_data)

    # sample transactions
    dt = datetime.datetime.now() + datetime.timedelta(-100)
    cur.execute(sql_translator('insert into transaction_info values (?,?,?,?,?,?,?)'),
                ('89U78003ES8880109', dt.strftime("%Y-%m-%d %H:%M:%S"), 1, 1, 36.77, 'test buyer\n1 Main St\nSan Jose\nCA, 95131, US', 2))
    cur.execute(sql_translator('insert into transaction_detail values (?,?,?,?)'),
                ('89U78003ES8880109', 5, 1, 18.06))
    cur.execute(sql_translator('insert into transaction_detail values (?,?,?,?)'),
                ('89U78003ES8880109', 6, 1, 16.31))

    dt = datetime.datetime.now() + datetime.timedelta(-20)
    cur.execute(sql_translator('insert into transaction_info values (?,?,?,?,?,?,?)'),
                ('6E178263NT5976051', dt.strftime("%Y-%m-%d %H:%M:%S"), 1, 2, 82.22, 'test buyer\n1 Main St\nSan Jose\nCA, 95131, US', 1))
    cur.execute(sql_translator('insert into transaction_detail values (?,?,?,?)'),
                ('6E178263NT5976051', 4, 1, 15.99))
    cur.execute(sql_translator('insert into transaction_detail values (?,?,?,?)'),
                ('6E178263NT5976051', 5, 1, 18.06))
    cur.execute(sql_translator('insert into transaction_detail values (?,?,?,?)'),
                ('6E178263NT5976051', 6, 1, 16.31))
    cur.execute(sql_translator('insert into transaction_detail values (?,?,?,?)'),
                ('6E178263NT5976051', 10, 1, 14.81))
    cur.execute(sql_translator('insert into transaction_detail values (?,?,?,?)'),
                ('6E178263NT5976051', 14, 1, 11.67))

    dt = datetime.datetime.now() + datetime.timedelta(-1)
    cur.execute(sql_translator('insert into transaction_info values (?,?,?,?,?,?,?)'),
                ('4XX45928SF3991535', dt.strftime("%Y-%m-%d %H:%M:%S"), 1, 1, 7.80, 'test buyer\n1 Main St\nSan Jose\nCA, 95131, US', 0))
    cur.execute(sql_translator('insert into transaction_detail values (?,?,?,?)'),
                ('4XX45928SF3991535', 5136, 1, 7.29))

    conn.commit()


if __name__ == '__main__':
    pass
