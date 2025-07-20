"""
Serveur HTTP simple pour Replit Always On
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
    """Page d'accueil"""
    return jsonify({
        'status': 'TeleFeed Bot Running',
        'timestamp': datetime.now().isoformat(),
        'service': 'Replit Always On'
    })

@app.route('/health')
def health():
    """Health check pour Replit"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot': 'TeleFeed Active'
    })

@app.route('/status')
def status():
    """Statut détaillé du système"""
    return jsonify({
        'bot_status': 'running',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'active',
        'redirections': '3 active',
        'predictions': 'enabled'
    })

def start_server_in_background():
    """Démarre le serveur HTTP en arrière-plan"""
    port = int(os.environ.get('PORT', 10000))
    
    def run_server():
        logger.info(f"🌐 Démarrage du serveur HTTP sur le port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        logger.info("🔄 Serveur HTTP démarré en arrière-plan")
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    start_server_in_background()