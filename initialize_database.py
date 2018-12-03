import sqlite3
import csv


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


if __name__ == '__main__':
    # connect to database
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # create tables
    cur.execute('''
    create table customer
    (
      customerID   INTEGER
        primary key,
      name         TEXT not null,
      address      TEXT,
      phoneNumber  NUMERIC,
      type         TEXT not null,
      loginName    TEXT unique not null,
      password     TEXT not null
    )
    ''')

    cur.execute('''
    create table manager
    (
      managerID INTEGER
        primary key,
      type      TEXT not null,
      loginName TEXT unique not null,
      password  TEXT not null,
      name      TEXT not null,
      address   TEXT,
      salary    NUMERIC
    )
    ''')

    cur.execute('''
    create table movie
    (
      movieID       INTEGER
        primary key,
      title         TEXT not null,
      summary       TEXT not null,
      year          INTEGER not null,
      country       TEXT not null,
      contentRating TEXT not null,
      rating        INTEGER not null,
      genres        TEXT not null,
      imdbID        TEXT unique not null
    )
    ''')

    cur.execute('''
    create table stock
    (
      storeID     INTEGER,
      movieID     INTEGER,
      stockAmount INTEGER not null,
      price       NUMERIC not null,
      primary key (storeID, movieID)
    )
    ''')

    cur.execute('''
    create table store
    (
      storeID     INTEGER
        primary key,
      address     TEXT not null
    )
    ''')

    cur.execute('''
    create table manage
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
        primary key,
      orderAmount  INTEGER not null,
      purchaseDate TEXT not null,
      customerID   INTEGER not null
        references customer,
      movieID      INTEGER not null
        references movie,
      storeID      INTEGER not null
        references store
    )
    ''')

    # import data from csv
    with open('static/movie_metadata_original.csv', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for record in reader:
            movie_data = [
                record['Media ID'],
                record['Title'],
                record['Summary'],
                record['Year'],
                record['Country'],
                record['Content Rating'],
                record['Rating'],
                record['Genres'],
                imdb_link_to_imdb_id(record['MetaDB Link']),
            ]
            movie_data = check_null(movie_data)
            try:
                cur.execute('insert into movie values (?,?,?,?,?,?,?,?,?)', movie_data)
            except sqlite3.IntegrityError:
                print('IntegrityError: movieID {}'.format(movie_data[0]))

    conn.commit()
    conn.close()
