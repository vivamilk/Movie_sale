from imdb import IMDb

imdb_database = IMDb(adultSearch=False)


def imdb_retrieve_movie_by_id(movie_id: str):
    movie = imdb_database.get_movie(movie_id)

    # item list
    genres = movie['genres']
    country = movie['countries']

    # single item
    title = movie['title']
    summary = movie['plot outline']
    year = movie['year']
    content_rating = find_US_certificate(movie['certificates'])
    rating = movie['rating']
    imdb_id = movie_id
    poster_url = movie['full-size cover url']
    return {

    }


def imdb_search_movie_by_name(movie_name: str, num_results=5):
    movie_list = imdb_database.search_movie(movie_name, results=num_results)
    return [(movie['title'], movie.movieID) for movie in movie_list]


# utility functions
def find_US_certificate(certificate_list: list):
    for certificate in certificate_list:
        if 'United States' in certificate:
            return certificate.split(':')[1]
    return None


if __name__ == '__main__':
    imdb_search_movie_by_name('star war')
    # imdb_retrieve_movie_by_id('0062622')
    print()
