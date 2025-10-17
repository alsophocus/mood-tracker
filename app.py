from flask import Flask
from datetime import timedelta
from config import Config
from database import db
from auth import auth_bp, init_auth
from routes import main_bp

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        raise
    
    # Initialize database
    try:
        db.initialize()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    
    # Initialize authentication
    init_auth(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # Add timezone conversion filter
    @app.template_filter('utc_to_local')
    def utc_to_local(utc_dt):
        if not utc_dt:
            return None
        return utc_dt - timedelta(hours=3)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
