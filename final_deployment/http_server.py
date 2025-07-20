from flask import Flask, jsonify, request
import threading
import time
import os
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variables globales pour le statut
server_status = {
    "last_activity": time.time(),
    "start_time": time.time(),
    "requests_count": 0,
    "wake_up_calls": 0
}

@app.route('/')
def home():
    """Page d'accueil"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    
    return jsonify({
        "status": "TeleFeed Bot Server Active",
        "uptime": int(time.time() - server_status["start_time"]),
        "last_activity": datetime.fromtimestamp(server_status["last_activity"]).strftime("%Y-%m-%d %H:%M:%S"),
        "requests_count": server_status["requests_count"]
    })

@app.route('/ping')
def ping():
    """Endpoint pour les pings de maintien d'activité"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    
    logger.info(f"📡 Ping reçu - {datetime.now().strftime('%H:%M:%S')}")
    
    return jsonify({
        "status": "pong",
        "timestamp": datetime.now().isoformat(),
        "server_active": True
    })

@app.route('/wake-up')
def wake_up():
    """Endpoint pour réveiller le serveur"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    server_status["wake_up_calls"] += 1
    
    logger.info("🔔 Serveur réveillé par le bot")
    
    return jsonify({
        "status": "D'accord Kouamé",
        "message": "Serveur Replit réveillé",
        "timestamp": datetime.now().isoformat(),
        "wake_up_calls": server_status["wake_up_calls"]
    })

@app.route('/status')
def status():
    """Statut détaillé du serveur"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    
    return jsonify({
        "server_status": "active",
        "uptime_seconds": int(time.time() - server_status["start_time"]),
        "last_activity": datetime.fromtimestamp(server_status["last_activity"]).strftime("%Y-%m-%d %H:%M:%S"),
        "requests_count": server_status["requests_count"],
        "wake_up_calls": server_status["wake_up_calls"],
        "current_time": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    server_status["last_activity"] = time.time()
    
    return jsonify({
        "status": "healthy",
        "service": "TeleFeed Bot",
        "timestamp": datetime.now().isoformat()
    })

def start_http_server():
    """Démarrer le serveur HTTP"""
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Démarrage du serveur HTTP sur le port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True
    )

def start_server_in_background():
    """Démarrer le serveur HTTP en arrière-plan"""
    server_thread = threading.Thread(target=start_http_server, daemon=True)
    server_thread.start()
    logger.info("🔄 Serveur HTTP démarré en arrière-plan")
    return server_thread

if __name__ == "__main__":
    start_http_server()