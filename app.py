from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://trial-db_owner:u2DemFOhR4WL@ep-silent-wood-a5ndpfqn.us-east-2.aws.neon.tech/journal-app?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('Users', backref=db.backref('entries', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'date_created': self.date_created,
            'user_id': self.user_id
        }

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = Users(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = Users.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message="Invalid Credentials"), 401

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = Users.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@app.route('/entries', methods=['POST'])
@jwt_required()
def create_entry():
    user_id = get_jwt_identity()
    data = request.json
    new_entry = JournalEntry(
        user_id=user_id, 
        title=data['title'], 
        content=data['content'], 
        category=data['category']
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify(new_entry.to_dict()), 201

@app.route('/entries', methods=['GET'])
@jwt_required()
def get_entries():
    user_id = get_jwt_identity()
    entries = JournalEntry.query.filter_by(user_id=user_id).all()
    return jsonify([entry.to_dict() for entry in entries]), 200

@app.route('/entries/<int:id>', methods=['GET'])
@jwt_required()
def get_entry(id):
    user_id = get_jwt_identity()
    entry = JournalEntry.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(entry.to_dict()), 200

@app.route('/entries/<int:id>', methods=['PUT'])
@jwt_required()
def update_entry(id):
    user_id = get_jwt_identity()
    data = request.json
    entry = JournalEntry.query.filter_by(id=id, user_id=user_id).first_or_404()
    entry.title = data['title']
    entry.content = data['content']
    entry.category = data['category']
    db.session.commit()
    return jsonify(entry.to_dict()), 200

@app.route('/entries/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_entry(id):
    user_id = get_jwt_identity()
    entry = JournalEntry.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    return '', 204

@app.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    user_id = get_jwt_identity()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify(message="Please provide both start_date and end_date"), 400

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify(message="Invalid date format, please use YYYY-MM-DD"), 400

    entries = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.date_created >= start_date,
        JournalEntry.date_created <= end_date
    ).all()

    total_entries = len(entries)
    category_summary = {}
    for entry in entries:
        if entry.category in category_summary:
            category_summary[entry.category] += 1
        else:
            category_summary[entry.category] = 1

    summary = {
        'total_entries': total_entries,
        'category_summary': category_summary
    }

    return jsonify(summary), 200

if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)
