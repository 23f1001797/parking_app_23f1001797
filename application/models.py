from .database import db
from flask_security import UserMixin, RoleMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String, unique = True, nullable = False)
    username = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)
    fs_uniquifier = db.Column(db.String, uniqui= True, nullabe = False)
    active = db.Column(db.Boolean, default = True)
    roles = db.relationship('Role', secondary = 'user_roles', backref = 'bearer')
    reservations = db.relationship('Reservation', backref = 'bearer')

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique = True, nullable = False)
    description = db.Column(db.String)

class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable = False)

class ParkingLot(db.Model):
    id = db.column(db.Integer, primary_key = True)
    pl_name = db.Column(db.String, nullable = False)
    price = db.Column(db.Integer, nullable = False, default = 1000)
    address = db.Column(db.String, nullable = False)
    pincode = db.Column(db.Integer, nullable = False)
    capacity = db.Column(db.Integer, nullable = False)
    spots_count = db.Column(db.Integer, nullable = False)
    created_at = db.Column(db.DateTime, nullabe = False)
    spots = db.relationship('ParkingSpot', backref = 'lot', cascade = 'all, delete')

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable = False)
    status = db.Column(db.String, nullable = False, default = 'available')
    reservations = db.relationship('Reservation', backref = 'spot', cascade = 'all, delete')

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullabe=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    vrn = db.Column(db.String, nullable = False)
    parking_timestamp = db.Column(db.DateTime, nullable = False)
    leaving_timestamp = db.Column(db.DateTime, nullable = True)
    duration = db.Column(db.String, nullable = True)
    status = db.Column(db.String, nullable = False, default = 'unpaid')
    parking_cost = db.Column(db.Integer, nullable = False, default = 0)
