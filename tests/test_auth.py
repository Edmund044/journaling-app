import json

def test_register(test_client):
    response = test_client.post('/auth/register', data=json.dumps({
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword'
    }), content_type='application/json')

    assert response.status_code == 201
    assert b'Users registered successfully' in response.data

def test_login(test_client):
    response = test_client.post('/auth/login', data=json.dumps({
        'username': 'testuser',
        'password': 'testpassword'
    }), content_type='application/json')

    assert response.status_code == 200
    assert 'access_token' in json.loads(response.data)
