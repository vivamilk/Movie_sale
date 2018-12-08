from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from movie.database import get_db
from movie import login_manager


@login_manager.user_loader
def load_user(user_id):
    user = User()
    return user.query_by_id(user_id)


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
        db, cur = get_db()
        cur.execute('select max(userID) from users')
        current_max_id = cur.fetchone()[0]
        if current_max_id is not None:
            self.id = str(current_max_id + 1)
        else:
            self.id = str(1)

        if self.type == 'customer':
            cur.execute('insert into users values (?,?,?,?)',
                        (self.id, self.username, self.password, False))
            cur.execute('insert into customer values (?,?,?,?,?)',
                        (None, self.id, self.name, self.email, self.phone_number))
        else:
            cur.execute('insert into users values (?,?,?,?)',
                        (self.id, self.username, self.password, True))
            cur.execute('insert into manager values (?,?,?,?,?,?)',
                        (None, self.id, False, self.name, self.email, self.salary))
        cur.commit()

    def query_by_id(self, user_id):
        # connect to database
        db, cur = get_db()
        cur.execute('select username, password, is_manager from users where userID=?', (user_id,))
        result = cur.fetchone()
        if result is None:
            return None
        else:
            return self._get_user_info(user_id, result[0], result[1], result[2])

    def query_by_username(self, username):
        # connect to database
        db, cur = get_db()
        cur.execute('select userID, password, is_manager from users where username=?', (username,))
        result = cur.fetchone()
        if result is None:
            return None
        else:
            return self._get_user_info(result[0], username, result[1], result[2])

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def _get_user_info(self, user_id, username, password, is_manager):
        self.username = username
        self.password = password
        if is_manager:
            # connect to database
            db, cur = get_db()
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
            # connect to database
            db, cur = get_db()
            cur.execute('select * from customer where userID=?', (user_id,))
            item = cur.fetchone()
            self.id = item[1]
            self.name = item[2]
            self.type = 'customer'
            self.email = item[3]
            self.phone_number = item[4]
        return self
