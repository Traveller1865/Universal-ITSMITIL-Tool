import unittest
from app import app, db, Incident
from flask_jwt_extended import create_access_token

class TestApp(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login(self):
        response = self.app.post('/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, 200)

    def test_incident_submission(self):
        token = create_access_token(identity={"username": "admin", "role": "admin"})
        response = self.app.post('/api/submit_internal', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'description': 'Test incident',
            'category': 'IT',
            'priority': 'P1'
        }, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)

    def test_role_restriction(self):
        token = create_access_token(identity={"username": "guest", "role": "guest"})
        response = self.app.get('/admin-dashboard', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()
