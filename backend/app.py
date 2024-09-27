from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

#JWT setup
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'
jwt = JWTManager(app)

# Simple hardcoded user for testing
users = {"admin": "password123"}  # Username: admin, Password: password123

# PostgreSQL connection settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://itsmuser:Traveller1865!!@localhost:5432/itsmtool'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Create login endpoint
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # Check if username exists and password is correct
    if username not in users or users[username] != password:
        return jsonify({"msg": "Invalid username or password"}), 401

    # Generate access token
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

# Initialize the database
db = SQLAlchemy(app)

# Define the Incident model (this corresponds to the incident table)
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)

# Create the database and tables
with app.app_context():
    db.create_all()

# Endpoint to handle form submissions
@app.route('/api/submit', methods=['POST'])
def submit_incident():
    data = request.json
    print(f"Received data: {data}")
    
    # Create a new Incident object
    new_incident = Incident(
        name=data['name'],
        email=data['email'],
        description=data['description'],
        category=data['category']
    )
    
    # Add the incident to the session and commit it to the database
    db.session.add(new_incident)
    db.session.commit()
    
    return jsonify({"message": "Incident submitted successfully!", "data": data}), 200

# Endpoint to retieve all Invidents stored
@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    query = Incident.query
    name = request.args.get('name')
    category = request.args.get('category')

    if name: 
        query = query.filter(Incident.name.ilike(f'%{name}%'))

    if category:
        query = query.filter_by(category=category)


    incidents = Incident.query.all()
    result = [
        {
            "id": incident.id,
            "name": incident.name,
            "email": incident.email,
            "description": incident.description,
            "category": incident.category
        } for incident in incidents 
    ]
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
