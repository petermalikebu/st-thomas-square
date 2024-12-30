from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Define Blueprint
main = Blueprint('main', __name__)

# Utility decorators for authentication and role-based access control
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to access this page.', 'error')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'manager':
            flash('You must be a manager to access this page.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@main.route('/')
def index():
    return render_template('base.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        db = current_app.db  # or use g.db if you set it in before_request
        if db.users.find_one({'email': email}):
            flash('Email is already registered.', 'error')
            return redirect(url_for('main.signup'))

        hashed_password = generate_password_hash(password)
        db.users.insert_one({'username': username, 'email': email, 'password': hashed_password, 'role': 'user'})
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('signup.html')

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

# Define Blueprint
main = Blueprint('main', __name__)

# Utility decorators for authentication and role-based access control
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to access this page.', 'error')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'manager':
            flash('You must be a manager to access this page.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@main.route('/')
def index():
    return render_template('base.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        db = current_app.db  # Use current_app.db to access the database
        if db.users.find_one({'email': email}):
            flash('Email is already registered.', 'error')
            return redirect(url_for('main.signup'))

        hashed_password = generate_password_hash(password)
        db.users.insert_one({'username': username, 'email': email, 'password': hashed_password, 'role': 'user'})
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('signup.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = current_app.db  # Use current_app.db to access the database
        user = db.users.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['user_role'] = user.get('role', 'user')
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user_name=session.get('username'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = current_app.db
    user = db.users.find_one({'_id': session['user_id']})

    if request.method == 'POST':
        updated_data = {
            'name': request.form['name'],
            'phone': request.form['phone'],
            'email': request.form['email']
        }
        db.users.update_one({'_id': session['user_id']}, {'$set': updated_data})
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))

    return render_template('profile.html', user=user)

@main.route('/menu/restaurant', methods=['GET'])
@login_required
def restaurant_menu():
    db = current_app.db
    menu = db.menu.find_one({'type': 'restaurant'})
    is_open = 9 <= datetime.now().hour <= 21
    return render_template('restaurant_menu.html', menu=menu, is_open=is_open)

@main.route('/menu/order', methods=['POST'])
@login_required
def place_order():
    db = current_app.db
    order_details = {
        'user_id': session['user_id'],
        'food_item': request.form['food_item'],
        'pickup_time': request.form['pickup_time'],
        'status': 'Pending',
        'order_time': datetime.now()
    }

    pickup_hour = int(order_details['pickup_time'].split(':')[0])
    if pickup_hour < 9 or pickup_hour > 21:
        flash('Pickup time must be between 9:00 AM and 9:00 PM.', 'error')
        return redirect(url_for('main.restaurant_menu'))

    db.orders.insert_one(order_details)
    flash('Order placed successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/admin/menu', methods=['GET', 'POST'])
@manager_required
def update_menu():
    db = current_app.db
    if request.method == 'POST':
        menu_data = request.form['menu']
        db.menu.update_one({'type': 'restaurant'}, {'$set': {'items': menu_data}}, upsert=True)
        flash('Menu updated successfully!', 'success')
    menu = db.menu.find_one({'type': 'restaurant'})
    return render_template('admin_menu.html', menu=menu)

@main.route('/admin/dashboard', methods=['GET'])
@manager_required
def admin_dashboard():
    db = current_app.db
    total_orders = db.orders.count_documents({})
    pending_orders = db.orders.count_documents({'status': 'Pending'})
    completed_orders = db.orders.count_documents({'status': 'Completed'})
    total_stock = sum(item['quantity'] for item in db.stock.find())

    return render_template('admin_dashboard.html',
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           completed_orders=completed_orders,
                           total_stock=total_stock)


@main.route('/bar', methods=['GET'])
@login_required
def bar_menu():
    db = current_app.db
    bar_events = db.events.find({'type': 'bar'})
    bartender_on_duty = db.staff.find_one({'role': 'bartender', 'on_duty': True})
    return render_template('bar_menu.html', events=bar_events, bartender=bartender_on_duty)

@main.route('/rooms', methods=['GET'])
@login_required
def room_list():
    db = current_app.db
    rooms = db.rooms.find()
    return render_template('rooms.html', rooms=rooms)

@main.route('/rooms/book', methods=['POST'])
@login_required
def book_room():
    db = current_app.db
    room_id = request.form['room_id']
    user_details = {
        'name': request.form['name'],
        'phone': request.form['phone'],
        'arrival_date': request.form['arrival_date'],
        'hours': request.form['hours'],
    }
    # Update room status and store booking info
    db.rooms.update_one(
        {'_id': room_id, 'status': 'available'},
        {'$set': {'status': 'booked', 'booked_by': user_details}}
    )
    flash('Room booked successfully!', 'success')
    send_booking_notification(user_details, room_id)
    return redirect(url_for('main.room_list'))  # This should work as the endpoint is part of the 'main' blueprint


def send_booking_notification(user_details, room_id):
    # Simulate sending an email or SMS
    message = (
        f"Hello {user_details['name']},\n\n"
        f"Your room (ID: {room_id}) is booked.\n"
        f"Arrival Date: {user_details['arrival_date']}\n"
        f"Duration: {user_details['hours']} hours\n\n"
        "Thank you for choosing St. Thomas Square!"
    )
    print(f"Notification sent: {message}")  # Replace with actual notification logic




@main.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

# Functions for notifications (can be extended with actual email/SMS APIs)
def send_order_notification(order_details):
    print(f"Order notification sent: {order_details}")

def send_booking_notification(user_details, room_id):
    print(f"Booking notification sent for room {room_id}: {user_details}")
