from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

from config.database import get_db
from models.schemas  import bike_schema
from models.helpers  import serial, serial_list, oid

bikes_bp = Blueprint('bikes', __name__)


# ── Featured  (MUST be before /<bike_id>) ────────────────────────
@bikes_bp.route('/featured', methods=['GET'])
def get_featured():
    db    = get_db()
    bikes = list(db.bikes.find({'is_available': True})
                          .sort('rating', -1).limit(6))
    return jsonify(serial_list(bikes))


# ── AI Recommend  (MUST be before /<bike_id>) ────────────────────
@bikes_bp.route('/recommend', methods=['GET'])
@jwt_required()
def recommend():
    db  = get_db()
    uid = get_jwt_identity()

    past       = list(db.bookings.find({'user_id': uid, 'status': 'completed'}))
    rented_ids = [b['bike_id'] for b in past]

    if rented_ids:
        rented_bikes = list(db.bikes.find(
            {'_id': {'$in': [oid(bid) for bid in rented_ids]}}
        ))
        if rented_bikes:
            type_counts = {}
            for b in rented_bikes:
                type_counts[b['type']] = type_counts.get(b['type'], 0) + 1
            pref_type = max(type_counts, key=type_counts.get)
            avg_price = sum(b['price_per_hour'] for b in rented_bikes) / len(rented_bikes)

            recommended = list(db.bikes.find({
                'type':           pref_type,
                'is_available':   True,
                '_id':            {'$nin': [oid(bid) for bid in rented_ids]},
                'price_per_hour': {'$lte': avg_price * 1.5},
            }).sort('rating', -1).limit(4))

            if recommended:
                return jsonify({
                    'bikes':  serial_list(recommended),
                    'reason': f'Based on your love for {pref_type} bikes',
                })

    bikes = list(db.bikes.find({'is_available': True})
                          .sort([('rating', -1), ('total_bookings', -1)])
                          .limit(4))
    return jsonify({'bikes': serial_list(bikes), 'reason': 'Top rated bikes'})


# ── List / Search ─────────────────────────────────────────────────
@bikes_bp.route('/', methods=['GET'])
def get_bikes():
    db = get_db()

    # --- query params ---
    location    = request.args.get('location', '').strip()
    bike_type   = request.args.get('type', '').strip()
    search      = request.args.get('search', '').strip()
    sort_by     = request.args.get('sort', 'newest')
    avail_only  = request.args.get('available', 'true').lower() != 'false'

    try:
        min_price = float(request.args.get('min_price', 0))
        max_price = float(request.args.get('max_price', 99999))
        page      = max(1, int(request.args.get('page', 1)))
        per_page  = min(50, max(1, int(request.args.get('per_page', 12))))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid numeric parameter'}), 400

    # --- build query ---
    query = {}
    if avail_only:
        query['is_available'] = True
    if bike_type:
        query['type'] = bike_type
    if min_price or max_price < 99999:
        query['price_per_hour'] = {}
        if min_price:
            query['price_per_hour']['$gte'] = min_price
        if max_price < 99999:
            query['price_per_hour']['$lte'] = max_price
    if location:
        query['location'] = {'$regex': location, '$options': 'i'}
    if search:
        query['$or'] = [
            {'name':        {'$regex': search, '$options': 'i'}},
            {'brand':       {'$regex': search, '$options': 'i'}},
            {'model':       {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}},
        ]

    # --- sort ---
    sort_map = {
        'price_asc':  [('price_per_hour', 1)],
        'price_desc': [('price_per_hour', -1)],
        'rating':     [('rating', -1)],
        'newest':     [('created_at', -1)],
    }
    sort = sort_map.get(sort_by, [('created_at', -1)])

    total    = db.bikes.count_documents(query)
    pages    = max(1, (total + per_page - 1) // per_page)
    skip     = (page - 1) * per_page
    bikes    = list(db.bikes.find(query).sort(sort).skip(skip).limit(per_page))

    return jsonify({
        'bikes':    serial_list(bikes),
        'total':    total,
        'page':     page,
        'per_page': per_page,
        'pages':    pages,
    })


# ── Single Bike ───────────────────────────────────────────────────
@bikes_bp.route('/<bike_id>', methods=['GET'])
def get_bike(bike_id):
    db = get_db()
    try:
        bike = db.bikes.find_one({'_id': oid(bike_id)})
    except ValueError:
        return jsonify({'error': 'Invalid bike ID'}), 400

    if not bike:
        return jsonify({'error': 'Bike not found'}), 404

    # Attach recent reviews with user names
    reviews = list(
        db.reviews.find({'bike_id': bike_id})
                  .sort('created_at', -1).limit(20)
    )
    for r in reviews:
        u = db.users.find_one({'_id': oid(r['user_id'])}, {'name': 1})
        r['user_name'] = u['name'] if u else 'Anonymous'

    result            = serial(bike)
    result['reviews'] = serial_list(reviews)
    return jsonify(result)


# ── Availability Check ────────────────────────────────────────────
@bikes_bp.route('/<bike_id>/availability', methods=['GET'])
def check_availability(bike_id):
    start = request.args.get('start', '')
    end   = request.args.get('end', '')
    if not start or not end:
        return jsonify({'error': 'start and end query params required'}), 400

    db = get_db()
    # Check for overlapping confirmed/active bookings
    conflict = db.bookings.find_one({
        'bike_id': bike_id,
        'status':  {'$in': ['confirmed', 'active']},
        '$or': [{'start_time': {'$lt': end}, 'end_time': {'$gt': start}}],
    })
    return jsonify({'available': conflict is None})


# ── Add Bike  (vendor / admin) ────────────────────────────────────
@bikes_bp.route('/', methods=['POST'])
@jwt_required()
def add_bike():
    db  = get_db()
    uid = get_jwt_identity()
    u   = db.users.find_one({'_id': oid(uid)})
    if not u or u.get('role') not in ('vendor', 'admin'):
        return jsonify({'error': 'Vendor or Admin access required'}), 403

    data    = request.get_json(silent=True) or {}
    missing = [f for f in ('name','type','brand','model','year',
                            'price_per_hour','price_per_day','location')
               if not data.get(f)]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    try:
        bike = bike_schema(
            vendor_id=uid, name=data['name'], type_=data['type'],
            brand=data['brand'], model=data['model'], year=data['year'],
            price_per_hour=data['price_per_hour'],
            price_per_day=data['price_per_day'],
            location=data['location'],
            description=data.get('description', ''),
            image=data.get('image'),
        )
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid data: {e}'}), 400

    bike['features'] = data.get('features', [])
    result = db.bikes.insert_one(bike)
    bike['_id'] = result.inserted_id
    return jsonify({'message': 'Bike added successfully', 'bike': serial(bike)}), 201


# ── Update Bike ───────────────────────────────────────────────────
@bikes_bp.route('/<bike_id>', methods=['PUT'])
@jwt_required()
def update_bike(bike_id):
    db  = get_db()
    uid = get_jwt_identity()
    try:
        bike = db.bikes.find_one({'_id': oid(bike_id)})
    except ValueError:
        return jsonify({'error': 'Invalid bike ID'}), 400
    if not bike:
        return jsonify({'error': 'Bike not found'}), 404

    u = db.users.find_one({'_id': oid(uid)})
    if u.get('role') != 'admin' and bike.get('vendor_id') != uid:
        return jsonify({'error': 'Unauthorized'}), 403

    data    = request.get_json(silent=True) or {}
    allowed = ['name','type','brand','model','year','price_per_hour',
               'price_per_day','location','description','image',
               'is_available','features']
    updates = {k: data[k] for k in allowed if k in data}
    updates['updated_at'] = datetime.utcnow()
    db.bikes.update_one({'_id': oid(bike_id)}, {'$set': updates})
    return jsonify(serial(db.bikes.find_one({'_id': oid(bike_id)})))


# ── Delete Bike ───────────────────────────────────────────────────
@bikes_bp.route('/<bike_id>', methods=['DELETE'])
@jwt_required()
def delete_bike(bike_id):
    db  = get_db()
    uid = get_jwt_identity()
    try:
        bike = db.bikes.find_one({'_id': oid(bike_id)})
    except ValueError:
        return jsonify({'error': 'Invalid bike ID'}), 400
    if not bike:
        return jsonify({'error': 'Bike not found'}), 404

    u = db.users.find_one({'_id': oid(uid)})
    if u.get('role') != 'admin' and bike.get('vendor_id') != uid:
        return jsonify({'error': 'Unauthorized'}), 403

    db.bikes.delete_one({'_id': oid(bike_id)})
    return jsonify({'message': 'Bike deleted successfully'})
