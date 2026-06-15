"""
Core Extensions Module

This module initializes the shared extensions for the Flask application.
By instantiating them here without binding them to a specific app instance,
we prevent circular dependency issues across blueprints and models.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Initialize SQLAlchemy to handle Object-Relational Mapping (ORM) with the database.
db = SQLAlchemy()

# Initialize JWTManager to manage JSON Web Token creation, decoding, and authentication.
jwt = JWTManager()