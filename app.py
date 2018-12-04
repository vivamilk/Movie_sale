import random
import sqlite3
from flask import Flask, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, UserMixin
from config import Config
from form import LoginForm, RegistrationForm
from functools import wraps


app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


def roles_accepted(*roles):
    """Decorator which specifies that a user must have at least one of the
    specified roles. Example::
        @app.route('/create_post')
        @roles_accepted('editor', 'author')
        def create_post():
            return 'Create Post'
    The current user must have either the `editor` role or `author` role in
    order to view the page.
    :param args: The possible roles.
    """
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            elif current_user.type in roles:
                # TODO return to previous page if login but don't have role
                return login_manager.unauthorized()
            return func(*args, **kwargs)
        return decorated_view
    return wrapper


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html', home=True)


@app.route('/test')
@roles_accepted('senior_manager')
def test():
    return render_template('test.html')


@app.route('/shopping')
def get_shopping_data():
    movie = []
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('select movieID, title from movie limit 20')
        data = cur.fetchall()

    for select_data in data:
        movieID, title = select_data
        # TODO Here use random data / Join table to get data instead
        price = random.randint(3, 20)
        movie.append({'id': str(movieID), 'title': title, 'price': price})

    return render_template('shopping.html', images=movie, home=True)


@app.route('/manager')
@roles_accepted('manager', 'senior_manager')
def manage_data():
    # Here to fetch the data
    movie = []
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('select movieID, title from movie limit 20')
        data = cur.fetchall()

    for select_data in data:
        movieID, title = select_data
        # TODO Here use random data / Join table to get data instead
        stock = random.randint(10, 20)
        price = random.randint(3, 20)
        cost = price - random.randint(0, 3)
        movie.append({'id': str(movieID), 'name': title, 'price': price, 'cost': cost, 'inventory':stock})
    return render_template('admin.html', movies=movie, home=True)


@app.route('/list')
# TODO User Login -> List Movie / Admin Login -> Manger Movie
def list_movie():
    movie = []
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('select movieID, imdbID, title, year, rating from movie')
        data = cur.fetchall()
    for select_data in data:
        movieID, imdbID, title, year, rating = select_data
        # TODO Here use random data / Join table to get data instead
        stock = random.randint(4, 10)
        price = random.randint(3, 20)
        movie.append({'id': movieID, 'imdbid': imdbID, 'title': title, 'year': year,
                       'rating': rating, 'stock': stock, 'price': price})
    return render_template('list_metadata.html', movies=movie, home=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User().query_by_username(form.username.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        User().new_user(form.username.data, form.name.data, form.password.data, 'customer', form.email.data, form.phone_number.data)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# login utility functions
class User(UserMixin):

    def new_user(self, username, name, password, type, email=None, phone_numer=None, salary=None):
        self.username = username
        self.name = name
        self.password = generate_password_hash(password)
        self.type = type
        self.email = email
        self.phone_number = phone_numer
        self.salary = salary
        # connect to database
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('select max(userID) from users')
            current_max_id = cur.fetchone()[0]
            if current_max_id is not None:
                self.id = str(current_max_id + 1)
            else:
                self.id = str(1)
            try:
                if self.type == 'customer':
                    cur.execute('insert into users values (?,?,?)',
                                (self.id, self.username, self.password))
                    cur.execute('insert into customer values (?,?,?,?,?)',
                                (None, self.id, self.name, self.email, self.phone_number))
                else:
                    cur.execute('insert into users values (?,?,?)',
                                (self.id, self.username, self.password))
                    cur.execute('insert into manager values (?,?,?,?,?,?)',
                                (None, self.id, False, self.name, self.email, self.salary))
                conn.commit()
            except sqlite3.IntegrityError:
                flash("IntegrityError")
                conn.rollback()

    def query_by_id(self, user_id):
        # connect to database
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('select username, password, is_manager from users where userID=?', (user_id,))
            username, password, is_manager = cur.fetchone()
            if username is None:
                return None
            else:
                return self._get_user_info(user_id, username, password, is_manager)

    def query_by_username(self, username):
        # connect to database
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('select userID, password, is_manager from users where username=?', (username,))
            user_id, password, is_manager = cur.fetchone()
            if password is None:
                return None
            else:
                return self._get_user_info(user_id, username, password, is_manager)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def _get_user_info(self, user_id, username, password, is_manager):
        self.username = username
        self.password = password
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            if is_manager:
                cur.execute('select * from manager where userID=?', (user_id,))
                item = cur.fetchone()
                self.id = item[1]
                if item[2]:
                    self.type = 'senior_manager'
                else:
                    self.type = 'manager'
                self.name = item[3]
                self.email = item[4]
                self.salary = item[5]
            else:
                cur.execute('select * from customer where userID=?', (user_id,))
                item = cur.fetchone()
                self.id = item[1]
                self.name = item[2]
                self.type = 'customer'
                self.email = item[3]
                self.phone_number = item[4]
            return self


@login_manager.user_loader
def load_user(user_id):
    user = User()
    return user.query_by_id(user_id)


if __name__ == '__main__':
    app.run(debug=True)
