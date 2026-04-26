
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import bcrypt
import os
import uuid
import json
from datetime import datetime
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['DATA_FILE'] = 'data/alerts.json'

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Encryption key (in production, store this securely)
ENCRYPTION_KEY = get_random_bytes(32)  # AES-256

def encrypt_data(data):
    """Encrypt data using AES-256"""
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    iv = cipher.iv
    return base64.b64encode(iv + ct_bytes).decode()

def decrypt_data(encrypted_data):
    """Decrypt data using AES-256"""
    try:
        data = base64.b64decode(encrypted_data)
        iv = data[:16]
        ct = data[16:]
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode()
    except (ValueError, KeyError):
        return None

def load_alerts():
    """Load alerts from JSON file"""
    try:
        with open(app.config['DATA_FILE'], 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default alerts (using existing files as placeholders)
        return {
            "alerts": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Emma Johnson",
                    "age": 8,
                    "description": "Brown hair, blue eyes, red jacket",
                    "last_seen": "Central Park area",
                    "last_seen_time": "2024-01-15T14:30:00",
                    "status": "critical",
                    "image": "Anusign.png"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Michael Chen",
                    "age": 10,
                    "description": "Blonde hair, glasses, striped shirt",
                    "last_seen": "Lincoln Elementary",
                    "last_seen_time": "2024-01-15T11:45:00",
                    "status": "urgent",
                    "image": "drawio.png"
                }
            ]
        }

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve images from the root or upload directory"""
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return send_from_directory('.', filename)

def save_alerts(alerts):
    """Save alerts to JSON file"""
    with open(app.config['DATA_FILE'], 'w') as f:
        json.dump(alerts, f, indent=2)

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Dummy login route"""
    data = request.json
    username = data.get('username')
    return jsonify({"success": True, "message": f"Welcome, {username}!"})

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all active alerts"""
    alerts = load_alerts()
    return jsonify(alerts)

@app.route('/api/report', methods=['POST'])
def submit_report():
    """Submit a new sighting report"""
    try:
        # Get JSON data
        data = request.json
        location = data.get('location')
        time_seen = data.get('time_seen')
        details = data.get('details')
        
        # Encrypt sensitive data
        encrypted_data = encrypt_data(json.dumps({
            'location': location,
            'time_seen': time_seen,
            'details': details,
            'submitted_at': datetime.now().isoformat()
        }))
        
        # Simulate fake report detection
        is_fake = len(details) < 10 if details else True
        
        return jsonify({
            'success': True,
            'message': 'Report submitted successfully',
            'encrypted': True,
            'ai_analysis': {
                'match_probability': 0,
                'is_potential_fake': is_fake
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/emergency', methods=['POST'])
def emergency_hotline():
    """Simulate emergency hotline connection"""
    return jsonify({
        'success': True,
        'message': 'Connecting to emergency hotline: 1-800-555-SAFE',
        'hotline': '1-800-555-SAFE'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Calculate participant counts from CSV files"""
    stats = []
    files = [
        "registrations-export-participants.csv",
        "registrations-export-participants (1).csv",
        "registrations-export-participants (2).csv",
        "registrations-export-participants (3).csv",
        "registrations-export-participants (4).csv"
    ]
    
    total = 0
    for file_name in files:
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    count = len(lines) - 1 if len(lines) > 0 else 0
                    stats.append({"file": file_name, "count": max(0, count)})
                    total += max(0, count)
            except Exception:
                stats.append({"file": file_name, "count": "Error reading"})
        else:
            stats.append({"file": file_name, "count": "File not found"})
            
    return jsonify({"details": stats, "total": total})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
