from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

from config.database import get_db
from models.helpers  import serial, serial_list, oid

admin_bp = Blueprint('admin', __name__)


def _require_admin(db, uid: str):
    u = db.users.find_one({'_id': oid(uid)})
    if not u or u.get('role') != 'admin':
        return None
    return u


# ── Platform Stats ────────────────────────────────────────────────
@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    db  = get_db()
    uid = get_jwt_identity()
    if not _require_admin(db, uid):
        return jsonify({'error': 'Admin access required'}), 403

    # Revenue aggregation
    rev_pipeline = [
        {'$match': {'status': 'success'}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}},
    ]
    rev_result = list(db.payments.aggregate(rev_pipeline))
    revenue    = rev_result[0]['total'] if rev_result else 0

    return jsonify({
        'total_users':    db.users.count_documents({'role': 'user'}),
        'total_vendors':  db.users.count_documents({'role': 'vendor'}),
        'total_bikes':    db.bikes.count_documents({}),
        'available_bikes': db.bikes.count_documents({'is_available': True}),
        'total_bookings': db.bookings.count_documents({}),
        'active_bookings': db.bookings.count_documents(
            {'status': {'$in': ['active', 'confirmed']}}
        ),
        'pending_kyc':    db.users.count_documents(
            {'kyc_status': 'pending', 'license_image': {'$ne': None}}
        ),
        'total_revenue':  round(revenue, 2),
    })


# ── All Users ─────────────────────────────────────────────────────
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    db  = get_db()
    uid = get_jwt_identity()
    if not _require_admin(db, uid):
        return jsonify({'error': 'Admin access required'}), 403

    users = list(db.users.find({}, {'password': 0}).sort('created_at', -1))
    return jsonify(serial_list(users))


# ── Approve / Reject KYC ─────────────────────────────────────────
@admin_bp.route('/kyc/<target_id>', methods=['PUT'])
@jwt_required()
def update_kyc(target_id):
    db  = get_db()
    uid = get_jwt_identity()
    if not _require_admin(db, uid):
        return jsonify({'error': 'Admin access required'}), 403

    data   = request.get_json(silent=True) or {}
    status = data.get('status', '')
    if status not in ('approved', 'rejected'):
        return jsonify({'error': 'status must be "approved" or "rejected"'}), 400

    try:
        result = db.users.update_one(
            {'_id': oid(target_id)},
            {'$set': {'kyc_status': status, 'updated_at': datetime.utcnow()}}
        )
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400

    if result.matched_count == 0:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': f'KYC {status} successfully'})


# ── Toggle User Active / Suspended ───────────────────────────────
@admin_bp.route('/users/<target_id>/toggle', methods=['PUT'])
@jwt_required()
def toggle_user(target_id):
    db  = get_db()
    uid = get_jwt_identity()
    if not _require_admin(db, uid):
        return jsonify({'error': 'Admin access required'}), 403

    try:
        user = db.users.find_one({'_id': oid(target_id)})
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400
    if not user:
        return jsonify({'error': 'User not found'}), 404

    new_state = not user.get('is_active', True)
    db.users.update_one(
        {'_id': oid(target_id)},
        {'$set': {'is_active': new_state, 'updated_at': datetime.utcnow()}}
    )
    action = 'activated' if new_state else 'suspended'
    return jsonify({'message': f'User {action}', 'is_active': new_state})


# ── All Bookings ──────────────────────────────────────────────────
@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
def all_bookings():
    db  = get_db()
    uid = get_jwt_identity()
    if not _require_admin(db, uid):
        return jsonify({'error': 'Admin access required'}), 403

    status = request.args.get('status', '')
    query  = {}
    if status:
        query['status'] = status

    bks    = list(db.bookings.find(query).sort('created_at', -1).limit(200))
    result = []
    for bk in bks:
        bk   = serial(bk)
        bike = db.bikes.find_one({'_id': oid(bk['bike_id'])}, {'name': 1})
        user = db.users.find_one({'_id': oid(bk['user_id'])}, {'name': 1})
        if bike: bk['bike_name'] = bike.get('name', '')
        if user: bk['user_name'] = user.get('name', '')
        result.append(bk)
    return jsonify(result)


# ── All Payments ──────────────────────────────────────────────────
@admin_bp.route('/payments', methods=['GET'])
@jwt_required()
def all_payments():
    db  = get_db()
    uid = get_jwt_identity()
    if not _require_admin(db, uid):
        return jsonify({'error': 'Admin access required'}), 403

    pmts = list(db.payments.find({}).sort('created_at', -1).limit(100))
    return jsonify(serial_list(pmts))
