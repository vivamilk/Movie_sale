import datetime


context_base = {'current_year': datetime.date.today().year}


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
