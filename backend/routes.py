from datetime import datetime
from functools import wraps
from flask import Blueprint, session, redirect, url_for, current_app
from flask import render_template, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, db  # Ensure you import User and db from your models
from sqlalchemy import text

main = Blueprint('main', __name__)

# Utility decorators
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

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'error')
            return redirect(url_for('main.signup'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('signup.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = str(user.id)
            session['username'] = user.username
            session['user_role'] = user.role
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
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.username = request.form['name']
        user.phone = request.form['phone']
        user.email = request.form['email']
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))

    return render_template('profile.html', user=user)


@main.route('/menu/restaurant', methods=['GET'])
@login_required
def restaurant_menu():
    # Use SQLAlchemy's text() function to handle raw SQL queries
    result = db.session.execute(text("SELECT * FROM menu WHERE type='restaurant'")).fetchall()
    is_open = 9 <= datetime.now().hour <= 21
    return render_template('restaurant_menu.html', menu=result, is_open=is_open)

@main.route('/menu/bar', methods=['GET'])
@login_required
def bar_menu():
    # Logic for bar menu
    return render_template('bar_menu.html')

@main.route('/menu/order', methods=['POST'])
@login_required
def place_order():
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

    db.session.execute(
        "INSERT INTO orders (user_id, food_item, pickup_time, status, order_time) "
        "VALUES (:user_id, :food_item, :pickup_time, :status, :order_time)",
        order_details
    )
    db.session.commit()

    flash('Order placed successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/admin/dashboard', methods=['GET'])
@manager_required
def admin_dashboard():
    # Count orders for the admin dashboard
    total_orders = db.session.execute("SELECT COUNT(*) FROM orders").scalar()
    pending_orders = db.session.execute("SELECT COUNT(*) FROM orders WHERE status='Pending'").scalar()
    completed_orders = db.session.execute("SELECT COUNT(*) FROM orders WHERE status='Completed'").scalar()

    return render_template(
        'admin_dashboard.html',
        total_orders=total_orders,
        pending_orders=pending_orders,
        completed_orders=completed_orders,
    )

@main.route('/rooms', methods=['GET'])
@login_required
def room_list():
    # Correct the raw SQL query by wrapping it with text()
    rooms = db.session.execute(text("SELECT * FROM rooms")).fetchall()
    return render_template('rooms.html', rooms=rooms)

@main.route('/rooms/book', methods=['POST'])
@login_required
def book_room():
    room_id = request.form['room_id']
    user_details = {
        'name': request.form['name'],
        'phone': request.form['phone'],
        'arrival_date': request.form['arrival_date'],
        'hours': request.form['hours'],
    }

    room = db.session.execute(
        "SELECT * FROM rooms WHERE id=:room_id AND status='available'", {'room_id': room_id}
    ).fetchone()

    if not room:
        flash('Room is not available.', 'error')
        return redirect(url_for('main.room_list'))

    db.session.execute(
        "UPDATE rooms SET status='booked', booked_by=:user_details WHERE id=:room_id",
        {'user_details': user_details, 'room_id': room_id}
    )
    db.session.commit()

    flash('Room booked successfully!', 'success')
    send_booking_notification(user_details, room_id)
    return redirect(url_for('main.room_list'))

# Notification functions
def send_booking_notification(user_details, room_id):
    message = (
        f"Hello {user_details['name']},\n\n"
        f"Your room (ID: {room_id}) is booked.\n"
        f"Arrival Date: {user_details['arrival_date']}\n"
        f"Duration: {user_details['hours']} hours\n\n"
        "Thank you for choosing our service!"
    )
    print(f"Notification sent: {message}")

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
