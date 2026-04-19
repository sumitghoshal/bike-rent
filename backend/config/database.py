"""
MongoDB Atlas connection manager.
Uses pymongo with SRV connection string for Atlas.
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config.settings import Config
import logging

logger = logging.getLogger(__name__)

_client: MongoClient = None
_db = None


def get_db():
    """Return the MongoDB database instance (singleton)."""
    global _client, _db
    if _db is None:
        _connect()
    return _db


def _connect():
    """Establish connection to MongoDB Atlas."""
    global _client, _db
    try:
        _client = MongoClient(
            Config.MONGO_URI,
            serverSelectionTimeoutMS=8000,   # 8 sec timeout
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
            maxPoolSize=50,
            retryWrites=True,
        )
        # Verify connection
        _client.admin.command('ping')
        _db = _client[Config.DB_NAME]
        _create_indexes(_db)
        logger.info(f"✅ Connected to MongoDB Atlas — database: '{Config.DB_NAME}'")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise RuntimeError(
            f"Cannot connect to MongoDB Atlas.\n"
            f"  URI: {Config.MONGO_URI[:60]}...\n"
            f"  Error: {e}\n"
            f"  Check: Network, IP whitelist (0.0.0.0/0), credentials."
        )


def _create_indexes(db):
    """Create indexes for performance."""
    try:
        # users — unique email
        db.users.create_index([('email', ASCENDING)], unique=True, background=True)
        db.users.create_index([('role', ASCENDING)], background=True)
        db.users.create_index([('kyc_status', ASCENDING)], background=True)

        # bikes
        db.bikes.create_index([('location', ASCENDING)], background=True)
        db.bikes.create_index([('type', ASCENDING)], background=True)
        db.bikes.create_index([('price_per_hour', ASCENDING)], background=True)
        db.bikes.create_index([('is_available', ASCENDING)], background=True)
        db.bikes.create_index([('vendor_id', ASCENDING)], background=True)
        db.bikes.create_index([('rating', DESCENDING)], background=True)
        db.bikes.create_index(
            [('name', 'text'), ('brand', 'text'), ('model', 'text'), ('description', 'text')],
            background=True
        )

        # bookings
        db.bookings.create_index([('user_id', ASCENDING)], background=True)
        db.bookings.create_index([('bike_id', ASCENDING)], background=True)
        db.bookings.create_index([('vendor_id', ASCENDING)], background=True)
        db.bookings.create_index([('status', ASCENDING)], background=True)
        db.bookings.create_index([('created_at', DESCENDING)], background=True)

        # reviews
        db.reviews.create_index([('bike_id', ASCENDING)], background=True)
        db.reviews.create_index([('user_id', ASCENDING)], background=True)
        db.reviews.create_index(
            [('booking_id', ASCENDING), ('user_id', ASCENDING)], unique=True, background=True
        )

        # payments
        db.payments.create_index([('user_id', ASCENDING)], background=True)
        db.payments.create_index([('booking_id', ASCENDING)], background=True)
        db.payments.create_index([('status', ASCENDING)], background=True)

        logger.info("✅ MongoDB indexes created/verified")
    except Exception as e:
        logger.warning(f"Index creation warning (non-fatal): {e}")


def close_db():
    """Close the MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")
