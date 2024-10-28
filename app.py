from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from config import Config
from models import db, User, Book, Membership, Transaction
from forms import LoginForm, BookForm, MembershipForm, UserForm, IssueForm, ReturnForm, FinePaymentForm
from datetime import datetime, timedelta

# Initialize Flask app, DB, and login manager
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Index Route
@app.route('/')
def index():
    return render_template('index.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# Add Membership Route (Admin Only)
@app.route('/add_membership', methods=['GET', 'POST'])
@login_required
def add_membership():
    if not current_user.is_admin():
        flash('Access Denied', 'danger')
        return redirect(url_for('index'))
    form = MembershipForm()
    if form.validate_on_submit():
        new_membership = Membership(
            name=form.name.data,
            duration_months=form.duration.data,
            start_date=datetime.utcnow()
        )
        db.session.add(new_membership)
        db.session.commit()
        flash('Membership added successfully!', 'success')
        return redirect(url_for('manage_memberships'))
    return render_template('maintenance/memberships.html', form=form)


# Check Book Availability Route
@app.route('/check_availability', methods=['GET', 'POST'])
@login_required
def check_availability():
    form = BookForm()
    books = []
    if form.validate_on_submit():
        search_term = form.search.data
        books = Book.query.filter(Book.title.contains(search_term)).all()
    return render_template('transactions/availability.html', form=form, books=books)


# Issue Book Route
@app.route('/issue_book', methods=['GET', 'POST'])
@login_required
def issue_book():
    form = IssueForm()
    if form.validate_on_submit():
        book = Book.query.filter_by(title=form.title.data).first()
        if book and book.checkout():
            transaction = Transaction(
                user_id=current_user.id,
                book_id=book.id,
                issue_date=datetime.utcnow(),
                return_date=datetime.utcnow() + timedelta(days=15)
            )
            db.session.add(transaction)
            db.session.commit()
            flash(f'Book "{form.title.data}" issued successfully!', 'success')
            return redirect(url_for('index'))
        flash('Book is not available.', 'danger')
    return render_template('transactions/issue.html', form=form)


# Return Book Route
@app.route('/return_book', methods=['GET', 'POST'])
@login_required
def return_book():
    form = ReturnForm()
    if form.validate_on_submit():
        transaction = Transaction.query.filter_by(
            user_id=current_user.id,
            book_id=form.book_id.data,
            actual_return_date=None
        ).first()
        if transaction:
            transaction.actual_return_date = datetime.utcnow()
            transaction.calculate_fine()
            book = Book.query.get(transaction.book_id)
            book.return_book()
            db.session.commit()
            flash(f'Book "{book.title}" returned successfully!', 'success')
            return redirect(url_for('pay_fine', transaction_id=transaction.id))
        flash('Invalid return request.', 'danger')
    return render_template('transactions/return.html', form=form)


# Pay Fine Route
@app.route('/pay_fine/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def pay_fine(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    form = FinePaymentForm()
    if form.validate_on_submit():
        if form.fine_paid.data:
            transaction.fine = 0
            db.session.commit()
            flash('Fine paid successfully!', 'success')
        else:
            flash('Fine payment is required to complete return.', 'danger')
        return redirect(url_for('index'))
    return render_template('transactions/fine_payment.html', form=form, transaction=transaction)


# Manage Memberships Route (Admin Only)
@app.route('/manage_memberships')
@login_required
def manage_memberships():
    if not current_user.is_admin():
        flash('Access Denied', 'danger')
        return redirect(url_for('index'))
    memberships = Membership.query.all()
    return render_template('maintenance/manage_memberships.html', memberships=memberships)


# Add Book Route (Admin Only)
@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if not current_user.is_admin():
        flash('Access Denied', 'danger')
        return redirect(url_for('index'))
    form = BookForm()
    if form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            category=form.category.data,
            copies_total=form.copies.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('manage_books'))
    return render_template('maintenance/add_book.html', form=form)


# Manage Books Route (Admin Only)
@app.route('/manage_books')
@login_required
def manage_books():
    if not current_user.is_admin():
        flash('Access Denied', 'danger')
        return redirect(url_for('index'))
    books = Book.query.all()
    return render_template('maintenance/manage_books.html', books=books)


# Main Block to Run the App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=Config.DEBUG)
