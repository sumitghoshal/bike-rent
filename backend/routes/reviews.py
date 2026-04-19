from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from config.database import get_db
from models.schemas  import review_schema
from models.helpers  import serial, serial_list, oid

reviews_bp = Blueprint('reviews', __name__)


# ── Add Review ────────────────────────────────────────────────────
@reviews_bp.route('/', methods=['POST'])
@jwt_required()
def add_review():
    data = request.get_json(silent=True) or {}
    uid  = get_jwt_identity()

    for f in ('bike_id', 'booking_id', 'rating', 'comment'):
        if not str(data.get(f, '')).strip():
            return jsonify({'error': f'{f} is required'}), 400

    try:
        rating = int(data['rating'])
    except (ValueError, TypeError):
        return jsonify({'error': 'rating must be an integer'}), 400
    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    db = get_db()

    # Validate booking
    try:
        bk = db.bookings.find_one({'_id': oid(data['booking_id'])})
    except ValueError:
        return jsonify({'error': 'Invalid booking ID'}), 400
    if not bk or bk['user_id'] != uid:
        return jsonify({'error': 'Booking not found or not yours'}), 400
    if bk['status'] != 'completed':
        return jsonify({'error': 'You can only review completed bookings'}), 400

    # Duplicate check (unique index: booking_id + user_id)
    if db.reviews.find_one({'booking_id': data['booking_id'], 'user_id': uid}):
        return jsonify({'error': 'You already reviewed this booking'}), 409

    rev = review_schema(uid, data['bike_id'], data['booking_id'],
                        rating, data['comment'])
    result = db.reviews.insert_one(rev)
    rev['_id'] = result.inserted_id

    # Recalculate bike rating
    pipeline = [
        {'$match': {'bike_id': data['bike_id']}},
        {'$group': {'_id': None,
                    'avg': {'$avg': '$rating'},
                    'cnt': {'$sum': 1}}},
    ]
    agg = list(db.reviews.aggregate(pipeline))
    if agg:
        db.bikes.update_one(
            {'_id': oid(data['bike_id'])},
            {'$set': {'rating':        round(agg[0]['avg'], 1),
                      'total_reviews': agg[0]['cnt']}}
        )

    return jsonify({'message': 'Review added successfully',
                    'review':  serial(rev)}), 201


# ── Get Reviews for a Bike ────────────────────────────────────────
@reviews_bp.route('/bike/<bike_id>', methods=['GET'])
def bike_reviews(bike_id):
    db      = get_db()
    reviews = list(db.reviews.find({'bike_id': bike_id})
                              .sort('created_at', -1))
    result  = []
    for r in reviews:
        r = serial(r)
        u = db.users.find_one({'_id': oid(r['user_id'])}, {'name': 1})
        r['user_name'] = u['name'] if u else 'Anonymous'
        result.append(r)
    return jsonify(result)
