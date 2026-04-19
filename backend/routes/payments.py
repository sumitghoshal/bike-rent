import uuid, random
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

from config.database import get_db
from models.schemas  import payment_schema
from models.helpers  import serial, serial_list, oid

payments_bp = Blueprint('payments', __name__)


# ── Process Payment  (mock/simulation) ───────────────────────────
@payments_bp.route('/process', methods=['POST'])
@jwt_required()
def process_payment():
    data = request.get_json(silent=True) or {}
    uid  = get_jwt_identity()

    booking_id = data.get('booking_id', '').strip()
    method     = data.get('method', 'card')

    if not booking_id:
        return jsonify({'error': 'booking_id is required'}), 400
    if method not in ('card', 'upi', 'wallet'):
        return jsonify({'error': 'method must be card, upi or wallet'}), 400

    db = get_db()
    try:
        bk = db.bookings.find_one({'_id': oid(booking_id)})
    except ValueError:
        return jsonify({'error': 'Invalid booking ID'}), 400
    if not bk:
        return jsonify({'error': 'Booking not found'}), 404
    if bk['user_id'] != uid:
        return jsonify({'error': 'Unauthorized'}), 403
    if bk.get('payment_status') == 'paid':
        return jsonify({'error': 'This booking is already paid'}), 400

    # Simulate payment — 92 % success rate
    success    = random.random() < 0.92
    txn_id     = uuid.uuid4().hex[:16].upper()
    amount     = bk['total_amount']

    # Service fee (5%) + GST (18%)
    service    = round(amount * 0.05, 2)
    gst        = round(amount * 0.18, 2)
    grand      = round(amount + service + gst, 2)

    pmt = payment_schema(booking_id, uid, grand, method)
    pmt['transaction_id'] = txn_id if success else None
    pmt['status']         = 'success' if success else 'failed'
    pmt['breakdown']      = {'base': amount, 'service_fee': service, 'gst': gst}
    pmt['card_last4']     = data.get('card_last4', '****')

    result = db.payments.insert_one(pmt)

    if success:
        db.bookings.update_one(
            {'_id': oid(booking_id)},
            {'$set': {
                'payment_status': 'paid',
                'payment_id':     str(result.inserted_id),
                'status':         'confirmed',
                'updated_at':     datetime.utcnow(),
            }}
        )

    return jsonify({
        'success':        success,
        'transaction_id': txn_id if success else None,
        'message':        ('Payment successful! Booking confirmed.' if success
                           else 'Payment failed. Please try again.'),
        'amount':         grand,
        'method':         method,
    })


# ── Payment History ───────────────────────────────────────────────
@payments_bp.route('/history', methods=['GET'])
@jwt_required()
def payment_history():
    db  = get_db()
    uid = get_jwt_identity()
    pmts = list(db.payments.find({'user_id': uid}).sort('created_at', -1))
    return jsonify(serial_list(pmts))
