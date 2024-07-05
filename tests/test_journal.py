import json
from datetime import datetime

def test_update_profile(test_client, test_headers):
    response = test_client.put('/journal/profile', headers=test_headers, data=json.dumps({
        'username': 'updateduser',
        'email': 'updateduser@example.com'
    }), content_type='application/json')

    assert response.status_code == 200
    assert b'Profile updated successfully' in response.data

def test_create_entry(test_client, test_headers):
    response = test_client.post('/journal/entries', headers=test_headers, data=json.dumps({
        'title': 'Test Entry',
        'content': 'This is a test entry.',
        'category': 'Test',
        'date': datetime.now().strftime('%Y-%m-%d')
    }), content_type='application/json')

    assert response.status_code == 201
    assert b'Entry created successfully' in response.data

def test_get_entries(test_client, test_headers):
    response = test_client.get('/journal/entries', headers=test_headers)

    assert response.status_code == 200
    entries = json.loads(response.data)
    assert len(entries) > 0

def test_update_entry(test_client, test_headers):
    response = test_client.get('/journal/entries', headers=test_headers)
    entries = json.loads(response.data)
    entry_id = entries[0]['id']

    response = test_client.put(f'/journal/entries/{entry_id}', headers=test_headers, data=json.dumps({
        'title': 'Updated Entry',
        'content': 'This is an updated entry.',
        'category': 'Updated',
        'date': datetime.now().strftime('%Y-%m-%d')
    }), content_type='application/json')

    assert response.status_code == 200
    assert b'Entry updated successfully' in response.data

def test_delete_entry(test_client, test_headers):
    response = test_client.get('/journal/entries', headers=test_headers)
    entries = json.loads(response.data)
    entry_id = entries[0]['id']

    response = test_client.delete(f'/journal/entries/{entry_id}', headers=test_headers)

    assert response.status_code == 200
    assert b'Entry deleted successfully' in response.data

def test_get_summary(test_client, test_headers):
    response = test_client.get('/journal/summary?start_date=2023-01-01&end_date=2023-12-31', headers=test_headers)

    assert response.status_code == 200
    summary = json.loads(response.data)
    assert 'total_entries' in summary
    assert 'categories' in summary
