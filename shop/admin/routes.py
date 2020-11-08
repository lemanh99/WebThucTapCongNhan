from itertools import product

from flask import render_template, session, redirect, request, url_for, flash, session

from shop import app, db, bcrypt
from .form import RegistrationForm, LoginForm, CustomerRegisterForm
from .models import Admin
from shop.customers.models import Register, CustomerOrder
from shop.products.models import Addproduct, Brand, Category


@app.route('/admin/customer_register', methods=['GET', 'POST'])
def admin_register_custormer():
    if 'email' not in session:
        flash(f'please login first', 'danger')
        return redirect(url_for('login'))
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(username=form.username.data, email=form.email.data, first_name=form.first_name.data,
                            last_name=form.last_name.data, phone_number=form.phone_number.data, gender=form.gender.data,
                            password=hash_password)
        db.session.add(register)
        flash(f'Welcome {form.first_name.data} {form.last_name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('admin_register_custormer'))
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('admin/customer_register.html', form=form, user=user[0])


@app.route('/admin')
def admin():
    if 'email' not in session:
        flash(f'please login first', 'danger')
        return redirect(url_for('login'))
    return redirect(url_for('admin_manager'))


@app.route('/admin_manager')
def admin_manager():
    if 'email' not in session:
        flash(f'please login first', 'danger')
        return redirect(url_for('login'))
    user = Admin.query.filter_by(email=session['email']).all()
    admins = Admin.query.all()
    return render_template('admin/admin-manager.html', title='Admin manager page', user=user[0], admins=admins)


@app.route('/customer_manager')
def customer_manager():
    if 'email' not in session:
        flash(f'please login first', 'danger')
        return redirect(url_for('login'))
    user = Admin.query.filter_by(email=session['email']).all()
    customers = Register.query.all()
    return render_template('admin/customer_manager.html', title='Customer manager page', user=user[0],
                           customers=customers)


@app.route('/admin/orders')
def orders():
    if 'email' not in session:
        flash(f'please login first', 'danger')
        return redirect(url_for('login'))
    user = Admin.query.filter_by(email=session['email']).all()
    orders = CustomerOrder.query.all()
    return render_template('admin/orders.html', title='Order manager page', user=user[0], orders=orders)


@app.route('/accept_order/<int:id>', methods=['GET', 'POST'])
def accept_order(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    customer = CustomerOrder.query.get_or_404(id)
    if request.method == "POST":
        customer.status = 'Accepted'
        db.session.commit()
        return redirect(url_for('orders'))
    return redirect(url_for('orders'))


@app.route('/delete_order/<int:id>', methods=['GET', 'POST'])
def delete_order(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    customer = CustomerOrder.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(customer)
        db.session.commit()
        return redirect(url_for('orders'))
    return redirect(url_for('orders'))


@app.route('/lock_customer/<int:id>', methods=['GET', 'POST'])
def lock_customer(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    customer = Register.query.get_or_404(id)
    if request.method == "POST":
        customer.lock = 1
        db.session.commit()
        return redirect(url_for('customer_manager'))
    return redirect(url_for('customer_manager'))


@app.route('/unlock_customer/<int:id>', methods=['GET', 'POST'])
def unlock_customer(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    customer = Register.query.get_or_404(id)
    if request.method == "POST":
        customer.lock = 0
        db.session.commit()
        return redirect(url_for('customer_manager'))
    return redirect(url_for('customer_manager'))


@app.route('/delete_customer/<int:id>', methods=['GET', 'POST'])
def delete_customer(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    customer = Register.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(customer)
        db.session.commit()
        flash(f"The customer {customer.username} was deleted from your database", "success")
        return redirect(url_for('customer_manager'))
    flash(f"The customer {customer.username} can't be  deleted from your database", "warning")
    return redirect(url_for('customer_manager'))


@app.route('/delete_admin/<int:id>', methods=['GET', 'POST'])
def delete_admin(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    admin = Admin.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(admin)
        db.session.commit()
        flash(f"The admin {admin.name} was deleted from your database", "success")
        return redirect(url_for('admin_manager'))
    flash(f"The admin {admin.name} can't be  deleted from your database", "warning")
    return redirect(url_for('admin_manager'))


@app.route('/product')
def product():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    products = Addproduct.query.all()
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('admin/index.html', title='Product page', products=products, user=user[0])


@app.route('/brands')
def brands():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    brands = Brand.query.order_by(Brand.id.desc()).all()
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('admin/brand.html', title='brands', brands=brands, user=user[0])


@app.route('/categories')
def categories():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('admin/brand.html', title='categories', categories=categories, user=user[0])


@app.route('/admin/changepassword', methods=['GET', 'POST'])
def changes_password():
    if 'email' not in session:
        flash(f'please login first', 'danger')
        return redirect(url_for('login'))
    user = Admin.query.filter_by(email=session['email'])
    detail_password_admin = Admin.query.get_or_404(user[0].id)
    old_password = request.form.get('oldpassword')
    new_password = request.form.get('newpassword')
    if request.method == "POST":
        if not bcrypt.check_password_hash(detail_password_admin.password, old_password):
            flash(f'Old passwords do not match!', 'danger')
            return redirect(url_for('changes_password'))
        detail_password_admin.password = bcrypt.generate_password_hash(new_password)
        flash(f'Change Password Complete!', 'success')
        db.session.commit()
        return redirect(url_for('changes_password'))
    return render_template('admin/change_password.html', title='Change Password', user=user[0])


@app.route('/admin/register', methods=['GET', 'POST'])
def register():
    if 'email' not in session:
        flash(f'please login first', 'danger')
        return redirect(url_for('login'))
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = Admin(name=form.name.data, username=form.username.data, email=form.email.data, password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f' Wellcom {form.name.data} Thanks for registering', 'success')
        return redirect(url_for('register'))
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('admin/register.html', form=form, title='Registration page', user=user[0])


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Admin.query.filter_by(email=form.email.data).first()
        print(form.email.data)
        print('user')
        print(user)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'welcome {form.email.data} you are logedin now', 'success')
            return redirect(url_for('admin'))
        else:
            flash(f'Wrong email and password', 'danger')
            return redirect(url_for('login'))
    return render_template('admin/login.html', title='Login page', form=form)


@app.route('/admin/logout')
def logout():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
    else:
        session.pop('email', None)
    return redirect(url_for('login'))
