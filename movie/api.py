import datetime
import requests
from copy import copy
from flask import redirect, url_for, flash, jsonify, request, session
from flask_login import current_user

from movie import app
from movie.utils import context_base
from movie.database import get_db


# -----------------------------------
# utility functions
# -----------------------------------

def get_movies_with_params(movie_columns):
    """
    Get list of movie data from database given the parameters.
    :param movie_columns: which columns are needed (a string)
    :return:
    """
    # get keywords
    search_term = request.args.get('search_term')
    sort_by = request.args.get('sort_by')
    is_descent = request.args.get('order') == 'True'
    store_id = int(session['store_id'])

    if is_descent:
        ordered = 'DESC'
    else:
        ordered = ''
    if not search_term:
        search_term = ""
        search_sql = ""
    else:
        search_sql = "and title like '%{}%' ".format(search_term)
    if sort_by == 'price':
        sort_sql = "order by S.salePrice {}".format(ordered)
    elif sort_by:
        sort_sql = "order by M.{} {}".format(sort_by, ordered)
    else:
        sort_sql = ""

    # select movies from db
    conn, cur = get_db()
    cur = conn.cursor()
    cur.execute('''
    select {}
    from movie M
    join stock S
    where M.movieID=S.movieID {}and S.storeID={}
    {}
    '''.format(movie_columns, search_sql, store_id, sort_sql))
    data = cur.fetchall()

    # store info
    cur.execute('select storeID, region from store')
    store_data = cur.fetchall()
    stores = []
    for store in store_data:
        stores.append({'id': str(store[0]), 'name': store[1]})

    content = copy(context_base)
    content['order'] = not is_descent
    content['sort_by'] = sort_by
    content['search_term'] = search_term
    content['search_bar'] = True
    content['stores'] = stores
    return data, content


@app.route('/store_id_listener', methods=["POST"])
def store_id_listener():
    response = request.get_json()
    if 'store_id' not in response:
        return redirect(url_for('index'))
    else:
        session['store_id'] = str(response['store_id'])
        return jsonify(session['store_id'])


# -----------------------------------
# Shopping Cart Operations
# -----------------------------------

def get_items():
    """Inner function to get items in cart."""
    store_id = int(session['store_id'])
    conn, cur = get_db()

    cur.execute('select customerID from customer where userID=?', (current_user.id,))
    customer_id = cur.fetchone()[0]

    # get items in the cart with their price
    cur.execute('''
        select Shop.amount, Shop.movieID, M.title, S.salePrice
        from shopping_cart Shop
        join stock S on Shop.movieID=S.movieID and Shop.storeID=S.storeID
        join movie M on S.movieID = M.movieID
        where customerID=? and Shop.storeID=?
        ''', (customer_id, store_id))
    records = cur.fetchall()
    return records


@app.route('/shopping/get_items', methods=['POST'])
def get_items_in_cart():
    records = get_items()
    json_data = []
    for record in records:
        json_data.append({'amount': record[0], 'movieID': record[1], 'title': record[2], 'price': record[3]})
    return jsonify(json_data)


@app.route('/shopping/remove_items', methods=['POST'])
def remove_items_in_cart():
    store_id = int(session['store_id'])
    conn, cur = get_db()

    cur.execute('select customerID from customer where userID=?', (current_user.id,))
    customer_id = cur.fetchone()[0]

    # get items in the cart
    cur.execute('select amount, movieID from shopping_cart where customerID=? and storeID=?', (customer_id, store_id))
    records = cur.fetchall()

    # remove records from database.shopping_cart
    cur.execute('delete from shopping_cart where customerID=? and storeID=?', (customer_id, store_id))

    # update database.stock
    for amount, movie_id in records:
        cur.execute('select amountTemp from stock where movieID=? and storeID=?', (movie_id, store_id))
        temp_amount_all = cur.fetchone()[0]
        cur.execute('update stock set amountTemp=? where movieID=? and storeID=?',
                    (temp_amount_all + amount, movie_id, store_id))
    conn.commit()
    return jsonify({"operation": "remove all items"})


@app.route('/shopping/<int:movie_id>', methods=['POST'])
def add_item_to_cart(movie_id):
    amount = 1
    store_id = int(session['store_id'])
    conn, cur = get_db()

    cur.execute('select customerID from customer where userID=?', (current_user.id,))
    customer_id = cur.fetchone()[0]

    cur.execute('select amount from shopping_cart where customerID=? and movieID=? and storeID=?',
                (customer_id, movie_id, store_id))
    current_amount = cur.fetchone()

    # insert or update record into database.shopping_cart
    if current_amount is None:
        cur.execute('insert into shopping_cart values (?,?,?,?)',
                    (amount, customer_id, movie_id, store_id))
    else:
        cur.execute('update shopping_cart set amount=? where customerID=? and movieID=? and storeID=?',
                    (current_amount[0] + amount, customer_id, movie_id, store_id))

    # update amountTemp in database.stock
    cur.execute('select amountTemp from stock where movieID=? and storeID=?', (movie_id, store_id))
    temp_amount_all = cur.fetchone()[0]
    cur.execute('update stock set amountTemp=? where movieID=? and storeID=?',
                (temp_amount_all - amount, movie_id, store_id))

    conn.commit()
    return jsonify({"operation": "add item", "movieID": movie_id, "amount": amount})


@app.route('/shopping/remove/<int:movie_id>', methods=['POST'])
def remove_item_in_cart(movie_id):
    amount = -1
    store_id = int(session['store_id'])
    conn, cur = get_db()

    cur.execute('select customerID from customer where userID=?', (current_user.id,))
    customer_id = cur.fetchone()[0]

    cur.execute('select amount from shopping_cart where customerID=? and movieID=? and storeID=?',
                (customer_id, movie_id, store_id))
    current_amount = cur.fetchone()[0]

    # delete or update record into database.shopping_cart
    if current_amount + amount <= 0:
        cur.execute('delete from shopping_cart where customerID=? and movieID=? and storeID=?',
                    (customer_id, movie_id, store_id))
    else:
        cur.execute('update shopping_cart set amount=? where customerID=? and movieID=? and storeID=?',
                    (current_amount + amount, customer_id, movie_id, store_id))

    # update amountTemp in database.stock
    cur.execute('select amountTemp from stock where movieID=? and storeID=?', (movie_id, store_id))
    temp_amount_all = cur.fetchone()[0]
    cur.execute('update stock set amountTemp=? where movieID=? and storeID=?',
                (temp_amount_all - amount, movie_id, store_id))

    conn.commit()

    return jsonify({"operation": "reduce item", "movieID": movie_id, "amount": amount})


@app.route('/shopping/update/<int:movie_id>', methods=['POST'])
def update_item_in_cart(movie_id):
    response = request.get_json()
    amount = response['number']
    store_id = int(session['store_id'])
    conn, cur = get_db()

    cur.execute('select customerID from customer where userID=?', (current_user.id,))
    customer_id = cur.fetchone()[0]

    cur.execute('select amount from shopping_cart where customerID=? and movieID=? and storeID=?',
                (customer_id, movie_id, store_id))
    current_amount = cur.fetchone()[0]

    # remove or update record into database.shopping_cart
    if amount <= 0:
        amount = 0
        cur.execute('delete from shopping_cart where customerID=? and movieID=? and storeID=?',
                    (customer_id, movie_id, store_id))
    else:
        cur.execute('update shopping_cart set amount=? where customerID=? and movieID=? and storeID=?',
                    (amount, customer_id, movie_id, store_id))

    # update amountTemp in database.stock
    cur.execute('select amountTemp from stock where movieID=? and storeID=?', (movie_id, store_id))
    temp_amount_all = cur.fetchone()[0]
    cur.execute('update stock set amountTemp=? where movieID=? and storeID=?',
                (temp_amount_all - amount + current_amount, movie_id, store_id))

    conn.commit()
    return jsonify({"operation": "update item", "movieID": movie_id, "amount": amount})


@app.route('/shopping/count_items', methods=['POST'])
def count_items_in_cart():
    store_id = int(session['store_id'])
    conn, cur = get_db()

    cur.execute('select customerID from customer where userID=?', (current_user.id,))
    customer_id = cur.fetchone()[0]

    cur.execute('''
        select COUNT(*)
        from shopping_cart Shop
        where customerID=? and Shop.storeID=?
        ''', (customer_id, store_id))
    count = cur.fetchone()
    return jsonify(count)


@app.route('/checkout', methods=['POST'])
def checkout_for_cart():
    records = get_items()
    if not records:
        return jsonify({"error": "Your shopping cart is empty. Please add movies first."})
    data = {
        'business': '9AK39BT347LLA',
        'cmd': '_cart',
        'upload': 1,
        'no_shipping': 1,
        'currency_code': 'USD',
    }
    for idx, record in enumerate(records):
        data_append = {
            'item_number_%d' % (idx + 1): record[1],
            'item_name_%d' % (idx + 1): record[2],
            'amount_%d' % (idx + 1): record[3],
            'quantity_%d' % (idx + 1): record[0],
            'tax_rate_%d' % (idx + 1): 7}
        data = {**data, **data_append}
    return jsonify(data)


@app.route('/listener')
def listener():
    """
    Validate transaction status from PayPal, and insert transaction record into database.
    """
    transaction_id = request.args.get('tx')
    if not transaction_id:
        return redirect(url_for('index'))

    data = {
        'cmd': '_notify-synch',
        'tx': transaction_id,
        'at': 'Rs8M8Q-rndgOUSnWmGaYxR76aPnZSrWX8P3oWNivJ0TLN2hKthF8cu65Rwa'
    }
    response = requests.post(
        "https://www.sandbox.paypal.com/cgi-bin/webscr", data=data).text
    if response.startswith('SUCCESS'):
        record_transaction(transaction_id)
        flash("Success!")
        return redirect('/receipt/{}&{}'.format(transaction_id, 'success'))
    else:
        flash("Something wrong with your purchase, please contact PayPal for more information.")
        return redirect('/receipt/{}&{}'.format(transaction_id, 'fail'))


def record_transaction(paypal_id):
    store_id = int(session['store_id'])
    purchase_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn, cur = get_db()

    cur.execute('select customerID from customer where userID=?', (current_user.id,))
    customer_id = cur.fetchone()[0]

    # get items in the cart
    cur.execute('select amount, movieID from shopping_cart where customerID=? and storeID=?', (customer_id, store_id))
    records = cur.fetchall()

    # remove records from database.shopping_cart
    cur.execute('delete from shopping_cart where customerID=? and storeID=?', (customer_id, store_id))

    # update database.stock & database.transaction
    for amount, movie_id in records:
        cur.execute('select amount from stock where movieID=? and storeID=?', (movie_id, store_id))
        amount_all = cur.fetchone()[0]
        cur.execute('update stock set amount=? where movieID=? and storeID=?', (amount_all-amount, movie_id, store_id))
        cur.execute('insert into transactions values (?,?,?,?,?,?,?)',
                    (None, amount, purchase_time, paypal_id, customer_id, movie_id, store_id))
    conn.commit()
    return jsonify({"operation": "record transaction"})
