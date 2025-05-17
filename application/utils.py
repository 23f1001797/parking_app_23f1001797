from .models import ParkingSpot

def roles_list(roles):
    return [role.name for role in roles]

def get_reserved_spots_count(lot_id):
    return ParkingSpot.query.filter_by(lot_id = lot_id, status = "occupied").count()