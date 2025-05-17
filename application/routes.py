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

@app.route('/user_logout')
@auth_required()
def user_logout():
    logout_user()
    return redirect(url_for('user_login'))

####################################################################################

                              # ADMIN ROUTES #

####################################################################################

@app.route('/admin/dashboard')
@auth_required()
@roles_required('admin')
def admin_dashboard():
    lots = ParkingLot.query.all()
    return render_template('admin_dashboard.html', lots=lots)

@app.route('/admin/users')
@auth_required()
@roles_required('admin')
def get_users_data():
    users = (
        db.session.query(User.id, User.username, User.email, User.active, func.count(Reservation.id).label("reservation_count"))
        .outerjoin(Reservation, User.id == Reservation.user_id)
        .group_by(User.id)
        .all()
    )
    return render_template('users.html', users = users[1:])

@app.route('/admin/add_parking_lot', methods=['GET', 'POST'])
@auth_required()
@roles_required('admin')
def create_lot():
    if request.method == 'POST':
        pl_name = request.form.get('pl_name')
        price = request.form.get('price')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        created_at = datetime.now()
        capacity = request.form.get('capacity')

        if not pl_name or not price or not address or not pincode or not capacity:
            flash("please fill all the fields", "danger")
            return redirect(url_for('create_lot'))
        
        parking_lot = ParkingLot(
            pl_name = pl_name,
            price = price,
            address = address,
            pincode = pincode, 
            created_at = created_at,
            capacity = capacity,
            spots_count = capacity
        )
        db.session.add(parking_lot)

        db.session.flush()

        for i in range(int(capacity)):
            spot = ParkingSpot(lot_id = parking_lot.id)
            db.session.add(spot)
        db.session.commit()

        flash("parking lot created successfully", "success")
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('create_lot.html')

@app.route('/admin/view_parking_lot/<int:lot_id>')
@auth_required()
@roles_required('admin')
def view_parking_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    occupied_spots = get_reserved_spots_count(lot.id)
    available_spots = lot.spots_count - occupied_spots
    return render_template('view_lot.html', lot=lot, occupied_spots = occupied_spots, available_spots = available_spots)

@app.route('/admin/edit_parking_lot/<int:lot_id>', methods=['GET', 'POST'])
@auth_required()
@roles_required('admin')
def edit_parking_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if request.method == 'POST':
        pl_name = request.form.get('pl_name')
        price = request.form.get('price')
        address = request.form.get('address')
        pincode = request.form.get('pincode')

        if not pl_name or not price or not address or not pincode:
            flash('please fill all the fields', "danger")
            redirect(url_for('edit_parking_lot', lot_id = lot.id))
        
        lot.pl_name = pl_name
        lot.price = price
        lot.address = address
        lot.pincode = pincode
        db.session.commit()
        flash('parking lot updated successfully', 'success')
        return redirect(url_for('view_parking_lot', lot_id=lot_id))
    else:
        return render_template('edit_lot.html', lot = lot)

@app.route('/admin/delete_parking_lot/<int:lot_id>')
@auth_required()
@roles_required('admin')
def delete_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    occupied_spots = [spot for spot in lot.spots if spot.status.lower() != 'available']

    if occupied_spots:
        flash("cannot delete parking lot. some spots are still occupied.", "danger")
        return redirect(url_for('view_parking_lot', lot_id = lot_id))
    db.session.delete(lot)
    db.session.commit()
    flash("parking lot deleted successfully", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/get_spot/<int:spot_id>')
@auth_required()
@roles_required('admin')
def get_spot(spot_id):
    spot = ParkingSpot.query.get(spot_id)
    if spot.status == "occupied":
        reservation = Reservation.query.filter_by(spot_id = spot.id).order_by(Reservation.id.desc()).first()
        return render_template('spot.html', reservation = reservation)
    return render_template('spot.html', spot = spot)

@app.route('/admin/add_spot/<int:lot_id>')
@auth_required()
@roles_required('admin')
def create_spot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if lot.spots_count < lot.capacity:
        spot = ParkingSpot(lot_id = lot_id)
        lot.spots_count += 1
        db.session.add(spot)
        db.session.commit()
        flash("parking spot added successfully", "success") 
    else:
        flash("parking lot is full", "danger")
    return redirect(url_for('view_parking_lot', lot_id= lot_id))   

@app.route('/admin/delete/spot/<int:spot_id>')
@auth_required()
@roles_required('admin')
def delete_spot(spot_id):
    spot = ParkingSpot.query.get(spot_id)
    if spot.status != 'available':
        flash('cannot delete an occupied spot.', "danger")
        return redirect(url_for('get_spot', spot_id, spot_id))
    spot_lot = ParkingLot.query.get(spot.lot_id)
    spot_lot.spots_count -= 1
    db.session.delete(spot)
    db.session.commit()
    flash('parking spot deleted successfully', 'success')
    return redirect(url_for('view_parking_lot', lot_id = spot.lot_id))


#####################################################################################

                              # USER ROUTES #

#####################################################################################

@app.route('/user/dashboard')
@auth_required()
@roles_required('user')
def user_dashboard():
    user = current_user
    reservations = Reservation.query.filter_by(user_id = user.id).all()
    return render_template('user_dashboard.html', reservations=reservations)
