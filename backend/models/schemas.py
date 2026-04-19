"""
MongoDB document schemas.
All _id fields use MongoDB's ObjectId (auto-generated).
Datetime fields stored as Python datetime objects (MongoDB BSON native).
"""
from datetime import datetime


def user_schema(name: str, email: str, password_hash: str,
                phone: str = '', role: str = 'user') -> dict:
    return {
        'name':          name.strip(),
        'email':         email.lower().strip(),
        'password':      password_hash,
        'phone':         phone.strip(),
        'role':          role,           # 'user' | 'vendor' | 'admin'
        'avatar':        None,
        'license_image': None,
        'kyc_status':    'pending',      # 'pending' | 'approved' | 'rejected'
        'is_active':     True,
        'created_at':    datetime.utcnow(),
        'updated_at':    datetime.utcnow(),
    }


def bike_schema(vendor_id: str, name: str, type_: str, brand: str,
                model: str, year: int, price_per_hour: float,
                price_per_day: float, location: str,
                description: str = '', image: str = None) -> dict:
    return {
        'vendor_id':      str(vendor_id),
        'name':           name.strip(),
        'type':           type_,         # mountain|road|electric|city|hybrid
        'brand':          brand.strip(),
        'model':          model.strip(),
        'year':           int(year),
        'price_per_hour': float(price_per_hour),
        'price_per_day':  float(price_per_day),
        'location':       location.strip(),
        'description':    description.strip(),
        'image':          image,
        'features':       [],
        'is_available':   True,
        'rating':         0.0,
        'total_reviews':  0,
        'total_bookings': 0,
        'created_at':     datetime.utcnow(),
        'updated_at':     datetime.utcnow(),
    }


def booking_schema(user_id: str, bike_id: str, vendor_id: str,
                   start_time: datetime, end_time: datetime,
                   total_hours: float, total_amount: float,
                   pickup_location: str, notes: str = '') -> dict:
    return {
        'user_id':         str(user_id),
        'bike_id':         str(bike_id),
        'vendor_id':       str(vendor_id),
        'start_time':      start_time,
        'end_time':        end_time,
        'total_hours':     round(float(total_hours), 2),
        'total_amount':    round(float(total_amount), 2),
        'pickup_location': pickup_location.strip(),
        'notes':           notes.strip(),
        'status':          'pending',    # pending|confirmed|active|completed|cancelled
        'payment_status':  'unpaid',     # unpaid|paid|refunded
        'payment_id':      None,
        'created_at':      datetime.utcnow(),
        'updated_at':      datetime.utcnow(),
    }


def review_schema(user_id: str, bike_id: str, booking_id: str,
                  rating: int, comment: str) -> dict:
    return {
        'user_id':    str(user_id),
        'bike_id':    str(bike_id),
        'booking_id': str(booking_id),
        'rating':     int(rating),       # 1–5
        'comment':    comment.strip(),
        'created_at': datetime.utcnow(),
    }


def payment_schema(booking_id: str, user_id: str,
                   amount: float, method: str) -> dict:
    return {
        'booking_id':     str(booking_id),
        'user_id':        str(user_id),
        'amount':         round(float(amount), 2),
        'method':         method,        # card|upi|wallet
        'status':         'pending',     # pending|success|failed
        'transaction_id': None,
        'created_at':     datetime.utcnow(),
    }
