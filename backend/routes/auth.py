import os, re
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from bson import ObjectId
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from config.database import get_db
from models.schemas  import user_schema
from models.helpers  import serial, oid

auth_bp = Blueprint('auth', __name__)


def _allowed(filename: str) -> bool:
    ext = {'png','jpg','jpeg','gif','pdf'}
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ext


def _clean(user: dict) -> dict:
    """Return serialized user without password."""
    u = serial(user)
    u.pop('password', None)
    return u


# ── Register ─────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data     = request.get_json(silent=True) or {}
    name     = (data.get('name') or '').strip()
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password', '')
    phone    = (data.get('phone') or '').strip()
    role     = data.get('role', 'user')

    if not name or not email or not password:
        return jsonify({'error': 'name, email and password are required'}), 400
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return jsonify({'error': 'Invalid email address'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    if role not in ('user', 'vendor'):
        role = 'user'

    db   = get_db()
    user = user_schema(name, email, generate_password_hash(password), phone, role)

    try:
        result = db.users.insert_one(user)
        user['_id'] = result.inserted_id
    except DuplicateKeyError:
        return jsonify({'error': 'Email already registered'}), 409

    uid = str(result.inserted_id)
    return jsonify({
        'message':       'Registration successful',
        'access_token':  create_access_token(identity=uid),
        'refresh_token': create_refresh_token(identity=uid),
        'user':          _clean(user),
    }), 201


# ── Login ─────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data     = request.get_json(silent=True) or {}
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    db   = get_db()
    user = db.users.find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401
    if not user.get('is_active', True):
        return jsonify({'error': 'Account is deactivated. Contact support.'}), 403

    uid = str(user['_id'])
    return jsonify({
        'message':       'Login successful',
        'access_token':  create_access_token(identity=uid),
        'refresh_token': create_refresh_token(identity=uid),
        'user':          _clean(user),
    })


# ── Refresh ───────────────────────────────────────────────────────
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    uid = get_jwt_identity()
    return jsonify({'access_token': create_access_token(identity=uid)})


# ── Get Profile ───────────────────────────────────────────────────
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    db   = get_db()
    uid  = get_jwt_identity()
    user = db.users.find_one({'_id': oid(uid)})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(_clean(user))


# ── Update Profile ────────────────────────────────────────────────
@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    db   = get_db()
    uid  = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    allowed_fields = {k: data[k] for k in ('name', 'phone', 'avatar') if k in data}
    allowed_fields['updated_at'] = datetime.utcnow()

    db.users.update_one({'_id': oid(uid)}, {'$set': allowed_fields})
    user = db.users.find_one({'_id': oid(uid)})
    return jsonify(_clean(user))


# ── Upload License ────────────────────────────────────────────────
@auth_bp.route('/upload-license', methods=['POST'])
@jwt_required()
def upload_license():
    uid = get_jwt_identity()

    if 'license' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['license']
    if not file or not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    if not _allowed(file.filename):
        return jsonify({'error': 'Only jpg, png, gif, pdf files allowed'}), 400

    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"lic_{uid}_{secure_filename(file.filename)}"
    file.save(os.path.join(upload_dir, filename))

    db = get_db()
    db.users.update_one(
        {'_id': oid(uid)},
        {'$set': {
            'license_image': filename,
            'kyc_status':    'pending',
            'updated_at':    datetime.utcnow(),
        }}
    )
    return jsonify({'message': 'License uploaded successfully', 'filename': filename})
