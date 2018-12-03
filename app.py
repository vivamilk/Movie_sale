from flask import Flask, render_template, redirect, url_for, request, flash
from form import LoginForm, Register
from config import Config
import sqlite3


app = Flask(__name__)
app.config.from_object(Config)

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
    return render_template('register.html', form=form)


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
