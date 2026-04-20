"""
RentBike Flask API
MongoDB Atlas backend with JWT authentication.
"""
import sys, os, logging

# Ensure backend dir is on Python path regardless of where you run from
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config.settings  import Config
from config.database  import get_db, close_db

from routes.auth     import auth_bp
from routes.bikes    import bikes_bp
from routes.bookings import bookings_bp
from routes.payments import payments_bp
from routes.reviews  import reviews_bp
from routes.vendor   import vendor_bp
from routes.admin    import admin_bp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Extensions ───────────────────────────────────────────────
    CORS(
    app,
    resources={r"/api/*": {"origins": [
        "https://bike-rent-sajj.vercel.app",
        "http://localhost:3000"
    ]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)
    JWTManager(app)

    # ── Warm MongoDB connection on startup ────────────────────────
    with app.app_context():
        try:
            get_db()
        except RuntimeError as e:
            logger.critical(str(e))
            sys.exit(1)

    # ── Blueprints ────────────────────────────────────────────────
    app.register_blueprint(auth_bp,     url_prefix='/api/auth')
    app.register_blueprint(bikes_bp,    url_prefix='/api/bikes')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(reviews_bp,  url_prefix='/api/reviews')
    app.register_blueprint(vendor_bp,   url_prefix='/api/vendor')
    app.register_blueprint(admin_bp,    url_prefix='/api/admin')

    # ── Health check ──────────────────────────────────────────────
    @app.route('/api/health')
    def health():
        try:
            db = get_db()
            db.command('ping')
            return jsonify({
                'status':   'ok',
                'message':  'RentBike API running ✓',
                'database': 'MongoDB Atlas connected ✓',
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 503

    # ── Global error handlers ─────────────────────────────────────
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request', 'detail': str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'error': 'Unauthorized'}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'error': 'Forbidden'}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': 'File too large (max 16 MB)'}), 413

    @app.errorhandler(500)
    def server_error(e):
        logger.exception('Internal server error')
        return jsonify({'error': 'Internal server error'}), 500

    # ── JWT error handlers ────────────────────────────────────────
    @app.errorhandler(422)   # JWT decode errors come as 422
    def unprocessable(e):
        return jsonify({'error': 'Invalid or expired token'}), 422

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    print(f"""
╔════════════════════════════════════╗
║ 🏍️ RentBike API Starting          ║
╠════════════════════════════════════╣
║ URL: http://localhost:{port}      ║
║ Health: /api/health               ║
╚════════════════════════════════════╝
    """)

    app.run(host='0.0.0.0', port=port)
