from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FILE'] = 'data/alerts.json'
app.config['EVENTS_FILE'] = 'data/events.json'
app.config['REGS_FILE'] = 'data/registrations.json'
app.config['PUBLIC_FOLDER'] = 'public'

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# --- ERROR HANDLER ---
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"CRITICAL ERROR: {str(e)}")
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

def load_data(file_path, default_key='data'):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    if default_key == 'events':
        return {
            "events": [
                {
                    "eventId": "679ee38d-a005-4975-8603-402bcbbad5ad",
                    "title": "Tech Fest 2026",
                    "date": "2026-05-15",
                    "time": "10:00",
                    "location": "Main Auditorium",
                    "category": "Technical",
                    "registrationStatus": "open",
                    "participantCount": 0,
                    "volunteerCount": 0,
                    "participantLimit": 2, 
                    "createdBy": "admin",
                    "roles": [{"id": "r1", "name": "Volunteer", "slots": 5, "filled": 0, "remaining": 5}]
                }
            ]
        }
    return {default_key: []}

def save_data(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {file_path}: {e}")

# --- SERVE STATIC FILES ---
@app.route('/')
def index_root():
    return send_from_directory(app.config['PUBLIC_FOLDER'], 'index.html')

@app.route('/admin')
def admin_page():
    return send_from_directory(app.config['PUBLIC_FOLDER'], 'admin.html')

# --- AUTH ROUTES ---
@app.route('/api/auth/verify', methods=['GET'])
def verify_auth():
    return jsonify({
        "valid": True, 
        "user": {"role": "admin", "username": "admin", "email": "admin@example.com", "approved": True}
    })

@app.route('/api/auth/login', methods=['POST'])
@app.route('/api/login', methods=['POST'])
@app.route('/login', methods=['POST'])
def login_api():
    return jsonify({
        "success": True, 
        "token": "mock-token-for-demo",
        "user": {"role": "admin", "username": "admin", "approved": True}
    })

# --- EVENT ROUTES ---
@app.route('/api/events', methods=['GET'])
def get_events_api():
    data = load_data(app.config['EVENTS_FILE'], 'events')
    return jsonify(data['events'])

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event_single(event_id):
    data = load_data(app.config['EVENTS_FILE'], 'events')
    event = next((e for e in data['events'] if str(e['eventId']) == str(event_id)), None)
    if event: return jsonify(event)
    return jsonify({"error": "Event not found"}), 404

@app.route('/api/events/<event_id>/toggle-registration', methods=['PATCH', 'POST'])
def toggle_reg_api(event_id):
    data = load_data(app.config['EVENTS_FILE'], 'events')
    found_ev = None
    for ev in data['events']:
        if str(ev['eventId']) == str(event_id):
            ev['registrationStatus'] = 'closed' if ev.get('registrationStatus', 'open') == 'open' else 'open'
            found_ev = ev
            break
            
    if not found_ev:
        found_ev = {
            "eventId": event_id,
            "title": "New Event",
            "registrationStatus": "closed",
            "participantCount": 0,
            "volunteerCount": 0
        }
        data['events'].append(found_ev)
    
    save_data(app.config['EVENTS_FILE'], data)
    return jsonify(found_ev)

# --- REGISTRATION ROUTES ---
@app.route('/api/registrations', methods=['POST'])
def submit_reg_api():
    reg_data = request.json or {}
    event_id = reg_data.get('eventId')
    
    events_data = load_data(app.config['EVENTS_FILE'], 'events')
    event = next((e for e in events_data['events'] if str(e['eventId']) == str(event_id)), None)
    
    if not event: return jsonify({"error": "Event not found"}), 404
    if event.get('registrationStatus') == 'closed': return jsonify({"error": "Registrations closed"}), 400
        
    if reg_data.get('type') == 'participant':
        if int(event.get('participantCount', 0)) >= int(event.get('participantLimit', 100)):
            return jsonify({"error": "Limit reached"}), 400

    data = load_data(app.config['REGS_FILE'], 'registrations')
    reg_data['registrationId'] = str(uuid.uuid4())
    reg_data['status'] = 'confirmed'
    data['registrations'].append(reg_data)
    save_data(app.config['REGS_FILE'], data)
    
    if reg_data.get('type') == 'participant':
        event['participantCount'] = event.get('participantCount', 0) + 1
    else:
        event['volunteerCount'] = event.get('volunteerCount', 0) + 1
    save_data(app.config['EVENTS_FILE'], events_data)
    
    return jsonify({"success": True, "registration": reg_data, "eventTitle": event.get('title')})

@app.route('/api/registrations/my', methods=['GET'])
def get_my_regs():
    email = request.args.get('email')
    data = load_data(app.config['REGS_FILE'], 'registrations')
    my_regs = [r for r in data['registrations'] if r.get('email') == email]
    return jsonify(my_regs)

@app.route('/api/auth/send-otp', methods=['POST'])
def send_otp():
    return jsonify({"success": True, "message": "OTP sent! Use 123456"})

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    return jsonify({"success": True})

@app.route('/api/stats', methods=['GET'])
def get_stats_api():
    return jsonify({"total": 56, "details": [{"file": "Total System Count", "count": 56}]})

# --- IMAGE SERVING ---
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(app.config['PUBLIC_FOLDER'], filename)

# --- CATCH ALL ---
@app.route('/<path:path>')
def serve_any_public(path):
    return send_from_directory(app.config['PUBLIC_FOLDER'], path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
