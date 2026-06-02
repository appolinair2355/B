"""
Serveur HTTP simple pour keep-alive
"""
from flask import Flask, jsonify
import threading
import logging
import os
from datetime import datetime

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return jsonify({'status': 'TeleFeed Bot Running', 'timestamp': datetime.now().isoformat()})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/ping')
def ping():
    return jsonify({'status': 'ok'})

def start_server_in_background():
    port = int(os.environ.get('PORT', 10000))
    def run_server():
        app.run(host='0.0.0.0', port=port, debug=False)
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    start_server_in_background()
