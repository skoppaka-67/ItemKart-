##############################################################
##############################################################
################## Item Kart #################################
##############################################################
##############################################################

# Create an application for Item Kart
# The application should have the following functionality:
# 1. User login (Authentication)
# 2. List all the items available in the shop as per category (With limits and offsets)
# 3. Add the items to the cart (Authentication required)
# 4. List the items present in the cart (Authentication required)
# 5. Remove and Edit items of the cart (Authentication required)


# You can start writing your code for the above mentioned functionalities from here

from flask import Flask, request, jsonify, flash, session, redirect, url_for, render_template, abort
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
import re, json, jwt, datetime, copy
from functools import wraps
import pymongo
from pymongo import MongoClient
from utility import conf

client = MongoClient(conf.mongoconfig['connection_url'])
db = client[conf.mongoconfig['database_name']]
app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()
app.secret_key = "8aacf358ee03b9e906455587c9538669"
cart_list = []
User_DATA = db.users.find({"name": "John Doe"}, {"_id": 0})[0]


def token_required(f):
    """
    function to verify the jwt tokens, will will be used a decorator to the functions

    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'token' in session:
            token = session['token']
        if not token:
            return render_template("login.html")
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            # current_user =  db.user.find({"username":data['username']}, {"_id": 0})[0]
            current_user = data['username']
        except:
            return render_template("login.html")
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and len(session) > 0:

        if session['username'] == User_DATA['username']:
            return redirect(url_for('my_home'))
    if request.method == 'POST':

        if request.form['username'] == User_DATA['name'] and request.form['password'] == User_DATA['password']:
            if len(session) > 0 and session['username'] == request.form['username']:
                flash("Already logged In ")

            session['username'] = request.form['username']
            session['password'] = request.form['password']

            """creartion of Jwt tokens  and stored in session  below token makes user to login after every 5 minutes"""

            token = jwt.encode(
                {'username': 'John Doe', 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)},
                app.config['SECRET_KEY'])

            session['token'] = token.decode('UTF-8')

            return redirect(url_for('add_to_cart'))
    return render_template("login.html")


@app.route('/home', methods=['GET'])
def home():
    """route to display tags """

    item_list = db.items.distinct("tags")
    return render_template('category_list.html', li=item_list)


@app.route('/category', methods=['GET'])
def category():
    """route to display  items of selected category along with pagination and url to move back and forth """

    data = []
    temp_json = {}
    category = str(request.args['category_list'])
    limit = int(request.args['limit'])
    offset = int(request.args['offset'])  # final record index
    starting_id = db.items.find().sort('_id', pymongo.ASCENDING)
    last_id = starting_id[offset]['_id']  # final record _id
    # item_list = db.items.distinct("tags")

    # for item_tag in item_list[offset-limit:offset]:
    cursy = db.items.find({'_id': {'$gt': last_id}, "tags": category}, {"name": 1, "price": 1, "description": 1}).sort(
        '_id', pymongo.ASCENDING).limit(limit)
    # datavalue[item_tag] =[record for record in cursy]
    for rec in cursy:
        temp_json[category] = rec
        data.append(copy.deepcopy(temp_json))
        temp_json.clear()
    next_url = '/category' + '?category_list=' + str(category) + '&limit=' + str(limit) + '&offset=' + str(
        offset + limit)
    prev_url = '/category' + '?category_list=' + str(category) + '&limit=' + str(limit) + '&offset=' + str(
        offset - limit)

    return jsonify({'result': data, 'prev_url': prev_url, 'next_url': next_url})


@app.route('/add_to_cart', methods=['GET', 'POST'])
@token_required
def add_to_cart(current_user):
    if request.method == 'GET' and len(session) > 0:

        if session['username'] == User_DATA['name']:
            return render_template('add_cart.html')
    if request.method == 'POST' and len(session) > 0:
        if current_user != 'John Doe':
            return jsonify({'message': 'cannot perform that function!'})

        if session['username'] == User_DATA['name']:
            temp_var = request.get_data()
            temp_var = temp_var.decode('utf-8')
            # temp_list = temp_var.split("&")
            item_name = temp_var.split('=')[-1].replace("+", " ")

            cursy = json.dumps(db.items.find({"name": item_name}, {'_id': 0})[0])
            if cursy in cart_list:
                flash("Item already exists")
                return render_template('add_cart.html')
            cart_list.append(copy.deepcopy(cursy))
            flash("Item added")
            return render_template('add_cart.html')
        flash("invalid User,Login again")
        return render_template('add_cart.html')
    return render_template('add_cart.html')


@app.route('/show_cart', methods=['GET'])
@token_required
def show_cart(current_user):
    if request.method == 'GET' and len(session) > 0:

        if session['username'] == User_DATA['name']:
            if current_user != 'John Doe':
                return jsonify({'message': 'cannot perform that function!'})
            return jsonify({"items": [x.replace('"', "").replace("'", '') for x in cart_list]})
        return render_template('login.html')


@app.route('/remove_cart', methods=['GET', 'POST'])
@token_required
def remove_cart(current_user):
    if request.method == 'GET' and len(session) > 0:

        if session['username'] == User_DATA['name']:
            return render_template('remove_cart.html')
    if request.method == 'POST' and len(session) > 0:
        if current_user != 'John Doe':
            return jsonify({'message': 'cannot perform that function!'})

        if session['username'] == User_DATA['name']:
            temp_var = request.get_data()
            temp_var = temp_var.decode('utf-8')
            # temp_list = temp_var.split("&")
            item_name = temp_var.split('=')[-1].replace("+", " ")

            cursy = json.dumps(db.items.find({"name": item_name}, {'_id': 0})[0])
            if cursy not in cart_list:
                flash("Item is not present in  cart")
                return render_template('remove_cart.html')
            cart_list.remove(cursy)
            flash("Item deleted")
            return render_template('remove_cart.html')
        flash("invalid User,Login again")
        return render_template('remove_cart.html')
    return render_template('remove_cart.html')


@app.route('/logout')
def logout():
    session.clear()

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
