from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from config.database import get_db
from models.helpers  import serial, serial_list, oid

vendor_bp = Blueprint('vendor', __name__)


def _require_vendor(db, uid: str):
    u = db.users.find_one({'_id': oid(uid)})
    if not u or u.get('role') not in ('vendor', 'admin'):
        return None
    return u


# ── Dashboard Stats ───────────────────────────────────────────────
@vendor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    db  = get_db()
    uid = get_jwt_identity()
    if not _require_vendor(db, uid):
        return jsonify({'error': 'Vendor access required'}), 403

    total_bikes    = db.bikes.count_documents({'vendor_id': uid})
    avail_bikes    = db.bikes.count_documents({'vendor_id': uid, 'is_available': True})
    total_bookings = db.bookings.count_documents({'vendor_id': uid})
    active_bks     = db.bookings.count_documents(
        {'vendor_id': uid, 'status': {'$in': ['active', 'confirmed']}}
    )

    # Revenue from paid bookings
    pipeline = [
        {'$match': {'vendor_id': uid, 'payment_status': 'paid'}},
        {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}},
    ]
    rev_result = list(db.bookings.aggregate(pipeline))
    revenue    = rev_result[0]['total'] if rev_result else 0

    return jsonify({
        'total_bikes':    total_bikes,
        'available_bikes': avail_bikes,
        'total_bookings': total_bookings,
        'active_bookings': active_bks,
        'total_revenue':  round(revenue, 2),
    })


# ── Vendor's Bikes ────────────────────────────────────────────────
@vendor_bp.route('/bikes', methods=['GET'])
@jwt_required()
def vendor_bikes():
    db  = get_db()
    uid = get_jwt_identity()
    if not _require_vendor(db, uid):
        return jsonify({'error': 'Vendor access required'}), 403

    bikes = list(db.bikes.find({'vendor_id': uid}).sort('created_at', -1))
    return jsonify(serial_list(bikes))


# ── Vendor's Bookings ─────────────────────────────────────────────
@vendor_bp.route('/bookings', methods=['GET'])
@jwt_required()
def vendor_bookings():
    db     = get_db()
    uid    = get_jwt_identity()
    if not _require_vendor(db, uid):
        return jsonify({'error': 'Vendor access required'}), 403

    status = request.args.get('status', '')
    query  = {'vendor_id': uid}
    if status:
        query['status'] = status

    bks    = list(db.bookings.find(query).sort('created_at', -1))
    result = []
    for bk in bks:
        bk = serial(bk)
        bike = db.bikes.find_one({'_id': oid(bk['bike_id'])}, {'name': 1, 'image': 1})
        user = db.users.find_one({'_id': oid(bk['user_id'])}, {'name': 1, 'phone': 1})
        if bike:
            bk['bike_name']  = bike.get('name', '')
            bk['bike_image'] = bike.get('image')
        if user:
            bk['user_name']  = user.get('name', '')
            bk['user_phone'] = user.get('phone', '')
        result.append(bk)
    return jsonify(result)
