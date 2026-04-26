from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['DATA_FILE'] = 'data/alerts.json'

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

ENCRYPTION_KEY = get_random_bytes(32)

def encrypt_data(data):
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + ct_bytes).decode()

def load_alerts():
    try:
        if os.path.exists(app.config['DATA_FILE']):
            with open(app.config['DATA_FILE'], 'r') as f:
                return json.load(f)
    except Exception:
        pass
    
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/images/<path:filename>')
def serve_image(filename):
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return send_from_directory('.', filename)

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', 'User')
    return jsonify({"success": True, "message": f"Welcome, {username}!"})

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    return jsonify(load_alerts())

@app.route('/api/report', methods=['POST'])
def submit_report():
    try:
        data = request.json or {}
        return jsonify({
            'success': True,
            'message': 'Report submitted successfully',
            'ai_analysis': {'match_probability': 0, 'is_potential_fake': False}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emergency', methods=['POST'])
def emergency_hotline():
    return jsonify({
        'success': True,
        'message': 'Connecting to emergency hotline: 1-800-555-SAFE'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = []
    files = [
        "registrations-export-participants.csv",
        "registrations-export-participants (1).csv",
        "registrations-export-participants (2).csv",
        "registrations-export-participants (3).csv",
        "registrations-export-participants (4).csv"
    ]
    total = 0
    for f_name in files:
        if os.path.exists(f_name):
            try:
                with open(f_name, 'r', encoding='utf-8') as f:
                    count = len(f.readlines()) - 1
                    stats.append({"file": f_name, "count": max(0, count)})
                    total += max(0, count)
            except:
                stats.append({"file": f_name, "count": 0})
        else:
            stats.append({"file": f_name, "count": 0})
    return jsonify({"details": stats, "total": total})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
