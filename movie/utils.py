import datetime
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from movie import login_manager


context_base = {'current_year': datetime.date.today().year}


def roles_accepted(*roles):
    """Decorator which specifies that a user must have at least one of the
    specified roles. Example::
        @app.route('/create_post')
        @roles_accepted('editor', 'author')
        def create_post():
            return 'Create Post'
    The current user must have either the `editor` role or `author` role in
    order to view the page.
    :param roles: The possible roles.
    """

    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            elif current_user.type not in roles:
                flash("Sorry, You do not have the permission to view this page. Return to homepage.")
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return decorated_view
    return wrapper


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
