from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, HiddenField, TextAreaField, FloatField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
import re
from movie.database import sql_translator


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], description='Username')
    password = PasswordField('Password', validators=[DataRequired()], description='Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], description='Username')
    password = PasswordField('Password', validators=[DataRequired()], description='Password')
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')], description='Confirm Password')
    name = StringField('Name', validators=[DataRequired()], description='Name')
    email = StringField('E-mail', validators=[Email()], description='E-mail')
    phone_number = IntegerField('Phone Number', description='Phone Number')
    submit = SubmitField('Register')

    def validate_username(self, username):
        from movie.models import User
        user = User().query_by_username(username.data)
        if user is not None:
            raise ValidationError('Please use a different username.')


class SearchBarForm(FlaskForm):
    choice = SelectField('Filter', choices=[('un-choose', ' -- Filter By -- '), ('year', 'Year'), ('genres', 'Genre'), ('content_rating', 'Content Rating')])
    year = SelectField('year', coerce=int, choices=[(0, '-- Year --')])
    genres = SelectField('genres', choices=[('None', '-- Genres --')])
    content_rating = SelectField('content_rating', choices=[('None', '-- Certificate --')])

    sort_by = SelectField('Sort By', choices=[('None', '-- Sort By --'), ('title', 'title'), ('year', 'year'), ('rating', 'rating'), ('price', 'price')])
    order = HiddenField('Order')
    search_term = StringField()

    submit = SubmitField()

    def init_options(self, range_sql):
        """Dynamically load filter options"""
        from movie.database import get_db
        conn, cur = get_db()

        # remove "order by ..." if exist
        order_filter_pattern = re.compile(r'order by .*')
        range_sql = order_filter_pattern.sub('', range_sql)

        cur.execute(sql_translator('select distinct year {} order by year desc').format(range_sql))
        years = cur.fetchall()
        self.year.choices.extend([(year[0], year[0]) for year in years])

        # join genres if not
        if 'join genres G' not in range_sql:
            idx = range_sql.index("where")
            range_sql = range_sql[:idx] + 'join genres G on M.movieID = G.movieID\n' + range_sql[idx:]
        cur.execute(sql_translator('select distinct genre {} order by genre').format(range_sql))
        genres = cur.fetchall()
        self.genres.choices.extend([(genre[0], genre[0]) for genre in genres])

        cur.execute(sql_translator('select distinct contentRating {} order by contentRating').format(range_sql))
        content_ratings = cur.fetchall()
        self.content_rating.choices.extend(
            [(content_rating[0], content_rating[0]) for content_rating in content_ratings])


class MovieDetailForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    summary = TextAreaField(validators=[DataRequired()])
    year = IntegerField(validators=[DataRequired()])
    content_rating = StringField(validators=[DataRequired()])
    rating = FloatField(validators=[DataRequired()])
    stock = IntegerField(validators=[DataRequired()])
    price = FloatField(validators=[DataRequired()])
    cost = FloatField(validators=[DataRequired()])
    imdb_id = StringField()
    genres = StringField()
    image = FileField()
    submit = SubmitField()
