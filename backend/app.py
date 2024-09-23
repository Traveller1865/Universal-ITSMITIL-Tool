from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# PostgreSQL connection settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://itsmuser:Traveller1865!!@localhost:5432/itsmtool'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

if __name__ == '__main__':
    app.run(debug=True)
