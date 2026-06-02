import logging
import os
import asyncio
from telethon import TelegramClient, events
from settings import API_ID, API_HASH, BOT_TOKEN, ADMIN_ID
from keep_alive import KeepAliveSystem
from license import check_license, validate_license_code
from payment import process_payment
from deploy import handle_deploy
from connection import handle_connect, handle_verification_code
from redirection import handle_redirection_command
from transformation import handle_transformation_command
from whitelist import handle_whitelist_command
from blacklist import handle_blacklist_command
from chats import handle_chats_command
from admin import handle_admin_commands
from channel_redirect import handle_channel_to_bot_command, setup_automatic_channel_redirection
from auto_setup import setup_channel_redirection_command
from reset import handle_reset_command, admin_reset_all

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/activity.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize Telegram client without starting it yet
client = TelegramClient('bot', API_ID, API_HASH)
bot_client = client  # Export pour utilisation dans d'autres modules

@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    """Handle /start command"""
    try:
        welcome_message = """
🌟 **Bienvenue sur TeleFeed !** 🌟

Votre bot intelligent pour la gestion de contenu Telegram.

**Commandes disponibles :**
• `/connect` - Connecter un numéro de téléphone
• `/redirection` - Gérer les redirections entre chats
• `/transformation` - Modifier le contenu des messages
• `/whitelist` - Filtrer les messages autorisés
• `/blacklist` - Ignorer certains messages
• `/chats` - Afficher les chats associés à un numéro
• `/deposer` - Déposer des fichiers
• `/channel_to_bot` - Rediriger un canal vers le bot
• `/setup_channel` - Configuration automatique de votre canal

Toutes les fonctionnalités sont maintenant disponibles gratuitement !
        """
        await event.respond(welcome_message)
        logger.info(f"User {event.sender_id} started the bot")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await event.respond("❌ Une erreur est survenue. Veuillez réessayer.")





@client.on(events.NewMessage(pattern="/deposer"))
async def deposer(event):
    """Handle /deposer command for file deployment"""
    try:
        await handle_deploy(event, client)
        logger.info(f"Deploy request from user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in deploy handling: {e}")
        await event.respond("❌ Erreur lors du traitement du dépôt. Veuillez réessayer.")

@client.on(events.NewMessage(pattern="/connect"))
async def connect(event):
    """Handle /connect command"""
    try:
        await handle_connect(event, client)
        logger.info(f"Connect command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in connect command: {e}")
        await event.respond("❌ Erreur lors de la connexion. Veuillez réessayer.")

@client.on(events.NewMessage(pattern="/redirection"))
async def redirection(event):
    """Handle /redirection command"""
    try:
        await handle_redirection_command(event, client)
        logger.info(f"Redirection command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in redirection command: {e}")
        await event.respond("❌ Erreur lors de la redirection. Veuillez réessayer.")

@client.on(events.NewMessage(pattern="/transformation"))
async def transformation(event):
    """Handle /transformation command"""
    try:
        await handle_transformation_command(event, client)
        logger.info(f"Transformation command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in transformation command: {e}")
        await event.respond("❌ Erreur lors de la transformation. Veuillez réessayer.")

@client.on(events.NewMessage(pattern="/whitelist"))
async def whitelist(event):
    """Handle /whitelist command"""
    try:
        await handle_whitelist_command(event, client)
        logger.info(f"Whitelist command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in whitelist command: {e}")
        await event.respond("❌ Erreur lors de la whitelist. Veuillez réessayer.")

@client.on(events.NewMessage(pattern="/blacklist"))
async def blacklist(event):
    """Handle /blacklist command"""
    try:
        await handle_blacklist_command(event, client)
        logger.info(f"Blacklist command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in blacklist command: {e}")
        await event.respond("❌ Erreur lors de la blacklist. Veuillez réessayer.")

@client.on(events.NewMessage(pattern="/chats"))
async def chats(event):
    """Handle /chats command"""
    try:
        await handle_chats_command(event, client)
        logger.info(f"Chats command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in chats command: {e}")
        await event.respond("❌ Erreur lors de l'affichage des chats. Veuillez réessayer.")

@client.on(events.NewMessage(pattern="/channel_to_bot"))
async def channel_to_bot(event):
    """Handle /channel_to_bot command"""
    try:
        await handle_channel_to_bot_command(event, client)
        logger.info(f"Channel to bot command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in channel to bot command: {e}")
        await event.respond("❌ Erreur lors de la configuration de la redirection canal → bot. Veuillez réessayer.")

@client.on(events.NewMessage(pattern="/setup_channel"))
async def setup_channel(event):
    """Handle /setup_channel command for automatic setup"""
    try:
        await setup_channel_redirection_command(event, client)
        logger.info(f"Auto setup channel command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in auto setup channel command: {e}")
        await event.respond("❌ Erreur lors de la configuration automatique. Veuillez réessayer.")

@client.on(events.NewMessage(pattern="/test_redirect"))
async def test_redirect(event):
    """Handle /test_redirect command for manual testing"""
    try:
        message_text = event.text.strip()
        user_id = event.sender_id

        if message_text == "/test_redirect":
            help_message = """
🔧 **Test de Redirection Manuel**

**Utilisation :**
`/test_redirect SOURCE_ID DESTINATION_ID`

**Exemple avec vos IDs :**
`/test_redirect 1001194981760 1002646551216`

Cette commande teste directement la redirection entre deux canaux.
            """
            await event.respond(help_message)
            return

        parts = message_text.split()
        if len(parts) != 3:
            await event.respond("❌ Format: `/test_redirect SOURCE_ID DESTINATION_ID`")
            return

        source_id = parts[1]
        destination_id = parts[2]

        await event.respond("🔄 **Test de redirection en cours...**")

        from manual_redirect import manual_redirector

        # Test access to both channels first
        source_ok, source_result = await manual_redirector.test_channel_access(user_id, source_id)
        dest_ok, dest_result = await manual_redirector.test_channel_access(user_id, destination_id)

        if not source_ok:
            await event.respond(f"❌ **Erreur d'accès au canal source {source_id}:**\n{source_result}")
            return

        if not dest_ok:
            await event.respond(f"❌ **Erreur d'accès au canal destination {destination_id}:**\n{dest_result}")
            return

        # Setup the redirection
        success, result = await manual_redirector.setup_manual_redirection(
            user_id, "test_phone", source_id, destination_id, "test_redirect"
        )

        if success:
            message = f"""
✅ **Test de redirection configuré !**

📺 **Canal source :** {result['source_name']} ({source_id})
🎯 **Canal destination :** {result['dest_name']} ({destination_id})

🔄 **Status :** Redirection active
📨 **Test :** Envoyez un message dans le canal source pour tester

⚠️ **Note :** Ceci est un test manuel. Les redirections automatiques nécessitent une session persistante.
            """
        else:
            message = f"❌ **Erreur lors de la configuration :**\n{result}"

        await event.respond(message)

    except Exception as e:
        logger.error(f"Error in test redirect command: {e}")
        await event.respond("❌ Erreur lors du test de redirection.")

@client.on(events.NewMessage(pattern="/help"))
async def help_command(event):
    """Handle /help command"""
    try:
        help_message = """
📋 **Aide TeleFeed**

**Commandes disponibles :**

🔹 `/start` - Démarrer le bot
🔹 `/connect` - Connecter un numéro de téléphone
🔹 `/redirection` - Gérer les redirections entre chats
🔹 `/transformation` - Modifier le contenu des messages
🔹 `/whitelist` - Filtrer les messages autorisés
🔹 `/blacklist` - Ignorer certains messages
🔹 `/chats` - Afficher les chats associés à un numéro
🔹 `/deposer` - Déposer des fichiers
🔹 `/channel_to_bot` - Rediriger un canal vers le bot
🔹 `/setup_channel` - Configuration automatique de votre canal
🔹 `/reset` - Réinitialiser toutes les connexions et redirections

🔹 `/help` - Afficher cette aide

**Support :**
Pour toute question ou problème, contactez l'administrateur.
        """
        await event.respond(help_message)
        logger.info(f"Help requested by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await event.respond("❌ Une erreur est survenue. Veuillez réessayer.")

# Admin commands
@client.on(events.NewMessage(pattern="/admin"))
async def admin_command(event):
    """Handle /admin command"""
    await handle_admin_commands(event, client)

@client.on(events.NewMessage(pattern="/confirm"))
async def confirm_command(event):
    """Handle /confirm command"""
    await handle_admin_commands(event, client)

@client.on(events.NewMessage(pattern="/generate"))
async def generate_command(event):
    """Handle /generate command"""
    await handle_admin_commands(event, client)

@client.on(events.NewMessage(pattern="/users"))
async def users_command(event):
    """Handle /users command"""
    await handle_admin_commands(event, client)

@client.on(events.NewMessage(pattern="/stats"))
async def stats_command(event):
    """Handle /stats command"""
    await handle_admin_commands(event, client)

async def handle_sessions(event, client):
    """
    Handle /sessions command
    Shows active sessions and connection status
    """
    try:
        user_id = event.sender_id

        # Informations du serveur Replit
        import os
        import socket
        import platform
        from datetime import datetime

        # Obtenir les informations du serveur
        hostname = socket.gethostname()
        repl_name = os.environ.get('REPL_SLUG', 'telefeed-bot')
        repl_owner = os.environ.get('REPL_OWNER', os.environ.get('USER', 'unknown'))
        repl_url = os.environ.get('REPLIT_URL', f'https://{repl_name}.{repl_owner}.repl.co')
        server_port = os.environ.get('PORT', '8080')
        server_ip = '0.0.0.0'

        # Informations système
        python_version = platform.python_version()
        system_info = f"{platform.system()} {platform.release()}"

        # Get active connections
        from connection import active_connections

        if user_id not in active_connections:
            # Afficher quand même les infos serveur
            server_info = f"""
🌐 **Serveur Replit Hébergement**

📛 **Nom du serveur :** {hostname}
🏷️ **Nom du Repl :** {repl_name}
👤 **Propriétaire :** {repl_owner}
🔗 **URL publique :** {repl_url}
🌍 **Adresse IP :** {server_ip}
🔌 **Port :** {server_port}
🐍 **Python :** {python_version}
💻 **Système :** {system_info}
⏰ **Statut :** ✅ Serveur actif

❌ **Sessions utilisateur :** Aucune session active trouvée.

💡 **Note :** Utilisez /connect pour créer une session.
"""
            await event.respond(server_info)
            return

        connection_info = active_connections[user_id]

        # Check if connection is still valid
        if 'client' not in connection_info:
            server_info = f"""
🌐 **Serveur Replit Hébergement**

📛 **Nom du serveur :** {hostname}
🏷️ **Nom du Repl :** {repl_name}
👤 **Propriétaire :** {repl_owner}
🔗 **URL publique :** {repl_url}
🌍 **Adresse IP :** {server_ip}
🔌 **Port :** {server_port}
🐍 **Python :** {python_version}
💻 **Système :** {system_info}
⏰ **Statut :** ✅ Serveur actif

❌ **Sessions utilisateur :** Session expirée. Veuillez vous reconnecter avec /connect.
"""
            await event.respond(server_info)
            return

        phone = connection_info.get('phone', 'N/A')
        connected_at = connection_info.get('connected_at', 'N/A')

        # Get session from database
        from session_manager import session_manager
        sessions = await session_manager.get_user_sessions(user_id)

        sessions_text = f"""
🌐 **Serveur Replit Hébergement**

📛 **Nom du serveur :** {hostname}
🏷️ **Nom du Repl :** {repl_name}
👤 **Propriétaire :** {repl_owner}
🔗 **URL publique :** {repl_url}
🌍 **Adresse IP :** {server_ip}
🔌 **Port :** {server_port}
🐍 **Python :** {python_version}
💻 **Système :** {system_info}
⏰ **Statut :** ✅ Serveur actif

📱 **Sessions Utilisateur**

👤 **Utilisateur :** {user_id}
📞 **Numéro :** {phone}
⏰ **Connecté le :** {connected_at}
🔗 **Statut :** {'✅ Connecté' if connection_info.get('connected', False) else '❌ Déconnecté'}

📊 **Détails des sessions :**
"""

        if sessions:
            for i, session in enumerate(sessions, 1):
                sessions_text += f"""
**Session {i}:**
- 📱 Phone: {session['phone']}
- 📅 Dernière utilisation: {session['last_used']}
- 📁 Fichier: {session['session_file']}
"""
        else:
            sessions_text += "\n❌ Aucune session persistante trouvée."

        sessions_text += f"""

🔧 **Informations Techniques**
- 📂 Répertoire de travail: /home/runner/workspace
- 🗄️ Base de données: PostgreSQL
- 🔄 Keep-Alive: Actif
- 📡 Webhook: {repl_url}/webhook
"""

        await event.respond(sessions_text)

    except Exception as e:
        logger.error(f"Erreur dans handle_sessions: {e}")
        await event.respond("❌ Erreur lors de la récupération des sessions.")
@client.on(events.NewMessage(pattern="/sessions"))
async def sessions_command(event):
    """Handle /sessions command"""
    await handle_admin_commands(event, client)

@client.on(events.NewMessage(pattern="/stop"))
async def stop_continuous_command(event):
    """Handle /stop command - Stop continuous mode"""
    try:
        user_id = event.sender_id

        # Only allow admin to control
        if user_id != ADMIN_ID:
            await event.respond("❌ Commande réservée aux administrateurs.")
            return

        # Access the keep_alive instance (will be created in start_bot)
        if hasattr(client, 'keep_alive_system'):
            response = client.keep_alive_system.stop_continuous_mode()
            await event.respond(response)
        else:
            await event.respond("❌ Système keep-alive non initialisé.")

        logger.info(f"Continuous mode stopped by admin {user_id}")

    except Exception as e:
        logger.error(f"Error in stop command: {e}")
        await event.respond("❌ Erreur lors de l'arrêt du mode continu.")

@client.on(events.NewMessage(pattern="/start_continuous"))
async def start_continuous_command(event):
    """Handle /start_continuous command - Start continuous mode"""
    try:
        user_id = event.sender_id

        # Only allow admin to control
        if user_id != ADMIN_ID:
            await event.respond("❌ Commande réservée aux administrateurs.")
            return

        # Access the keep_alive instance
        if hasattr(client, 'keep_alive_system'):
            response = client.keep_alive_system.start_continuous_mode()
            await event.respond(response)
        else:
            await event.respond("❌ Système keep-alive non initialisé.")

        logger.info(f"Continuous mode started by admin {user_id}")

    except Exception as e:
        logger.error(f"Error in start_continuous command: {e}")
        await event.respond("❌ Erreur lors du démarrage du mode continu.")

@client.on(events.NewMessage(pattern="/keepalive"))
async def keepalive_command(event):
    """Handle /keepalive command - Check keep-alive system status"""
    try:
        user_id = event.sender_id

        # Only allow admin to check status
        if user_id != ADMIN_ID:
            await event.respond("❌ Commande réservée aux administrateurs.")
            return

        # Get status from keep_alive system
        if hasattr(client, 'keep_alive_system'):
            status = client.keep_alive_system.get_status()

            if status['continuous_mode']:
                mode_text = "🔄 **Mode CONTINU FORCÉ**"
                mode_desc = "Messages envoyés en permanence"
            elif status['wake_up_active']:
                mode_text = "⚡ **Mode RÉVEIL ACTIF**"
                mode_desc = "Échanges en cours suite à inactivité"
            else:
                mode_text = "😴 **Mode VEILLE INTELLIGENT**"
                mode_desc = "Surveillance active - réveil si inactivité"

            status_message = f"""
🔄 **Statut du Système Keep-Alive**

{mode_text}
{mode_desc}

✅ Système de maintien d'activité actif
🤖 Bot TeleFeed: En ligne
🌐 Serveur HTTP: En fonctionnement

**Statistiques :**
• Messages envoyés: {status['message_count']}
• Dernière activité bot: {status['server_last_activity']}

**Contrôles :**
• `/stop` - Arrêter les échanges (mode veille)
• `/start_continuous` - Forcer mode continu

**Fonctionnement intelligent :**
• Surveillance automatique (1 min)
• Réveil si inactivité > 2 min
• Échanges jusqu'à `/stop`
            """
        else:
            status_message = """
🔄 **Statut du Système Keep-Alive**

❌ Système keep-alive non initialisé
            """

        await event.respond(status_message)
        logger.info(f"Keep-alive status checked by admin {user_id}")

    except Exception as e:
        logger.error(f"Error in keepalive command: {e}")
        await event.respond("❌ Erreur lors de la vérification du statut.")

@client.on(events.NewMessage(pattern="/reset"))
async def reset_command(event):
    """Handle /reset command"""
    try:
        await handle_reset_command(event, client)
        logger.info(f"Reset command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in reset command: {e}")
        await event.respond("❌ Erreur lors de la réinitialisation. Veuillez réessayer.")

@client.on(events.NewMessage)
async def handle_unknown_command(event):
    """Handle unknown commands and verification codes"""
    # Mettre à jour l'activité du bot à chaque message
    if hasattr(client, 'keep_alive_system'):
        client.keep_alive_system.update_bot_activity()

    # First check if it's a verification code
    if await handle_verification_code(event, client):
        return  # Message was handled as verification code

    # Check if it's a redirection format (ID - ID)
    if event.text and " - " in event.text:
        parts = event.text.split(" - ")
        if len(parts) == 2 and len(parts[0].strip()) > 5 and len(parts[1].strip()) > 5:
            from redirection import handle_redirection_format
            await handle_redirection_format(event, client, parts[0].strip(), parts[1].strip())
            return



    # Then check for unknown commands
    if event.text and event.text.startswith('/') and not any(event.text.startswith(cmd) for cmd in ['/start', '/connect', '/deposer', '/redirection', '/transformation', '/whitelist', '/blacklist', '/chats', '/help', '/admin', '/confirm', '/generate', '/users', '/stats', '/sessions', '/keepalive', '/stop', '/start_continuous', '/channel_to_bot', '/setup_channel', '/reset']):
        await event.respond("❓ Commande non reconnue. Tapez /help pour voir les commandes disponibles.")

# Surveillance automatique pour Render
@client.on(events.NewMessage(pattern="Kouamé Appolinaire tu es là ?"))
async def surveillance_response(event):
    """Handle automatic surveillance from Render"""
    try:
        await event.respond("oui bb")
        logger.info(f"Surveillance response sent to {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in surveillance response: {e}")

async def start_bot():
    """Start the bot and handle all initialization"""
    # Start client with bot token
    await client.start(bot_token=BOT_TOKEN)
    logger.info("🚀 Bot TeleFeed démarré avec succès!")
    print("Bot lancé !")

    # Wait a moment for bot to be fully ready
    await asyncio.sleep(2)

    # Restore persistent sessions (non-blocking — échec silencieux)
    try:
        from session_manager import session_manager
        logger.info("🔄 Restauration des sessions persistantes...")
        await session_manager.restore_all_sessions()
    except Exception as e:
        logger.warning(f"⚠️ Restauration sessions ignorée: {e}")

    # Setup message redirector (non-blocking — échec silencieux)
    try:
        from message_handler import message_redirector
        await message_redirector.setup_redirection_handlers()
        logger.info("🔄 Redirections configurées via message_redirector")
    except Exception as e:
        logger.warning(f"⚠️ Configuration redirections ignorée: {e}")

    logger.info("🔄 Système de restauration automatique des redirections activé")

    # Initialize keep-alive system (non-blocking)
    try:
        keep_alive = KeepAliveSystem(client, ADMIN_ID)
        client.keep_alive_system = keep_alive
        asyncio.create_task(keep_alive.start_keep_alive())
        logger.info("🔄 Système de maintien d'activité démarré")
    except Exception as e:
        logger.warning(f"⚠️ Keep-alive ignoré: {e}")

    # Toujours atteindre cette ligne — c'est ici que le bot écoute les commandes
    logger.info("✅ Bot en écoute — toutes les commandes sont actives")
    await client.run_until_disconnected()

def start_bot_sync():
    """Synchronous wrapper to start the bot"""
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the bot
        loop.run_until_complete(start_bot())
    except Exception as e:
        logger.error(f"Error in start_bot_sync: {e}")
        raise

if __name__ == "__main__":
    start_bot_sync()