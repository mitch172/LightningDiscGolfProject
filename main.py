from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from decimal import *
import re

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'milestone2'

# Intialize MySQL
mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def Home():
    return render_template('index.html')


@app.route('/', methods=['GET', 'POST'])
def Contact():
    return render_template('index.html')


# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
def userLogin():
    # Output message if something goes wrong...
    msg = ''
    # Check if "email" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account Admin account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Admin WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['ID'] = account['ID']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('adminHome'))
        # If account does not exist in Admin, check to see if credentials exist in User
        elif not account:
            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM User WHERE username = %s AND password = %s', (username, password,))
            # Fetch one record and return result
            account = cursor.fetchone()
            # If account exists in accounts table in out database
            if account:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['ID'] = account['ID']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('userHome'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('ID', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('userLogin'))


# http://localhost:5000/Falsk/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register2', methods=['GET', 'POST'])
def userRegister():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = %s AND email = %s', (username, email,))
        account = cursor.fetchone()
        # If account exists show error and valIDation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'InvalID email address!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valID, now insert new account into accounts table
            cursor.execute('INSERT INTO User (username, email, password) VALUES (%s,%s, %s)', (username, email, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythinlogin/userHome - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def userHome():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM Admin WHERE username = %s', (session['username'],))
         account= cursor.fetchone()
         if account:
            return render_template('adminHome.html', username=session['username'])
         else:
            return render_template('userHome.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('userLogin'))


# http://localhost:5000/pythinlogin/adminHome - this will be the home page, only accessible for loggedin admins
@app.route('/adminHome/home')
def adminHome():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('adminHome.html', username=session['username'])
    else:
        # User is not loggedin redirect to login page
        return redirect(url_for('userLogin'))


@app.route('/addItem', methods=['GET', 'POST'])
def addItem():
    # Output message if something goes wrong...
    msg = ''
    # Check if "brand", "name", "releaseDate", "discNumber", "abbreviation", and "cost" POST requests exist (user submitted form)
    if request.method == 'POST' and 'image' in request.form and 'brand' in request.form and 'name' in request.form and 'release_date' in request.form and 'disc_number' in request.form and 'abbreviation' in request.form and 'cost' in request.form:
        # Create variables for easy access
        image = request.form['image']
        brand = request.form['brand']
        name = request.form['name']
        release_date = request.form['release_date']
        disc_number = request.form['disc_number']
        abbreviation = request.form['abbreviation']
        cost = request.form['cost']

        # Check if product exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Item WHERE name = %s', (name,))
        item = cursor.fetchone()
        # If item exists show error and validation checks
        if item:
            msg = 'Item already exists!'
        elif not re.match('^[A-Za-z0-9_-]*$', image):
            msg = 'Image must contain only characters, numbers, and symbols!'
        elif not re.match(r'[A-Za-z0-9]+', brand):
            msg = 'Brand must contain only characters and numbers!'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Name must contain only characters and numbers!'
        elif not re.match(r'[0-9]+', release_date):
            msg = 'Release date must contain only numbers!'
        # elif not re.match(r'[0-9]+', disc_number):
        #   msg = 'Disc number must contain only numbers!'
        elif not re.match(r'[A-Za-z0-9]+', abbreviation):
            msg = 'Abbreviation must contain only characters and numbers!'
        elif not re.match(r'[0-9]+', cost):
            msg = 'Cost must contain only numbers!'
        elif not brand or not name or not release_date or not disc_number:
            msg = 'Please fill out the form!'
        else:
            # Item doesnt exists and the form data is valid, now insert new item into items table
            cursor.execute('INSERT INTO Item (image, brand, name, release_date, disc_number, abbreviation, cost) VALUES ( %s, %s, %s, %s, %s, %s)', (image, brand, name, release_date, disc_number, abbreviation, cost,))
            mysql.connection.commit()
            msg = 'Item successfully added'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('addItem.html', msg=msg)


@app.route('/inventory.html', methods=['GET', 'POST'])
def inventory():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Item')
    data = cursor.fetchall()
    return render_template('inventory.html', output_data=data)


@app.route('/cart.html', methods=['GET', 'POST'])
def showCart():
    return render_template('cart.html')

#Will be moved, method for viewing products
@app.route('/products.html',methods=['GET', 'POST'])
def products():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Item')
    rows= cursor.fetchall()
    return render_template('products.html',items=rows)


#Method for adding project to cart, uses array for each thing
@app.route('/add', methods=['POST'])
def add_product_to_cart():
    cursor = None
    try:
        _quantity = int(request.form['quantity'])
        _code = request.form['code']
        # validate the received values
        if _quantity and _code and request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM Item WHERE ItemCode=%s", (_code,))
            row = cursor.fetchone()

            costStr=row['Cost']
            cost= Decimal(costStr)
            itemArray = {row['ItemCode']: {'Name': row['Name'], 'ItemCode': row['ItemCode'], 'quantity': _quantity, 'Cost': cost, 'Image': row['Image'], 'total_price': _quantity * cost}}

            all_total_price = 0
            all_total_quantity = 0

            session.modified = True
            if 'cart_item' in session:
                if row['ItemCode'] in session['cart_item']:
                    for key, value in session['cart_item'].items():
                        if row['ItemCode'] == key:
                            old_quantity = session['cart_item'][key]['quantity']
                            total_quantity = old_quantity + _quantity
                            session['cart_item'][key]['quantity'] = total_quantity
                            session['cart_item'][key]['total_price'] = total_quantity * cost
                else:
                    session['cart_item'] = array_merge(session['cart_item'], itemArray)

                for key, value in session['cart_item'].items():
                    individual_quantity = int(session['cart_item'][key]['quantity'])
                    individual_price = float(session['cart_item'][key]['total_price'])
                    all_total_quantity = all_total_quantity + individual_quantity
                    all_total_price = all_total_price + individual_price
            else:
                session['cart_item'] = itemArray
                all_total_quantity = all_total_quantity + _quantity
                all_total_price = all_total_price + _quantity * cost

            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

            return redirect(url_for('products'))
        else:
            return 'Error while adding item to cart'
    except Exception as e:
        print(e)
    finally:
        cursor.close()


#Method to empty the cart
@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('.showCart'))
    except Exception as e:
        print(e)


#Method to delete product from the cart
@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True

        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

        return redirect(url_for('.showCart'))
    except Exception as e:
        print(e)


#Method to merge arrays of items
def array_merge( first_array , second_array ):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


@app.route('/products/<string:id>')
def single_item_page(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Item WHERE ItemID= %s',id)
    item= cursor.fetchone()
    return render_template('singleProd.html',item=item)



if __name__ == '__main__':
    app.run()
