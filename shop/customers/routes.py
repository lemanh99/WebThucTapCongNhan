from flask import render_template, session, request, redirect, url_for, flash, current_app, make_response
from flask_login import login_required, current_user, logout_user, login_user
from shop import app, db, photos, bcrypt
from .forms import CustomerRegisterForm, CustomerLoginFrom
from .models import Register, CustomerOrder
from shop.products.models import Category, Brand, Addproduct
import secrets
import os
import json


# import pdfkit
# import stripe

def brands():
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    return brands


def categories():
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return categories


@app.route('/myaccount', methods=['GET', 'POST'])
@login_required
def update_account():
    detail_customer = Register.query.get_or_404(current_user.id)
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    email = request.form.get('email')
    phone_number = request.form.get('phone')
    gender = request.form.get('gender')
    if request.method == "POST":
        if detail_customer.email != email:
            if Register.query.filter_by(email=email).first():
                flash(f'Email Used!', 'danger')
                return redirect(url_for('update_account'))
        if detail_customer.phone_number != phone_number:
            if Register.query.filter_by(phone_number=phone_number).first():
                flash(f'Phone Number Used!', 'danger')
                return redirect(url_for('update_account'))
        detail_customer.first_name = first_name
        detail_customer.last_name = last_name
        detail_customer.email = email
        detail_customer.phone_number = phone_number
        detail_customer.gender = gender
        flash(f'Information change complete!', 'success')
        db.session.commit()
        return redirect(url_for('update_account'))
    return render_template('customers/myaccount.html', detail_customer=detail_customer, brands=brands(),
                           categories=categories())


@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_password():
    detail_password_customer = Register.query.get_or_404(current_user.id)
    old_password = request.form.get('oldpassword')
    new_password = request.form.get('newpassword')
    if request.method == "POST":
        if not bcrypt.check_password_hash(detail_password_customer.password, old_password):
            flash(f'Old passwords do not match!', 'danger')
            return redirect(url_for('change_password'))

        detail_password_customer.password = bcrypt.generate_password_hash(new_password)
        flash(f'Change Password Complete!', 'success')
        db.session.commit()
        return redirect(url_for('change_password'))
    return render_template('customers/myaccount.html', detail_password_customer=detail_password_customer,
                           brands=brands(),
                           categories=categories())


@app.route('/register', methods=['GET', 'POST'])
def customer_register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(username=form.username.data, email=form.email.data, first_name=form.first_name.data,
                            last_name=form.last_name.data, phone_number=form.phone_number.data, gender=form.gender.data,
                            password=hash_password)
        db.session.add(register)
        flash(f'Welcome {form.first_name.data} {form.last_name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('customer_login'))
    return render_template('customers/register.html', form=form, brands=brands(), categories=categories())


@app.route('/login', methods=['GET', 'POST'])
def customer_login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        user = Register.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect email and password', 'danger')
        return redirect(url_for('customer_login'))
    return render_template('customers/login.html', form=form, brands=brands(), categories=categories())


@app.route('/logout')
@login_required
def customer_logout():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    logout_user()
    return redirect(url_for('home'))

#from Danh
#code payment
@app.route('/getorder')
@login_required
#connect from carts.html, call func get_order
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        # for key, item in session['Shoppingcart'].items():
        #     if int(key) == id:
        #         routes.deleteitem(id)
        # routes.clearcart()
        try:
            order =CustomerOrder(invoice=invoice,customer_id=customer_id,orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            #session.pop('Shoppingcart')
            print("done")
            return redirect(url_for('orders',invoice=invoice))
        except Exception as e:
            print("failsrun")
            print(e)
            return redirect(url_for('getCart'))

@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        total = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        subtotals = 0
        discounttotal = 0
        for key, product in session['Shoppingcart'].items():
            discounttotal += (product['discount'] / 100) * float(product['price']) * int(product['quantity'])
            subtotals += float(product['price']) * int(product['quantity'])
            subtotals -= discounttotal
    else:
        return redirect(url_for('customer_login'))
    return render_template('customers/order.html', invoice=invoice, subtotals=subtotals, customer=customer, orders=orders)

# @app.route('/payment',methods=['POST'])
# def payment():
#     invoice = request.get('invoice')
#     amount = request.form.get('amount')
#     customer = stripe.Customer.create(
#       email=request.form['stripeEmail'],
#       source=request.form['stripeToken'],
#     )
#     charge = stripe.Charge.create(
#       customer=customer.id,
#       description='Payment',
#       amount=amount,
#       currency='USD',
#     )
#     orders = CustomerOrder.query.filter_by(customer_id = current_user.id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
#     orders.status = 'Paid'
#     db.session.commit()
#     return redirect(url_for('thanks'))

@app.route('/submit_order',methods=['POST'])
def submit_order():
     if current_user.is_authenticated:
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()

        return render_template('customers/thanks_submit.html', orders=orders)
#end Danh