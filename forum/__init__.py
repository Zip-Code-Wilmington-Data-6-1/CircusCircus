from flask import Flask
from forum.routes import rt
from forum.auth import auth_bp

def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    # Register blueprints for modular organization
    app.register_blueprint(rt)
    app.register_blueprint(auth_bp)  # Authentication module
    # Set globals
    from forum.models import db
    db.init_app(app)
    
    with app.app_context():
        # Add some routes
        db.create_all()
        return app

