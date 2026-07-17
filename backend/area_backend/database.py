"""
Core Extensions Module

This module initializes the shared extensions for the Flask application.
By instantiating them here without binding them to a specific app instance,
we prevent circular dependency issues across blueprints and models.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize SQLAlchemy to handle Object-Relational Mapping (ORM) with the database.
db = SQLAlchemy()

# Initialize JWTManager to manage JSON Web Token creation, decoding, and authentication.
jwt = JWTManager()

# Initialize Limiter for rate limiting (brute-force protection on auth endpoints).
# The storage backend is configured via app.config['RATELIMIT_STORAGE_URI']
# (e.g. redis://redis:6379/0 in production).
limiter = Limiter(key_func=get_remote_address)
