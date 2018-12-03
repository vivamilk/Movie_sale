import sqlite3
from flask import Flask, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, UserMixin
from config import Config
from form import LoginForm, RegistrationForm


app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = 'index'


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html', home=True)


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/shopping')
def get_shopping_data():
    image = [
        {
            'id': '3'
        },
        {
            'id': '4'
        },
        {
            'id': '6'
        }
    ]
    return render_template('shopping.html', images=image)


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
        User().new_user(form.username.data, form.name.data, form.password.data, form.type.data, form.address.data, form.phone_number.data)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# login utility functions
class User(UserMixin):

    def new_user(self, username, name, password, type, address=None, phone_numer=None):
        self.username = username
        self.name = name
        self.password = generate_password_hash(password)
        self.type = type
        self.address = address
        self.phone_number = phone_numer
        # connect to database
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('select max(customerID) from customer')
            current_max_id = cur.fetchone()[0]
            if current_max_id is not None:
                self.id = str(current_max_id + 1)
            else:
                self.id = str(1)
            try:
                cur.execute('insert into customer values (?,?,?,?,?,?,?)',
                            (self.id, self.name, self.address, self.phone_number, self.type, self.username, self.password))
                conn.commit()
            except sqlite3.IntegrityError:
                flash("IntegrityError")
                conn.rollback()

    def query_by_id(self, user_id):
        # connect to database
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('select * from customer where customerID=?', (int(user_id),))
            item = cur.fetchone()
            if item is None:
                return None
            else:
                self.id = str(user_id)
                self.username = item[5]
                self.name = item[1]
                self.password = item[6]
                self.type = item[4]
                self.address = item[2]
                self.phone_number = item[3]
                return self

    def query_by_username(self, username):
        # connect to database
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('select * from customer where loginName=?', (username,))
            item = cur.fetchone()
            if item is None:
                return None
            else:
                self.id = item[0]
                self.username = username
                self.name = item[1]
                self.password = item[6]
                self.type = item[4]
                self.address = item[2]
                self.phone_number = item[3]
                return self

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login_manager.user_loader
def load_user(user_id):
    user = User()
    return user.query_by_id(user_id)


if __name__ == '__main__':
    app.run()
