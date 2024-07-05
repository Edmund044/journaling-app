import pytest
from app import create_app, db
from app.models import Users, JournalEntry
from flask_jwt_extended import create_access_token
from datetime import datetime

@pytest.fixture(scope='module')
def test_client():
    app = create_app()
    app.config.from_object('app.config.TestingConfig')

    testing_client = app.test_client()

    with app.app_context():
        db.create_all()

        # Insert a test user
        user = Users(username='testuser', email='testuser@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()

        yield testing_client

        db.drop_all()

@pytest.fixture(scope='module')
def token(test_client):
    user = Users.query.filter_by(username='testuser').first()
    access_token = create_access_token(identity=user.id)
    return access_token

@pytest.fixture(scope='module')
def test_headers(token):
    return {
        'Authorization': f'Bearer {token}'
    }
