from flask import Flask, request, jsonify
from functools import wraps
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv  # Load environment variables from .env file
from datetime import datetime, timedelta, timezone
import spacy
from custom_entity_ruler import add_entity_ruler
from nlp_categories import categorize_incident

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# JWT setup: load secret key from environment variables
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

app.config['SECRET_KEY'] = os.getenv('Flask_SECRET_KEY')

# Get the database URL from the environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Load language model and add the custom entity ruler
nlp = spacy.load("en_core_web_sm")
nlp = add_entity_ruler(nlp)  # This will add the registered entity ruler

# Sample users with roles (to be updated with DB later)
users = {
    "admin": {"password": "admin123", "roles": ["admin", "support_engineer", "manager", "analyst"]},
    "support": {"password": "support123", "roles": ["support_engineer"]},
    "agent": {"password": "agent123", "roles": ["service_desk_agent"]},
    "manager": {"password": "manager123", "roles": ["manager"]},
    "analyst": {"password": "analyst123", "roles": ["analyst"]},
    "guest": {"password": "guest123", "roles": ["guest"]},
    "external": {"password": "external123", "roles": ["guest", "external"]},
}

# Create user login endpoint
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # Check if username exists and password is correct
    if username not in users or users[username]['password'] != password:
        return jsonify({"msg": "Invalid username or password"}), 401

    role = users[username]["roles"]
    
    # Set different token expiry times based on roles
    if "admin" in role:
        expires = timedelta(days=7)
    elif "guest" in role:
        expires = timedelta(days=1)
    else:
        expires = timedelta(hours=36)  # Other non-admin staff

    # Generate token with roles
    access_token = create_access_token(identity={"username": username, "roles": role}, expires_delta=expires)
    return jsonify(access_token=access_token), 200

# Decorator to restrict access by roles
def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            user_roles = current_user.get('roles', [])
            if not any(role in user_roles for role in required_roles):
                return jsonify({"msg": f"Permission Denied: Requires one of the following roles: {required_roles}"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Admin has full access
@app.route('/admin-dashboard', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def admin_dashboard():
    return jsonify({"msg": "Admin access"}), 200

# Support engineer manages incidents
@app.route('/manage-incident', methods=['POST'])
@jwt_required()
@role_required(['support_engineer'])
def manage_incident():
    return jsonify({"msg": "Incident managed successfully."}), 200

# Service Desk Agent can submit and manage incidents
@app.route('/submit-incident', methods=['POST'])
@jwt_required()
@role_required(['service_desk_agent'])
def submit_incident_internal():
    return jsonify({"msg": "Incident submitted by agent."}), 200

# Manager can view incidents and reports
@app.route('/view-incidents', methods=['GET'])
@jwt_required()
@role_required(['manager'])
def view_incidents():
    return jsonify({"msg": "Incident list for manager."}), 200

# Analyst can only read incidents for reporting purposes
@app.route('/report-incident', methods=['GET'])
@jwt_required()
@role_required(['analyst'])
def report_incident():
    return jsonify({"msg": "Incident report."}), 200

# Guests or external users submit incidents
@app.route('/submit-external-incident', methods=['POST'])
def submit_incident_external():
    return jsonify({"msg": "External incident submitted."}), 200

# Define the Incident model
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(10), nullable=False)  # P1, P2, P3, P4
    submitted_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    escalation_level = db.Column(db.String(50), nullable=True)  # Optional escalation level
    escalated_at = db.Column(db.DateTime, nullable=True)  # Timestamp for escalation
    is_sla_breached = db.Column(db.Boolean, default=False)  # Track SLA breach
    breached_at = db.Column(db.DateTime, nullable=True)  # Timestamp for SLA breach

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
        return datetime.now(timezone.utc) > acknowledgment_deadline - timedelta(minutes=10)  # 10 min warning

    # Check if nearing resolution SLA
    def is_nearing_resolution_sla(self):
        sla_times = self.get_sla_times()
        resolution_deadline = self.submitted_at + timedelta(minutes=sla_times["resolution"])
        return datetime.now(timezone.utc) > resolution_deadline - timedelta(minutes=30)  # 30 min warning

# Acknowledge Incident (for Support Engineers)
@app.route('/api/incident/<int:incident_id>/acknowledge', methods=['PUT'])
@jwt_required()
@role_required(['support_engineer', 'admin'])
def acknowledge_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    if incident.acknowledged_at is not None:
        return jsonify({"msg": "Incident already acknowledged"}), 400
    
    incident.acknowledged_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Incident acknowledged", "incident_id": incident_id}), 200

# Resolve Incident (for Support Engineers)
@app.route('/api/incident/<int:incident_id>/resolve', methods=['PUT'])
@jwt_required()
@role_required(['support_engineer', 'admin'])
def resolve_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    if incident.resolved_at is not None:
        return jsonify({"msg": "Incident already resolved"}), 400

    incident.resolved_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Incident resolved", "incident_id": incident_id}), 200

# Create the database and tables
with app.app_context():
    db.create_all()

# Endpoint to handle form submissions
@app.route('/api/submit', methods=['POST'])
@jwt_required()
def submit_incident():
    data = request.json
    new_incident = Incident(
        name=data['name'],
        email=data['email'],
        description=data['description'],
        category=data['category'],
        priority=data['priority'],
        submitted_at=datetime.now(timezone.utc)
    )
    db.session.add(new_incident)
    db.session.commit()
    return jsonify({"message": "Incident submitted successfully!", "data": data}), 200

# Endpoint to retrieve all incidents (JWT required)
@app.route('/api/incidents', methods=['GET'])
@jwt_required()
def get_incidents():
    query = Incident.query
    name = request.args.get('name')
    category = request.args.get('category')

    if name:
        query = query.filter(Incident.name.ilike(f'%{name}%'))

    if category:
        query = query.filter_by(category=category)

    incidents = query.all()
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

# Middleware to handle incident text processing before saving
@app.before_request
def process_incident_middleware():
    if request.path == '/api/incidents/new' and request.method == 'POST':
        description = request.json.get('description')
        if description:
            # Process with SpaCy
            doc = nlp(description)
            request.entities = [(ent.text, ent.label_) for ent in doc.ents]


# Use SpaCy to process and categorize the incident description
@app.route('/api/incidents/new', methods=['POST'])
@jwt_required()
@role_required(['service_desk_agent', 'support_engineer', 'admin'])  # Restrict access
def submit_new_incident():
    data = request.get_json()
    description = data.get("description")
    name = data.get("name")
    email = data.get("email")
    priority = data.get("priority")
    
    # Use the categorize_incident function from nlp_categories.py
    category, entities = categorize_incident(description)
    
    # Create new incident with processed details
    new_incident = Incident(
        name=name,
        email=email,
        description=description,
        category=category,
        priority=priority,
        submitted_at=datetime.now(timezone.utc)
    )
    db.session.add(new_incident)
    db.session.commit()
    
    return jsonify({
        "message": "Incident submitted successfully",
        "category": category,
        "entities": entities
    }), 200


# SLA monitoring endpoint
@app.route('/api/incidents/sla-monitor', methods=['GET'])
@jwt_required()
def monitor_slas():
    incidents = Incident.query.all()
    sla_violations = []

    for incident in incidents:
        nearing_ack = incident.is_nearing_acknowledgment_sla()
        nearing_res = incident.is_nearing_resolution_sla()

        # Check if the incident has breached the SLA
        if not incident.is_sla_breached and nearing_res:
            incident.is_sla_breached = True
            incident.breached_at = datetime.now(timezone.utc)
            db.session.commit()

        if nearing_ack or nearing_res:
            sla_violations.append({
                "id": incident.id,
                "name": incident.name,
                "priority": incident.priority,
                "submitted_at": incident.submitted_at,
                "nearing_acknowledgment": nearing_ack,
                "nearing_resolution": nearing_res,
                "is_sla_breached": incident.is_sla_breached,
                "breached_at": incident.breached_at,
            })

    return jsonify(sla_violations), 200

# Create mock incidents for testing SpaCy NLP integration
incidents = [
    {"description": "Wi-Fi is down across campus."},
    {"description": "Server is overloaded in the data center."},
    {"description": "Password reset needed for student account."}
]

for incident in incidents:
    doc = nlp(incident['description'])
    print(f"Incident: {incident['description']}")
    print([(ent.text, ent.label_) for ent in doc.ents])

# Main entry point for running the app
if __name__ == '__main__':
    app.run(debug=True)
