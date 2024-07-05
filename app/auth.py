from typing import Any, Dict, Tuple
from flask import Blueprint, request, jsonify
from .app import db
from .models import Users
from flask_jwt_extended import create_access_token
from flasgger import swag_from

auth_bp: Blueprint = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'email', 'password']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'User registered successfully'
        },
        '400': {
            'description': 'User already exists'
        }
    }
})
def register() -> Tuple[Dict[str, str], int]:
    """
    Register a new user.

    Receives username, email, and password in JSON format.
    Returns a message indicating successful registration or if the user already exists.
    """
    data: Dict[str, Any] = request.get_json()
    username: str = data.get('username')
    email: str = data.get('email')
    password: str = data.get('password')

    if Users.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    new_user: Users = Users(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Access token'
        },
        '401': {
            'description': 'Invalid credentials'
        }
    }
})
def login() -> Tuple[Dict[str, Any], int]:
    """
    Login a user.

    Receives username and password in JSON format.
    Returns an access token if credentials are valid.
    """
    data: Dict[str, Any] = request.get_json()
    username: str = data.get('username')
    password: str = data.get('password')

    user: Users = Users.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token: str = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200
