from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv  # Load environment variables from .env file
from datetime import datetime, timedelta, timezone

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# JWT setup: load secret key from environment variables
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') or '0b27eccaeb11a9378fcab96f9f617417c3c749f278adf97b8cc2337c7d8ef2c4'
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

# Define the Incident model (this corresponds to the incident table)
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(10), nullable=False)  # P1, P2, P3, P4
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    # Get SLA times based on priority
    def get_sla_times(self):
        priority_slas = {
            "P1": {"acknowledgment": 15, "resolution": 240},
            "P2": {"acknowledgment": 30, "resolution": 480},
            "P3": {"acknowledgment": 60, "resolution": 1440},
            "P4": {"acknowledgment": 120, "resolution": 4320},
        }
        return priority_slas.get(self.priority, {"acknowledgment": 60, "resolution": 1440})

    # Check if nearing acknowledgment SLA
    def is_nearing_acknowledgment_sla(self):
        sla_times = self.get_sla_times()
        acknowledgment_deadline = self.submitted_at + timedelta(minutes=sla_times["acknowledgment"])
        return datetime.utcnow() > acknowledgment_deadline - timedelta(minutes=10)  # 10 min warning

    # Check if nearing resolution SLA
    def is_nearing_resolution_sla(self):
        sla_times = self.get_sla_times()
        resolution_deadline = self.submitted_at + timedelta(minutes=sla_times["resolution"])
        return datetime.utcnow() > resolution_deadline - timedelta(minutes=30)  # 30 min warning

# Create the database and tables
with app.app_context():
    db.create_all()

# Endpoint to handle form submissions
@app.route('/api/submit', methods=['POST'])
@jwt_required()  # Require JWT authentication
def submit_incident():
    data = request.json
    print(f"Received data: {data}")

    # Create a new Incident object
    new_incident = Incident(
        name=data['name'],
        email=data['email'],
        description=data['description'],
        category=data['category'],
        priority=data['priority'],  # P1, P2, P3, P4
        submitted_at=datetime.now(timezone.utc)  # Use timezone-aware datetime
    )

    # Add the incident to the session and commit it to the database
    db.session.add(new_incident)
    db.session.commit()

    return jsonify({"message": "Incident submitted successfully!", "data": data}), 200

# Endpoint to retrieve all incidents (JWT required)
@app.route('/api/incidents', methods=['GET'])
@jwt_required()  # Require JWT authentication
def get_incidents():
    current_user = get_jwt_identity()  # Get current logged-in user identity
    print(request.headers)  # Debugging: check if Authorization header is being sent

    query = Incident.query
    name = request.args.get('name')
    category = request.args.get('category')

    if name:
        query = query.filter(Incident.name.ilike(f'%{name}%'))

    if category:
        query = query.filter_by(category=category)

    incidents = query.all()  # Execute the query with filters applied
    result = [
        {
            "id": incident.id,
            "name": incident.name,
            "email": incident.email,
            "description": incident.description,
            "category": incident.category,
            "priority": incident.priority,
            "submitted_at": incident.submitted_at,
            "acknowledged_at": incident.acknowledged_at,
            "resolved_at": incident.resolved_at
        } for incident in incidents
    ]
    return jsonify(result), 200

# SLA monitoring endpoint
@app.route('/api/incidents/sla-monitor', methods=['GET'])
@jwt_required()
def monitor_slas():
    incidents = Incident.query.all()
    sla_violations = []

    for incident in incidents:
        nearing_ack = incident.is_nearing_acknowledgment_sla()
        nearing_res = incident.is_nearing_resolution_sla()

        if nearing_ack or nearing_res:
            sla_violations.append({
                "id": incident.id,
                "name": incident.name,
                "priority": incident.priority,
                "submitted_at": incident.submitted_at,
                "nearing_acknowledgment": nearing_ack,
                "nearing_resolution": nearing_res
            })

    return jsonify(sla_violations), 200

if __name__ == '__main__':
    app.run(debug=True)
