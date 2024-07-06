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

@journal_bp.route('/profile', methods=['GET'])
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
        }
    ],
    'responses': {
        '200': {
            'description': 'User profile details',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'username': {'type': 'string'},
                    'email': {'type': 'string'}
                }
            }
        },
        '404': {
            'description': 'User not found'
        }
    }
})
def get_profile() -> Tuple[Dict[str, Any], int]:
    """
    Get user profile details.

    Requires JWT token in the header.
    Returns the user profile details if found, or an error message if not.
    """
    user_id: int = get_jwt_identity()
    user: Users = Users.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    result: Dict[str, Any] = {
        'id': user.id,
        'username': user.username,
        'email': user.email
    }
    return jsonify(result), 200


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


@journal_bp.route('/entries/<int:id>', methods=['GET'])
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
            'description': 'ID of the journal entry to retrieve'
        }
    ],
    'responses': {
        '200': {
            'description': 'Journal entry',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'title': {'type': 'string'},
                    'content': {'type': 'string'},
                    'category': {'type': 'string'},
                    'date': {'type': 'string', 'format': 'date'}
                }
            }
        },
        '404': {
            'description': 'Entry not found'
        }
    }
})
def get_entry(id: int) -> Tuple[Dict[str, Any], int]:
    """
    Get a single journal entry by ID.

    Requires JWT token in the header.
    Returns the journal entry if found, or an error message if not.
    """
    user_id: int = get_jwt_identity()
    entry: JournalEntry = JournalEntry.query.filter_by(id=id, user_id=user_id).first()

    if not entry:
        return jsonify({'message': 'Entry not found'}), 404

    result: Dict[str, Any] = {
        'id': entry.id,
        'title': entry.title,
        'content': entry.content,
        'category': entry.category,
        'date': entry.date_created.strftime('%Y-%m-%d')
    }
    return jsonify(result), 200

@journal_bp.route('/entries/<int:id>', methods=['DELETE'])
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
            'description': 'ID of the journal entry to delete'
        }
    ],
    'responses': {
        '200': {
            'description': 'Entry deleted successfully'
        },
        '404': {
            'description': 'Entry not found'
        }
    }
})
def delete_entry(id: int) -> Tuple[Dict[str, str], int]:
    """
    Delete a journal entry by ID.

    Requires JWT token in the header.
    Returns a message indicating successful entry deletion or an error message if the entry is not found.
    """
    user_id: int = get_jwt_identity()
    entry: JournalEntry = JournalEntry.query.filter_by(id=id, user_id=user_id).first()

    if not entry:
        return jsonify({'message': 'Entry not found'}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Entry deleted successfully'}), 200

@journal_bp.route('/summary', methods=['GET'])
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
            'name': 'start_date',
            'in': 'query',
            'type': 'string',
            'format': 'date'
        },
        {
            'name': 'end_date',
            'in': 'query',
            'type': 'string',
            'format': 'date'
        }
    ],
    'responses': {
        '200': {
            'description': 'Summary data',
            'schema': {
                'type': 'object',
                'properties': {
                    'total_entries': {'type': 'integer'},
                    'categories': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def get_summary():
    user_id = get_jwt_identity()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    entries = JournalEntry.query.filter(JournalEntry.user_id == user_id, JournalEntry.date_created >= start_date, JournalEntry.date <= end_date).all()
    total_entries = len(entries)
    categories = set(entry.category for entry in entries)

    return jsonify({
        'total_entries': total_entries,
        'categories': list(categories)
    }), 200