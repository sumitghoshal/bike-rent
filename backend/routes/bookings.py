from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

from config.database import get_db
from models.schemas  import booking_schema
from models.helpers  import serial, serial_list, oid

bookings_bp = Blueprint('bookings', __name__)


def _serialize_booking(bk: dict) -> dict:
    """Serialize booking and convert datetime objects."""
    return serial(bk)


def _attach_bike_info(bk: dict, db) -> dict:
    """Attach bike name, brand, type, image to booking dict."""
    bike = db.bikes.find_one({'_id': oid(bk['bike_id'])},
                             {'name': 1, 'brand': 1, 'type': 1, 'image': 1})
    if bike:
        bk['bike_name']  = bike.get('name', '')
        bk['bike_brand'] = bike.get('brand', '')
        bk['bike_type']  = bike.get('type', '')
        bk['bike_image'] = bike.get('image')
    return bk


# ── Create Booking ────────────────────────────────────────────────
@bookings_bp.route('/', methods=['POST'])
@jwt_required()
def create_booking():
    data = request.get_json(silent=True) or {}
    uid  = get_jwt_identity()

    for f in ('bike_id', 'start_time', 'end_time', 'pickup_location'):
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400

    # Parse datetimes
    try:
        start_dt = datetime.fromisoformat(
            data['start_time'].replace('Z', '+00:00')
        ).replace(tzinfo=None)
        end_dt = datetime.fromisoformat(
            data['end_time'].replace('Z', '+00:00')
        ).replace(tzinfo=None)
    except ValueError:
        return jsonify({'error': 'Invalid datetime format. Use ISO 8601.'}), 400

    if end_dt <= start_dt:
        return jsonify({'error': 'end_time must be after start_time'}), 400

    # FIX: skip strict past-date check — client already validates this
    # and server timezone may differ from user timezone causing false rejections

    db = get_db()

    # Validate bike
    try:
        bike = db.bikes.find_one({'_id': oid(data['bike_id'])})
    except ValueError:
        return jsonify({'error': 'Invalid bike ID'}), 400
    if not bike:
        return jsonify({'error': 'Bike not found'}), 404
    if not bike.get('is_available', True):
        return jsonify({'error': 'Bike is currently unavailable'}), 400

    # Overlap check
    conflict = db.bookings.find_one({
        'bike_id': data['bike_id'],
        'status':  {'$in': ['confirmed', 'active']},
        '$or': [{'start_time': {'$lt': end_dt}, 'end_time': {'$gt': start_dt}}],
    })
    if conflict:
        return jsonify({'error': 'Bike already booked for this time slot'}), 409

    # Cost calculation
    hours = (end_dt - start_dt).total_seconds() / 3600
    if hours < 0.5:
        return jsonify({'error': 'Minimum booking duration is 30 minutes'}), 400

    if hours >= 24:
        days   = max(1, int((end_dt - start_dt).days))
        amount = days * bike['price_per_day']
    else:
        amount = hours * bike['price_per_hour']

    bk = booking_schema(
        user_id=uid, bike_id=data['bike_id'],
        vendor_id=bike.get('vendor_id', ''),
        start_time=start_dt, end_time=end_dt,
        total_hours=hours, total_amount=amount,
        pickup_location=data['pickup_location'],
        notes=data.get('notes', ''),
    )
    result = db.bookings.insert_one(bk)
    bk['_id'] = result.inserted_id
    return jsonify({'message': 'Booking created successfully',
                    'booking': serial(bk)}), 201


# ── My Bookings ───────────────────────────────────────────────────
@bookings_bp.route('/my', methods=['GET'])
@jwt_required()
def my_bookings():
    db     = get_db()
    uid    = get_jwt_identity()
    status = request.args.get('status', '')

    query = {'user_id': uid}
    if status:
        query['status'] = status

    bks = list(db.bookings.find(query).sort('created_at', -1))
    result = []
    for bk in bks:
        bk = serial(bk)
        bk = _attach_bike_info(bk, db)
        result.append(bk)
    return jsonify(result)


# ── Single Booking ────────────────────────────────────────────────
@bookings_bp.route('/<booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    db  = get_db()
    uid = get_jwt_identity()
    u   = db.users.find_one({'_id': oid(uid)})

    try:
        bk = db.bookings.find_one({'_id': oid(booking_id)})
    except ValueError:
        return jsonify({'error': 'Invalid booking ID'}), 400
    if not bk:
        return jsonify({'error': 'Booking not found'}), 404

    # Access control
    role = u.get('role', 'user')
    if role == 'user'   and bk['user_id']   != uid:
        return jsonify({'error': 'Unauthorized'}), 403
    if role == 'vendor' and bk['vendor_id'] != uid:
        return jsonify({'error': 'Unauthorized'}), 403

    bk = serial(bk)
    # Attach full bike object
    bike = db.bikes.find_one({'_id': oid(bk['bike_id'])})
    if bike:
        bk['bike'] = serial(bike)
    return jsonify(bk)


# ── Cancel ────────────────────────────────────────────────────────
@bookings_bp.route('/<booking_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_booking(booking_id):
    db  = get_db()
    uid = get_jwt_identity()

    try:
        bk = db.bookings.find_one({'_id': oid(booking_id)})
    except ValueError:
        return jsonify({'error': 'Invalid booking ID'}), 400
    if not bk:
        return jsonify({'error': 'Booking not found'}), 404
    if bk['user_id'] != uid:
        return jsonify({'error': 'Unauthorized'}), 403
    if bk['status'] in ('completed', 'cancelled'):
        return jsonify({'error': f'Cannot cancel a {bk["status"]} booking'}), 400

    db.bookings.update_one(
        {'_id': oid(booking_id)},
        {'$set': {'status': 'cancelled', 'updated_at': datetime.utcnow()}}
    )
    return jsonify({'message': 'Booking cancelled successfully'})


# ── Update Status  (vendor / admin) ──────────────────────────────
@bookings_bp.route('/<booking_id>/status', methods=['PUT'])
@jwt_required()
def update_status(booking_id):
    db  = get_db()
    uid = get_jwt_identity()
    u   = db.users.find_one({'_id': oid(uid)})

    if u.get('role') not in ('vendor', 'admin'):
        return jsonify({'error': 'Vendor or Admin access required'}), 403

    data       = request.get_json(silent=True) or {}
    new_status = data.get('status', '')
    valid      = ('pending', 'confirmed', 'active', 'completed', 'cancelled')
    if new_status not in valid:
        return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid)}'}), 400

    try:
        bk = db.bookings.find_one({'_id': oid(booking_id)})
    except ValueError:
        return jsonify({'error': 'Invalid booking ID'}), 400
    if not bk:
        return jsonify({'error': 'Booking not found'}), 404

    db.bookings.update_one(
        {'_id': oid(booking_id)},
        {'$set': {'status': new_status, 'updated_at': datetime.utcnow()}}
    )
    if new_status == 'completed':
        db.bikes.update_one(
            {'_id': oid(bk['bike_id'])},
            {'$inc': {'total_bookings': 1}}
        )
    return jsonify({'message': f'Status updated to {new_status}'})
