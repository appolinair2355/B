from flask import Flask, jsonify
import threading, os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'status': 'TeleFeed Bot Running', 'timestamp': datetime.now().isoformat()})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/ping')
def ping():
    return jsonify({'status': 'ok'})

def start_server_in_background():
    port = int(os.environ.get('PORT', 10000))
    t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False), daemon=True)
    t.start()
    return t
