from flask_restful import Resource, Api, reqparse, fields, marshal
from flask_security import auth_required, current_user, roles_required
from datetime import datetime

from .models import ParkingLot, ParkingSpot
from .database import db
from .utils import get_reserved_spots_count

api = Api()

parking_lot_fields = {
    'id': fields.Integer,
    'pl_name': fields.String,
    'price': fields.Integer,
    'address': fields.String,
    'capacity': fields.Integer,
    'spots_count': fields.Integer,
    'created_at': fields.DateTime
}

class ParkingLotApi(Resource):
    def __init__(self):
        self.lot_args = reqparse.RequestParser()
        self.lot_args.add_argument('pl_name')
        self.lot_args.add_argument('price')
        self.lot_args.add_argument('address')
        self.lot_args.add_argument('pincode')
        self.lot_args.add_argument('capacity')

    @auth_required('token')
    @roles_required('admin')
    def get(self, lot_id=None):

        if lot_id:
            parking_lot = ParkingLot.query.get(lot_id)
            if parking_lot:
                return marshal(parking_lot, parking_lot_fields)
            return {"message": "parking lot not found"}

        parking_lots = ParkingLot.query.all()
        if parking_lots:
            return marshal(parking_lots, parking_lot_fields)
        
        return {
            'message': 'No parking lots found'
        }, 404

    @auth_required('token')
    @roles_required('admin')
    def post(self):
        args = self.lot_args.parse_args()
        try:
            parking_lot = ParkingLot(
                pl_name = args['pl_name'],
                price = args['price'],
                address = args['address'],
                pincode = args['pincode'],
                created_at = datetime.now(),
                capacity = args['capacity'],
                spots_count = args['capacity'],
            )
            db.session.add(parking_lot)
            db.session.flush()

            for i in range(int(parking_lot.spots_count)):
                spot = ParkingSpot(lot_id = parking_lot.id)
                db.session.add(spot)
            db.session.commit()
            return {
                'message': 'parking lot created successfully'
            }, 201
        except:
            return {
                'message': 'Error creating parking lot'
            }, 400
    
    @auth_required('token')
    @roles_required('admin')
    def put(self, lot_id):
        args = self.lot_args.parse_args()
        try:
            parking_lot = ParkingLot.query.get(lot_id)
            parking_lot.pl_name = args['pl_name']
            parking_lot.price = args['price']
            parking_lot.address = args['address']
            parking_lot.pincode = args['pincode']
            db.session.commit()
            return {
                'message': 'parking lot updated successfully'
            }, 200
        except:
            return {
                'message': 'Error updating parking lot'
            }, 400
    
    @auth_required('token')
    @roles_required('admin')
    def delete(self, lot_id):
        try:
            parking_lot = ParkingLot.query.get(lot_id)

            if parking_lot:
                occupied_spots = get_reserved_spots_count(lot_id)
                if occupied_spots > 0:
                    return {
                        'message': 'cannot delete parking lot with occupied spots'
                    }, 400

                spots = ParkingSpot.query.filter_by(lot_id = lot_id).all()
                
                for spot in spots:
                    db.session.delete(spot)
                db.session.delete(parking_lot)
                db.session.commit()
                return {
                    'message': 'parking lot deleted successfully'
                }, 200
            if not parking_lot:
                return {
                    'message' : 'parking lot not found'
                }, 404
                
        except:
            return {
                'message': 'Error deleting parking lot'
            }, 400


api.add_resource(ParkingLotApi, '/api/parking_lot', '/api/parking_lot/<int:lot_id>')