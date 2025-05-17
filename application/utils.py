from .models import ParkingSpot
from datetime import datetime

def roles_list(roles):
    return [role.name for role in roles]

def get_reserved_spots_count(lot_id):
    return ParkingSpot.query.filter_by(lot_id = lot_id, status = "occupied").count()

def get_duration(parking_timestamp):
    current_time = datetime.now()
    duration = current_time - parking_timestamp

    duration_in_seconds = int(duration.total_seconds())
    duration_in_min = duration_in_seconds//60
    duration_in_hr = round(duration_in_min/60, 2)
    duration_min = duration_in_min % 60
    duration_hr = duration_in_min // 60

    return {
        "duration_in_seconds": duration_in_seconds,
        "duration_in_min": duration_in_min,
        "duration_in_hr": duration_in_hr,
        "duration_min": duration_min,
        "duration_hr": duration_hr
    }