from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .app import db
from .models import Users, JournalEntry
from datetime import datetime
from flasgger import swag_from

journal_bp = Blueprint('journal', __name__)

@journal_bp.route('/profile', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Profile'],
    'parameters': [
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
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    user = Users.query.get(user_id)

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
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'content': {'type': 'string'},
                    'category': {'type': 'string'},
                    'date': {'type': 'string', 'format': 'date'}
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
def create_entry():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_entry = JournalEntry(
        title=data['title'],
        content=data['content'],
        category=data['category'],
        date=datetime.strptime(data['date'], '%Y-%m-%d'),
        user_id=user_id
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({'message': 'Entry created successfully'}), 201

@journal_bp.route('/entries', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Journal'],
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
def get_entries():
    user_id = get_jwt_identity()
    entries = JournalEntry.query.filter_by(user_id=user_id).all()
    result = [{'id': entry.id, 'title': entry.title, 'content': entry.content, 'category': entry.category, 'date': entry.date.strftime('%Y-%m-%d')} for entry in entries]
    return jsonify(result), 200

@journal_bp.route('/entries/<int:id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Journal'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'content': {'type': 'string'},
                    'category': {'type': 'string'},
                    'date': {'type': 'string', 'format': 'date'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Entry updated successfully'
        },
        '404': {
            'description': 'Entry not found'
        }
    }
})
def update_entry(id):
    user_id = get_jwt_identity()
    data = request.get_json()
    entry = JournalEntry.query.get(id)

    if entry is None or entry.user_id != user_id:
        return jsonify({'message': 'Entry not found'}), 404

    if 'title' in data:
        entry.title = data['title']
    if 'content' in data:
        entry.content = data['content']
    if 'category' in data:
        entry.category = data['category']
    if 'date' in data:
        entry.date = datetime.strptime(data['date'], '%Y-%m-%d')

    db.session.commit()
    return jsonify({'message': 'Entry updated successfully'}), 200

@journal_bp.route('/entries/<int:id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Journal'],
    'responses': {
        '200': {
            'description': 'Entry deleted successfully'
        },
        '404': {
            'description': 'Entry not found'
        }
    }
})
def delete_entry(id):
    user_id = get_jwt_identity()
    entry = JournalEntry.query.get(id)

    if entry is None or entry.user_id != user_id:
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

    entries = JournalEntry.query.filter(JournalEntry.user_id == user_id, JournalEntry.date >= start_date, JournalEntry.date <= end_date).all()
    total_entries = len(entries)
    categories = set(entry.category for entry in entries)

    return jsonify({
        'total_entries': total_entries,
        'categories': list(categories)
    }), 200
