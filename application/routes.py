from flask import current_app as app, render_template, request, url_for, redirect, flash
from flask_security import current_user, roles_accepted, roles_required, auth_required, logout_user, login_user, hash_password, verify_password
from sqlalchemy import func, or_
from datetime import datetime

from .models import *
from .utils import *

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not email or not username or not password or not confirm_password:
            flash("please fill all the fields", "danger")
            return redirect(url_for('user_register'))
        
        if password != confirm_password:
            flash("password do not match", "danger")
            return redirect(url_for('user_register'))
        
        if app.security.datastore.find_user(email=email):
            flash("Email already exists", "danger")
            return redirect(url_for('user_register'))
        
        if app.security.datastore.find_user(username = username):
            flash("Username already exists", "danger")
        
        app.security.datastore.create_user(
            email = email,
            username = username,
            password = hash_password(password),
            roles = ['user']
        )
        db.session.commit()
        flash("User registered successfully", "success")
        return redirect(url_for('user_login'))
    
    else:
        return render_template('register.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('please fill all the fields', "danger")
            return redirect(url_for('user_login'))

        user = app.security.datastore.find_user(email = email)
        if user and verify_password(password, user.password):
            login_user(user)
            if "admin" in roles_list(user.roles):
                return redirect(url_for('admin_dashboard'))
            else: 
                return redirect(url_for('user_dashboard'))
        else:
            flash("Invallid credentials", "danger")
            return redirect(url_for('user_login'))
    else: 
        return render_template('security/login_user.html')

####################################################################################

                              # ADMIN ROUTES #

####################################################################################

@app.route('/admin/dashboard')
def admin_dashboard():
    lots = ParkingLot.query.all()
    return render_template('admin_dashboard.html', lots=lots)



#####################################################################################

                              # USER ROUTES #

#####################################################################################

@app.route('/user/dashboard')
def user_dashboard():
    user = current_user
    reservations = Reservation.query.filter_by(user_id = user.id).all()
    return render_template('user_dashboard.html', reservations=reservations)
