"""
Interface web pour TeleFeed avec boutons de contrôle
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import subprocess
import os
import signal
import psutil
import json
from datetime import datetime

app = Flask(__name__)

# Variables globales pour les processus
telefeed_process = None
predictions_process = None

def get_process_status(process_name):
    """Vérifie si un processus est en cours d'exécution"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if process_name.lower() in ' '.join(proc.info['cmdline']).lower():
                return True, proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
            continue
    return False, None

def load_redirections():
    """Charge les redirections depuis user_data.json"""
    try:
        with open('user_data.json', 'r') as f:
            data = json.load(f)
        return data.get('redirections', {})
    except:
        return {}

@app.route('/')
def index():
    """Page principale avec les boutons de contrôle"""
    telefeed_running, telefeed_pid = get_process_status('main.py')
    predictions_running, predictions_pid = get_process_status('predictions.py')

    redirections = load_redirections()

    return render_template('index.html', 
                         telefeed_running=telefeed_running,
                         telefeed_pid=telefeed_pid,
                         predictions_running=predictions_running,
                         predictions_pid=predictions_pid,
                         redirections=redirections)

@app.route('/start_telefeed', methods=['POST'])
def start_telefeed():
    """Démarre le bot TeleFeed"""
    global telefeed_process
    try:
        if telefeed_process is None or telefeed_process.poll() is not None:
            telefeed_process = subprocess.Popen(['python', 'main.py'])
            return jsonify({'status': 'success', 'message': 'Bot TeleFeed démarré', 'pid': telefeed_process.pid})
        else:
            return jsonify({'status': 'info', 'message': 'Bot TeleFeed déjà en cours'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur: {str(e)}'})

@app.route('/stop_telefeed', methods=['POST'])
def stop_telefeed():
    """Arrête le bot TeleFeed"""
    global telefeed_process
    try:
        running, pid = get_process_status('main.py')
        if running and pid:
            os.kill(pid, signal.SIGTERM)
            telefeed_process = None
            return jsonify({'status': 'success', 'message': 'Bot TeleFeed arrêté'})
        else:
            return jsonify({'status': 'info', 'message': 'Bot TeleFeed non actif'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur: {str(e)}'})

@app.route('/start_predictions', methods=['POST'])
def start_predictions():
    """Démarre le système de prédictions automatiques"""
    try:
        from bot.prediction_system import prediction_system
        prediction_system.enable_predictions()

        return jsonify({
            'status': 'success',
            'message': '🔮 Prédictions automatiques activées - Le système analysera maintenant les messages transférés',
            'enabled': prediction_system.is_enabled(),
            'info': 'Recherche automatique de 3 cartes de couleurs différentes dans les parenthèses'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur: {str(e)}',
            'error': str(e)
        })

@app.route('/prediction_status', methods=['GET'])
def prediction_status():
    """Récupère le statut des prédictions automatiques"""
    try:
        from bot.prediction_system import prediction_system
        return jsonify({
            'status': 'success',
            'enabled': prediction_system.is_enabled(),
            'message': '🔮 Prédictions activées' if prediction_system.is_enabled() else '⏸️ Prédictions désactivées'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur: {str(e)}',
            'enabled': False
        })

@app.route('/stop_predictions', methods=['POST'])
def stop_predictions():
    try:
        from bot.prediction_system import prediction_system

        result = prediction_system.stop_predictions()

        return jsonify({
            'status': 'success',
            'message': f'Système de prédictions désactivé: {result}',
            'active': False
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur: {str(e)}'
        })

@app.route('/predictions_status')
def predictions_status():
    try:
        from bot.prediction_system import prediction_system

        status = prediction_system.get_status()

        return jsonify({
            'active': status['active'],
            'total_predictions': status['total_predictions']
        })

    except Exception as e:
        return jsonify({
            'active': False,
            'total_predictions': 0,
            'error': str(e)
        })

@app.route('/legacy_predictions', methods=['POST'])
def legacy_predictions():
    """Arrête le système de prédictions"""
    global predictions_process
    try:
        running, pid = get_process_status('predictions.py')
        if running and pid:
            os.kill(pid, signal.SIGTERM)
            predictions_process = None
            return jsonify({'status': 'success', 'message': 'Prédictions arrêtées'})
        else:
            return jsonify({'status': 'info', 'message': 'Prédictions non actives'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur: {str(e)}'})

@app.route('/configure_bot_redirect', methods=['POST'])
def configure_bot_redirect():
    """Configure la redirection automatique vers le bot"""
    try:
        # Configurer la première redirection pour envoyer vers le bot
        data = request.json
        source_id = data.get('source_id')
        bot_id = data.get('bot_id')

        # Ajouter la configuration dans user_data.json
        with open('user_data.json', 'r') as f:
            user_data = json.load(f)

        # Ajouter une redirection automatique vers le bot
        user_id = "1190237801"  # ID utilisateur principal
        if user_id not in user_data['redirections']:
            user_data['redirections'][user_id] = {}

        user_data['redirections'][user_id]['auto_bot_redirect'] = {
            "phone": "22995501564",
            "name": "auto_bot_redirect",
            "channel_name": "🤖 Auto Bot Redirect",
            "source_id": source_id,
            "destination_id": bot_id,
            "created_at": datetime.now().isoformat(),
            "replaced_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "active": True,
            "auto_redirect_to_bot": True,
            "replacement_info": ""
        }

        with open('user_data.json', 'w') as f:
            json.dump(user_data, f, indent=2)

        return jsonify({'status': 'success', 'message': 'Redirection automatique vers le bot configurée'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur: {str(e)}'})

@app.route('/status')
def status():
    """API pour récupérer le statut des services"""
    telefeed_running, telefeed_pid = get_process_status('main.py')
    predictions_running, predictions_pid = get_process_status('predictions.py')

    return jsonify({
        'telefeed': {
            'running': telefeed_running,
            'pid': telefeed_pid
        },
        'predictions': {
            'running': predictions_running, 
            'pid': predictions_pid
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)