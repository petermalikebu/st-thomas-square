from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4

# Initialize SQLAlchemy
db = SQLAlchemy()

def generate_uuid():
    return str(uuid4())

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'manager'
    phone = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"

class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'restaurant', 'snack', etc.

    def __repr__(self):
        return f"<MenuItem {self.name}>"

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    food_item = db.Column(db.String(100), nullable=False)
    pickup_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Completed', etc.
    order_time = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f"<Order {self.food_item} for {self.user_id}>"

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='available')  # 'available', 'booked'
    booked_by = db.Column(db.JSON, nullable=True)  # Store booking details

    def __repr__(self):
        return f"<Room {self.name} - {self.status}>"

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Event {self.name} on {self.date}>"

class Staff(db.Model):
    __tablename__ = 'staff'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        return f"<Staff {self.name} - {self.position}>"
