# Auth module initialization
from .auth_routes import auth_bp

# Make the blueprint available when importing the auth module
__all__ = ['auth_bp']

