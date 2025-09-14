# backend/app.py
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import uuid
from did_manager import DIDManager

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)

did_manager = DIDManager()
active_challenges = {}  # Store active challenges {challenge_id: challenge_data}

@app.route('/')
def index():
    """Serve the main frontend page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend folder"""
    return send_from_directory('../frontend', filename)

@app.route('/api/register_did', methods=['POST'])
def register_did():
    """Register new DID with user information"""
    try:
        data = request.get_json()
        user_info = data.get('user_info', {})
        
        if not user_info:
            return jsonify({'error': 'User information required'}), 400
        
        result = did_manager.create_did(user_info)
        
        return jsonify({
            'success': True,
            'did': result['did'],
            'document': result['document'],
            'private_key': result['private_key'],
            'message': 'DID created successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_did/<did>', methods=['GET'])
def get_did(did):
    """Get DID document by DID"""
    try:
        document = did_manager.get_did_document(did)
        
        if not document:
            return jsonify({'error': 'DID not found'}), 404
        
        return jsonify({
            'success': True,
            'did': did,
            'document': document
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create_challenge', methods=['POST'])
def create_challenge():
    """Create authentication challenge"""
    try:
        data = request.get_json()
        did = data.get('did')
        
        if not did:
            return jsonify({'error': 'DID required'}), 400
        
        # Check if DID exists
        did_doc = did_manager.get_did_document(did)
        if not did_doc:
            return jsonify({'error': 'DID not found'}), 404
        
        # Generate challenge
        challenge_id = str(uuid.uuid4())
        challenge = f"auth-challenge-{challenge_id}-{did}"
        
        active_challenges[challenge_id] = {
            'challenge': challenge,
            'did': did,
            'used': False
        }
        
        return jsonify({
            'success': True,
            'challenge_id': challenge_id,
            'challenge': challenge
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    """Authenticate using signed challenge"""
    try:
        data = request.get_json()
        challenge_id = data.get('challenge_id')
        signature = data.get('signature')
        
        if not challenge_id or not signature:
            return jsonify({'error': 'Challenge ID and signature required'}), 400
        
        # Get challenge data
        challenge_data = active_challenges.get(challenge_id)
        if not challenge_data:
            return jsonify({'error': 'Invalid or expired challenge'}), 400
        
        if challenge_data['used']:
            return jsonify({'error': 'Challenge already used'}), 400
        
        # Verify signature
        is_valid = did_manager.authenticate_challenge(
            challenge_data['did'],
            challenge_data['challenge'],
            signature
        )
        
        # Mark challenge as used
        challenge_data['used'] = True
        
        return jsonify({
            'success': True,
            'authenticated': is_valid,
            'did': challenge_data['did'],
            'message': 'Authentication successful' if is_valid else 'Authentication failed'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sign_challenge', methods=['POST'])
def sign_challenge():
    """Sign challenge with private key (helper endpoint)"""
    try:
        data = request.get_json()
        challenge = data.get('challenge')
        private_key = data.get('private_key')
        
        if not challenge or not private_key:
            return jsonify({'error': 'Challenge and private key required'}), 400
        
        signature = did_manager.sign_challenge(challenge, private_key)
        
        return jsonify({
            'success': True,
            'signature': signature
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain_info', methods=['GET'])
def blockchain_info():
    """Get blockchain information"""
    try:
        info = did_manager.get_blockchain_info()
        return jsonify({
            'success': True,
            'blockchain_info': info
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)