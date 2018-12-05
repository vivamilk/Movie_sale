import sqlite3
import csv
import random
import datetime


def imdb_link_to_imdb_id(link: str):
    return link.split('/')[-1][2:]


def imdb_id_to_imdb_link(imdb_id: str):
    prefix = 'http://www.imdb.com/title/tt'
    return prefix + imdb_id


def check_null(movie_data: list):
    temp_data = []
    for value in movie_data:
        if value == 'N/A':
            temp_data.append(None)
        else:
            temp_data.append(value)
    return temp_data


def genres_to_list(genres: str):
    return genres.replace('\n', ' ').split(" - ")


if __name__ == '__main__':
    # connect to database
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # create tables
    cur.execute('''
    create table customer
    (
      customerID   INTEGER
        primary key autoincrement,
      userID       INTEGER
        references users,
      name         VARCHAR(20) not null,
      emailAddress VARCHAR(30),
      phoneNumber  INTEGER(16)
    )
    ''')

    cur.execute('''
    create table manager
    (
      managerID     INTEGER
        primary key autoincrement,
      userID        INTEGER
        references users,
      managerLevel  BOOLEAN not null,
      name          VARCHAR(20) not null,
      emailAddress  VARCHAR(30),
      salary        NUMERIC
    )
    ''')

    cur.execute('''
    create table movie
    (
      movieID       INTEGER
        primary key autoincrement,
      title         VARCHAR(30) not null,
      summary       VARCHAR(1000) not null,
      year          INTEGER(4) not null,
      contentRating VARCHAR(10) not null,
      rating        NUMERIC not null,
      imdbID        VARCHAR(10) unique not null
    )
    ''')

    cur.execute('''
    create table genres
    (
      movieID INTEGER
        references movie,
      genre   VARCHAR(20) not null
    )
    ''')

    cur.execute('''
    create table stock
    (
      storeID     INTEGER
        references store,
      movieID     INTEGER
        references movie,
      stockAmount INTEGER(10) not null,
      salePrice   NUMERIC not null,
      cost        NUMERIC not null,
      primary key (storeID, movieID)
    )
    ''')

    cur.execute('''
    create table store
    (
      storeID        INTEGER
        primary key autoincrement,
      emailAddress   VARCHAR(30) not null,
      region         VARCHAR(30)not null
    )
    ''')

    cur.execute('''
    create table management
    (
      managerID INTEGER
        references manager,
      storeID   INTEGER
        references store,
      primary key (storeID, managerID)
    )
    ''')

    cur.execute('''
    create table transactions
    (
      purchaseID   INTEGER
        primary key autoincrement,
      orderAmount  INTEGER(10) not null,
      purchaseDate datetime not null,
      customerID   INTEGER
        references customer,
      movieID      INTEGER
        references movie,
      storeID      INTEGER
        references store
    )
    ''')

    cur.execute('''
    create table users
    (
      userID      INTEGER
        primary key,
      username    VARCHAR(20) unique not null,
      password    VARCHAR(100) not null,
      is_manager  BOOLEAN
    )
    ''')

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
    with open('static/movie_metadata_original.csv', encoding='utf-8') as file:
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
                    cur.execute('insert into stock values (?,?,?,?,?)',
                                (store_id, movie_data[0], random.randint(100, 300), sale_price/100, cost/100))
            except sqlite3.IntegrityError:
                print('IntegrityError: movieID {}'.format(movie_data[0]))

    # sample transactions
    dt = datetime.datetime.now() + datetime.timedelta(-100)
    cur.execute('insert into transactions values (?,?,?,?,?,?)',
                (None, 1, dt.strftime("%Y-%m-%d %H:%M:%S"), 1, 4, 1))
    dt = datetime.datetime.now() + datetime.timedelta(-90)
    cur.execute('insert into transactions values (?,?,?,?,?,?)',
                (None, 2, dt.strftime("%Y-%m-%d %H:%M:%S"), 1, 5, 1))
    dt = datetime.datetime.now() + datetime.timedelta(-80)
    cur.execute('insert into transactions values (?,?,?,?,?,?)',
                (None, 2, dt.strftime("%Y-%m-%d %H:%M:%S"), 1, 6, 2))
    dt = datetime.datetime.now() + datetime.timedelta(-70)
    cur.execute('insert into transactions values (?,?,?,?,?,?)',
                (None, 1, dt.strftime("%Y-%m-%d %H:%M:%S"), 1, 7, 2))
    conn.commit()
    conn.close()
