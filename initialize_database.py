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
      name         VARCHAR(20) not null,
      emailAddress VARCHAR(30),
      phoneNumber  INTEGER(16),
      username     VARCHAR(20) unique not null,
      password     VARCHAR(100) not null
    )
    ''')

    cur.execute('''
    create table manager
    (
      managerID INTEGER
        primary key autoincrement,
      managerLevel      BOOLEAN not null,
      username  VARCHAR(20) unique not null,
      password  VARCHAR(100) not null,
      name      VARCHAR(20) not null,
      emailAddress   VARCHAR(30),
      salary    NUMERIC
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

    # sample customer data
    cur.execute('insert into customer values (?,?,?,?,?,?)',
                (None,	'brian', 'pittsburgh', '4121231234', 'test', 'pbkdf2:sha256:50000$Eh6bXq9p$f1d73e42b410a6ab463cc597ecaece0ed2de5253f9a87835416c732b0a74981e'))
    cur.execute('insert into main.manager values (?,?,?,?,?,?,?)',
                (None, True, 'admin1', 'pbkdf2:sha256:50000$Eh6bXq9p$f1d73e42b410a6ab463cc597ecaece0ed2de5253f9a87835416c732b0a74981e', 'manager1', 'manager1@gamil.com', 6000))
    cur.execute('insert into main.manager values (?,?,?,?,?,?,?)',
                (None, False, 'admin2',
                 'pbkdf2:sha256:50000$Eh6bXq9p$f1d73e42b410a6ab463cc597ecaece0ed2de5253f9a87835416c732b0a74981e',
                 'senior_manager1', 's_manager1@gamil.com', 9000))
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
                record['Title'],
                record['Summary'],
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
                    sale_price = random.uniform(7, 19)
                    cost = sale_price - random.uniform(1, 5)
                    cur.execute('insert into stock values (?,?,?,?,?)',
                                (store_id, movie_data[0], random.randint(100, 300), sale_price, cost))
            except sqlite3.IntegrityError:
                print('IntegrityError: movieID {}'.format(movie_data[0]))

    # sample transactions
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute('insert into transactions values (?,?,?,?,?,?)',
                (None, 1, dt, 1, 4, 1))
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute('insert into transactions values (?,?,?,?,?,?)',
                (None, 2, dt, 1, 5, 1))
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute('insert into transactions values (?,?,?,?,?,?)',
                (None, 2, dt, 1, 6, 2))
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute('insert into transactions values (?,?,?,?,?,?)',
                (None, 1, dt, 1, 7, 2))
    conn.commit()
    conn.close()
