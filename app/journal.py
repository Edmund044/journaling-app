from typing import Any, Dict, List, Tuple
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .app import db
from .models import Users, JournalEntry
from datetime import datetime
from flasgger import swag_from

journal_bp: Blueprint = Blueprint('journal', __name__)

@journal_bp.route('/profile', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Profile'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'email': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Profile updated successfully'
        }
    }
})
def update_profile() -> Tuple[Dict[str, str], int]:
    """
    Update user profile.

    Receives username and email in JSON format. Requires JWT token in the header.
    Returns a message indicating successful profile update.
    """
    user_id: int = get_jwt_identity()
    data: Dict[str, Any] = request.get_json()
    user: Users = Users.query.get(user_id)

    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

@journal_bp.route('/entries', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Journal'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'content': {'type': 'string'},
                    'category': {'type': 'string'},
                },
                'required': ['title', 'content', 'category', 'date']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Entry created successfully'
        }
    }
})
def create_entry() -> Tuple[Dict[str, str], int]:
    """
    Create a new journal entry.

    Receives title, content, category, and date in JSON format. Requires JWT token in the header.
    Returns a message indicating successful entry creation.
    """
    user_id: int = get_jwt_identity()
    data: Dict[str, Any] = request.get_json()
    new_entry: JournalEntry = JournalEntry(
        title=data['title'],
        content=data['content'],
        category=data['category'],
        user_id=user_id
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({'message': 'Entry created successfully'}), 201

@journal_bp.route('/entries', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Journal'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        }
    ],
    'responses': {
        '200': {
            'description': 'A list of journal entries',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'title': {'type': 'string'},
                        'content': {'type': 'string'},
                        'category': {'type': 'string'},
                        'date': {'type': 'string', 'format': 'date'}
                    }
                }
            }
        }
    }
})
def get_entries() -> Tuple[List[Dict[str, Any]], int]:
    """
    Get all journal entries for the authenticated user.

    Requires JWT token in the header.
    Returns a list of journal entries.
    """
    user_id: int = get_jwt_identity()
    entries: List[JournalEntry] = JournalEntry.query.filter_by(user_id=user_id).all()
    result: List[Dict[str, Any]] = [
        {
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'category': entry.category,
            'date': entry.date_created.strftime('%Y-%m-%d')
        } for entry in entries
    ]
    return jsonify(result), 200

@journal_bp.route('/entries/<int:id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Journal'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the journal entry to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'content': {'type': 'string'},
                    'category': {'type': 'string'},
                },
                'required': ['title', 'content', 'category', 'date']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Entry updated successfully'
        },
        '404': {
            'description': 'Entry not found'
        },
        '400': {
            'description': 'Invalid input'
        }
    }
})
def update_entry(id: int) -> Tuple[Dict[str, str], int]:
    """
    Update a journal entry by ID.

    Receives title, content, category, and date in JSON format. Requires JWT token in the header.
    Returns a message indicating successful entry update or error messages if the entry is not found or input is invalid.
    """
    user_id: int = get_jwt_identity()
    entry: JournalEntry = JournalEntry.query.filter_by(id=id, user_id=user_id).first()

    if not entry:
        return jsonify({'message': 'Entry not found'}), 404

    data: Dict[str, Any] = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid input'}), 400

    entry.title = data.get('title', entry.title)
    entry.content = data.get('content', entry.content)
    entry.category = data.get('category', entry.category)

    db.session.commit()
    return jsonify({'message': 'Entry updated successfully'}), 200
