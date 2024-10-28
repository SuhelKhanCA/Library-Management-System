from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # Store hashed passwords here
    is_admin = db.Column(db.Boolean, default=False)

    # Method to check if user is an admin
    def is_admin(self):
        return self.is_admin

    # Set the password with hashing
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check if password is correct
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Static method for authentication
    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

class Membership(db.Model):
    __tablename__ = 'memberships'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date, default=datetime.utcnow)
    duration_months = db.Column(db.Integer, nullable=False, default=6)  # 6, 12, or 24 months
    is_active = db.Column(db.Boolean, default=True)

    @property
    def end_date(self):
        return self.start_date + timedelta(days=self.duration_months * 30)  # Approximate end date

    def extend_membership(self, months=6):
        """Extends the membership by a specified number of months (default is 6)."""
        self.duration_months += months


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='book')  # 'book' or 'movie'
    is_available = db.Column(db.Boolean, default=True)
    copies_total = db.Column(db.Integer, nullable=False, default=1)
    copies_checked_out = db.Column(db.Integer, nullable=False, default=0)

    def check_availability(self):
        return self.copies_checked_out < self.copies_total

    def checkout(self):
        """Mark a book as checked out, decreasing availability."""
        if self.check_availability():
            self.copies_checked_out += 1
            self.is_available = self.check_availability()
            return True
        return False

    def return_book(self):
        """Mark a book as returned, increasing availability."""
        if self.copies_checked_out > 0:
            self.copies_checked_out -= 1
            self.is_available = self.check_availability()
            return True
        return False


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    issue_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.Date, nullable=True)  # Expected return date
    actual_return_date = db.Column(db.Date, nullable=True)
    fine = db.Column(db.Float, default=0.0)
    remarks = db.Column(db.String(250), nullable=True)

    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    book = db.relationship('Book', backref=db.backref('transactions', lazy=True))

    @property
    def is_overdue(self):
        """Check if the book return is overdue based on the planned return date."""
        if self.return_date and not self.actual_return_date:
            return datetime.utcnow().date() > self.return_date
        return False

    def calculate_fine(self, daily_rate=1.0):
        """Calculate fine if the book is returned late."""
        if self.is_overdue:
            overdue_days = (datetime.utcnow().date() - self.return_date).days
            self.fine = overdue_days * daily_rate
            return self.fine
        return 0.0
