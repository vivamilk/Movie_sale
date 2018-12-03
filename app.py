from flask import Flask, render_template, redirect, url_for, request, flash
from form import LoginForm, Register
from config import Config
import sqlite3
import hashlib


app = Flask(__name__)
app.config.from_object(Config)

# connect to database
conn = sqlite3.connect('database.db')
cur = conn.cursor()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/index')
def index():
    return render_template('index.html', home=True)


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    # check user conflicts
    try:
        cur.execute('insert into customer (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city,
             state, country, phone))
        conn.commit()
        msg = "Registered Successfully"
    except sqlite3.IntegrityError:
        conn.rollback()
        msg = "User existed, please try another username"

    return render_template('register.html', form=form, error=msg)


def is_user_valid(form: LoginForm):
    cur.execute('SELECT loginName, password FROM customer')
    data = cur.fetchall()
    for (longin_name, password) in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True


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
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    '''
        error = None
        if request.method == 'POST':
            # Check the admin data
            if request.form['username'] != 'admin' or request.form['password'] != 'admin':
                error = 'Invalid Credentials. Please try again.'
            else:
                return redirect(url_for('index'))
        return render_template('login.html', error=error)
    '''
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run()
