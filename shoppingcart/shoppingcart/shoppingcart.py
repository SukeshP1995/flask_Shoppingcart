# -*- coding: utf-8 -*-
import json
import os # for paths
import datetime
from flask import Flask, request, session, redirect, url_for, abort, \
     render_template, flash, jsonify  # prune g
from flask_sqlalchemy import SQLAlchemy

# Instantiate and configure our little app :)
app = Flask(__name__)

app.config['DEBUG'] = True                      # used for DEBUGging during runtime
app.config['SECRET_KEY'] ='super-secret-key'    
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
current_email = ''

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "static/data", "books.json")
with open(json_url) as data_file:
    data = json.loads(data_file.read())
    
db = SQLAlchemy(app)
books = data['items']

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.String(80))
    book_id = db.Column(db.String(80))
    title = db.Column(db.String(80))
    price = db.Column(db.Float)
    thumbnail = db.Column(db.String(80))

    def __init__(self, email_id, book_id, title, price, thumbnail):
        self.email_id = email_id
        self.book_id = book_id
        self.title = title
        self.price = price
        self.thumbnail = thumbnail

    def __repr__(self):
        return '<name %r book %r title %r price %r thumbnail %r>' % self.book_id, self.title, self.price, self.thumbnail

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String(80))
    phone = db.Column(db.String(10))
    book_id = db.Column(db.String(80))
    title = db.Column(db.String(80))
    price = db.Column(db.Float)
    thumbnail = db.Column(db.String(80))
    count = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    def __init__(self, email_id, phone, book_id, title, price, thumbnail, count, timestamp):
        self.email_id = email_id
        self.phone = phone
        self.book_id = book_id
        self.title = title
        self.price = price
        self.thumbnail = thumbnail
        self.count = count
        self.timestamp = timestamp

class Register(db.Model):
    username = db.Column(db.String(80))
    email_id = db.Column(db.String(80), nullable=False, primary_key=True)
    phone = db.Column(db.String(10))
    password = db.Column(db.String(80))
    
    def __init__(self, username, email_id, phone, password):
        self.username = username
        self.email_id = email_id
        self.phone = phone
        self.password = password

db.create_all()
@app.route('/', methods=['GET'])
def mainpage():
    return redirect(url_for('show_books'))
    
@app.route('/show_books', methods=['GET'])
def show_books():
    return render_template('catalog.html', books=json.dumps(data))

@app.route('/addtocart/<int:i>/')
def add_to_cart(i):
    if not session.get('logged_in'):
        return redirect(url_for('show_books'))
    book_id = books[i]["id"]
    title = books[i]["volumeInfo"]["title"]
    price = books[i]["saleInfo"]["retailPrice"]["amount"]
    thumbnail = books[i]["volumeInfo"]["imageLinks"]["smallThumbnail"]
    l = db.session.query(db.func.count(Cart.book_id).label('count'),Cart.book_id).filter(Cart.email_id == current_email).filter(Cart.book_id == book_id).group_by(Cart.book_id).all()
    if len(l)!=0 and l[0][0] >= 3:
        print(jsonify("full"))
        return jsonify("full")
    cart_entry = Cart(current_email, book_id, title, float(price), thumbnail)
    db.session.add(cart_entry)
    db.session.commit()
    return jsonify("not_full")

@app.route('/cart', methods=['GET'])
def cart():
    if not session.get('logged_in'):
        return redirect(url_for('show_books'))
    books_list = db.session.query(Cart.book_id,Cart.title, Cart.price, Cart.thumbnail, db.func.count(Cart.book_id).label('count')).filter(Cart.email_id == current_email).group_by(Cart.book_id).all()
    total = db.session.query(Cart).filter(Cart.email_id == current_email).count()
    return render_template('cart.html', books_list=books_list, total=total)

@app.route('/plus/<string:id>/')
def plus(id):
    cart = db.session.query(Cart.id, Cart.book_id,Cart.title, Cart.price, Cart.thumbnail ).filter(Cart.email_id == current_email).filter(Cart.book_id == id)
    l = db.session.query(db.func.count(Cart.book_id).label('count'),Cart.book_id).filter(Cart.email_id == current_email).filter(Cart.book_id == id).group_by(Cart.book_id).all()
    if len(l)!=0 and l[0][0]>=3:
        return jsonify("full")
    cart_entry = Cart(current_email, cart[0].book_id, cart[0].title, float(cart[0].price), cart[0].thumbnail)
    db.session.add(cart_entry)
    db.session.commit()
    return jsonify("plus")

@app.route('/minus/<string:id>/')
def minus(id):
    cart = db.session.query(Cart.id, Cart.book_id,Cart.title, Cart.price, Cart.thumbnail ).filter(Cart.book_id == id)
    cart = Cart.query.get(cart[0].id)
    db.session.delete(cart)
    db.session.commit()
    l = db.session.query(db.func.count(Cart.book_id).label('count'), Cart.book_id).filter(Cart.email_id == current_email).filter(Cart.book_id == id).group_by(Cart.book_id).all()
    if len(l)==0:
        return jsonify("empty")
    return jsonify("minus")

@app.route('/checkout/', methods=['GET'])
def checkout():
    global current_email
    books_list = db.session.query(Cart.email_id, Cart.book_id, Cart.title, Cart.price, Cart.thumbnail, db.func.count(Cart.book_id).label('count'), db.func.sum(Cart.price).label("total")).filter(Cart.email_id == current_email).group_by(Cart.book_id).all()
    return render_template('checkout.html', books_list=books_list)

@app.route('/clear_cart/')
def clear_cart():
    try:
        num_rows_deleted = db.session.query(Cart).delete()
        db.session.commit()
        checkout()
    except:
        db.session.rollback()
    return jsonify(num_rows_deleted)

@app.route('/login_page/')
def login_page():
    if session.get('logged_in'):
        return redirect(url_for('show_books'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('logged_in'):
        return redirect(url_for('show_books'))
    global current_email
    print('here')
    error = None
    username = request.form['username']
    email_id = request.form['email_id']
    phone = request.form["phone"]
    password = request.form['password']
    retype_password = request.form['retype_password'] 

    if request.method == 'POST':
        if password != retype_password:
            error = 'Passwords do not match'
        elif len(username)!=0 and len(email_id)!=0  and len(password)!=0 and len(retype_password)!=0 and len(phone)!=0:
            try:
                register = Register(username, email_id, phone, password)
                db.session.add(register)
                db.session.commit()
            except:
                error = 'Email already exists'

    return render_template('login.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('show_books'))
    global current_email
    email_id = request.form['email_id']
    password = request.form['password']
    error = None
    if len(email_id) == 0 or len(password)==0:
        flash('Enter both fields')
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        register = db.session.query(Register.email_id, Register.password).filter(Register.email_id == email_id).all()
        if len(register) == 0:
            flash('Enter correct email')
            return redirect(url_for('login_page'))
        else:
            if register[0].password == password:
                global current_email
                current_email = email_id
                session['logged_in'] = True
                return redirect(url_for('show_books'))
            else:
                flash('Enter correct password')
                return redirect(url_for('login_page'))


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if not session.get('logged_in'):
        return redirect(url_for('show_books'))
    orders =  db.session.query(Orders.title, Orders.price, Orders.thumbnail, Orders.timestamp, Orders.count).filter(Orders.email_id == current_email).order_by(db.desc(Orders.timestamp)).all()

    return render_template('orders.html', orders=orders)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in', None)
    global current_email
    current_email = ''
    return redirect(url_for('show_books'))

@app.route('/proceed')
def proceed():
    phone = db.session.query(Register.phone).filter(Register.email_id == current_email).all()
    phone = phone[0].phone
    books_list = db.session.query(Cart.email_id, Cart.book_id, Cart.title, Cart.price, Cart.thumbnail, db.func.count(Cart.book_id).label('count'), db.func.sum(Cart.price).label("total")).filter(Cart.email_id == current_email).group_by(Cart.book_id).all()
    now = datetime.datetime.now()
    timenow = list(map(int,now.strftime("%y:%m:%d:%H:%M:%S").split(':')))
    timestamp = datetime.datetime(timenow[0]+2000,timenow[1],timenow[2],timenow[3],timenow[4],timenow[5])
    for book in books_list:
        order = Orders(book.email_id, phone, book.book_id, book.title, book.price, book.thumbnail, book.count, timestamp)
        db.session.add(order)
    db.session.commit()
    try:
        num_rows_deleted = db.session.query(Cart).delete()
        db.session.commit()
        checkout()
    except:
        db.session.rollback()
    return jsonify(num_rows_deleted)
    
    

if __name__ == '__main__':
    app.run()


