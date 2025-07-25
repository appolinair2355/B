import logging
import os
import asyncio
from telethon import TelegramClient, events
from config.settings import API_ID, API_HASH, BOT_TOKEN, ADMIN_ID
from keep_alive import KeepAliveSystem
from bot.license import check_license, validate_license_code
from bot.payment import process_payment
from bot.deploy import handle_deploy
from bot.connection import handle_connect, handle_verification_code
from bot.redirection import handle_redirection_command
from bot.transformation import handle_transformation_command
from bot.whitelist import handle_whitelist_command
from bot.blacklist import handle_blacklist_command
from bot.chats import handle_chats_command
from bot.admin import handle_admin_commands
from bot.channel_redirect import handle_channel_to_bot_command, setup_automatic_channel_redirection
from bot.auto_setup import setup_channel_redirection_command
from bot.reset import handle_reset_command, admin_reset_all

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
馃専 **Bienvenue sur TeleFeed !** 馃専

Votre bot intelligent pour la gestion de contenu Telegram.

**Commandes disponibles :**
鈥� `/connect` - Connecter un num茅ro de t茅l茅phone
鈥� `/redirection` - G茅rer les redirections entre chats
鈥� `/transformation` - Modifier le contenu des messages
鈥� `/whitelist` - Filtrer les messages autoris茅s
鈥� `/blacklist` - Ignorer certains messages
鈥� `/chats` - Afficher les chats associ茅s 脿 un num茅ro
鈥� `/deposer` - D茅poser des fichiers
鈥� `/channel_to_bot` - Rediriger un canal vers le bot
鈥� `/setup_channel` - Configuration automatique de votre canal

Toutes les fonctionnalit茅s sont maintenant disponibles gratuitement !
        """
        await event.respond(welcome_message)
        logger.info(f"User {event.sender_id} started the bot")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await event.respond("鉂� Une erreur est survenue. Veuillez r茅essayer.")





@client.on(events.NewMessage(pattern="/deposer"))
async def deposer(event):
    """Handle /deposer command for file deployment"""
    try:
        await handle_deploy(event, client)
        logger.info(f"Deploy request from user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in deploy handling: {e}")
        await event.respond("鉂� Erreur lors du traitement du d茅p么t. Veuillez r茅essayer.")

@client.on(events.NewMessage(pattern="/connect"))
async def connect(event):
    """Handle /connect command"""
    try:
        await handle_connect(event, client)
        logger.info(f"Connect command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in connect command: {e}")
        await event.respond("鉂� Erreur lors de la connexion. Veuillez r茅essayer.")

@client.on(events.NewMessage(pattern="/redirection"))
async def redirection(event):
    """Handle /redirection command"""
    try:
        await handle_redirection_command(event, client)
        logger.info(f"Redirection command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in redirection command: {e}")
        await event.respond("鉂� Erreur lors de la redirection. Veuillez r茅essayer.")

@client.on(events.NewMessage(pattern="/transformation"))
async def transformation(event):
    """Handle /transformation command"""
    try:
        await handle_transformation_command(event, client)
        logger.info(f"Transformation command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in transformation command: {e}")
        await event.respond("鉂� Erreur lors de la transformation. Veuillez r茅essayer.")

@client.on(events.NewMessage(pattern="/whitelist"))
async def whitelist(event):
    """Handle /whitelist command"""
    try:
        await handle_whitelist_command(event, client)
        logger.info(f"Whitelist command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in whitelist command: {e}")
        await event.respond("鉂� Erreur lors de la whitelist. Veuillez r茅essayer.")

@client.on(events.NewMessage(pattern="/blacklist"))
async def blacklist(event):
    """Handle /blacklist command"""
    try:
        await handle_blacklist_command(event, client)
        logger.info(f"Blacklist command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in blacklist command: {e}")
        await event.respond("鉂� Erreur lors de la blacklist. Veuillez r茅essayer.")

@client.on(events.NewMessage(pattern="/chats"))
async def chats(event):
    """Handle /chats command"""
    try:
        await handle_chats_command(event, client)
        logger.info(f"Chats command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in chats command: {e}")
        await event.respond("鉂� Erreur lors de l'affichage des chats. Veuillez r茅essayer.")

@client.on(events.NewMessage(pattern="/channel_to_bot"))
async def channel_to_bot(event):
    """Handle /channel_to_bot command"""
    try:
        await handle_channel_to_bot_command(event, client)
        logger.info(f"Channel to bot command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in channel to bot command: {e}")
        await event.respond("鉂� Erreur lors de la configuration de la redirection canal 鈫� bot. Veuillez r茅essayer.")

@client.on(events.NewMessage(pattern="/setup_channel"))
async def setup_channel(event):
    """Handle /setup_channel command for automatic setup"""
    try:
        await setup_channel_redirection_command(event, client)
        logger.info(f"Auto setup channel command used by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in auto setup channel command: {e}")
        await event.respond("鉂� Erreur lors de la configuration automatique. Veuillez r茅essayer.")

@client.on(events.NewMessage(pattern="/test_redirect"))
async def test_redirect(event):
    """Handle /test_redirect command for manual testing"""
    try:
        message_text = event.text.strip()
        user_id = event.sender_id

        if message_text == "/test_redirect":
            help_message = """
馃敡 **Test de Redirection Manuel**

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
            await event.respond("鉂� Format: `/test_redirect SOURCE_ID DESTINATION_ID`")
            return

        source_id = parts[1]
        destination_id = parts[2]

        await event.respond("馃攧 **Test de redirection en cours...**")

        from bot.manual_redirect import manual_redirector

        # Test access to both channels first
        source_ok, source_result = await manual_redirector.test_channel_access(user_id, source_id)
        dest_ok, dest_result = await manual_redirector.test_channel_access(user_id, destination_id)

        if not source_ok:
            await event.respond(f"鉂� **Erreur d'acc猫s au canal source {source_id}:**\n{source_result}")
            return

        if not dest_ok:
            await event.respond(f"鉂� **Erreur d'acc猫s au canal destination {destination_id}:**\n{dest_result}")
            return

        # Setup the redirection
        success, result = await manual_redirector.setup_manual_redirection(
            user_id, "test_phone", source_id, destination_id, "test_redirect"
        )

        if success:
            message = f"""
鉁� **Test de redirection configur茅 !**

馃摵 **Canal source :** {result['source_name']} ({source_id})
馃幆 **Canal destination :** {result['dest_name']} ({destination_id})

馃攧 **Status :** Redirection active
馃摠 **Test :** Envoyez un message dans le canal source pour tester

鈿狅笍 **Note :** Ceci est un test manuel. Les redirections automatiques n茅cessitent une session persistante.
            """
        else:
            message = f"鉂� **Erreur lors de la configuration :**\n{result}"

        await event.respond(message)

    except Exception as e:
        logger.error(f"Error in test redirect command: {e}")
        await event.respond("鉂� Erreur lors du test de redirection.")

@client.on(events.NewMessage(pattern="/help"))
async def help_command(event):
    """Handle /help command"""
    try:
        help_message = """
馃搵 **Aide TeleFeed**

**Commandes disponibles :**

馃敼 `/start` - D茅marrer le bot
馃敼 `/connect` - Connecter un num茅ro de t茅l茅phone
馃敼 `/redirection` - G茅rer les redirections entre chats
馃敼 `/transformation` - Modifier le contenu des messages
馃敼 `/whitelist` - Filtrer les messages autoris茅s
馃敼 `/blacklist` - Ignorer certains messages
馃敼 `/chats` - Afficher les chats associ茅s 脿 un num茅ro
馃敼 `/deposer` - D茅poser des fichiers
馃敼 `/channel_to_bot` - Rediriger un canal vers le bot
馃敼 `/setup_channel` - Configuration automatique de votre canal
馃敼 `/reset` - R茅initialiser toutes les connexions et redirections

**Commandes Admin :**
馃敭 `/prediction_start` - Activer les pr茅dictions automatiques
馃敭 `/prediction_stop` - D茅sactiver les pr茅dictions automatiques
馃敭 `/prediction_status` - Statut du syst猫me de pr茅dictions

馃敼 `/help` - Afficher cette aide

**Support :**
Pour toute question ou probl猫me, contactez l'administrateur.
        """
        await event.respond(help_message)
        logger.info(f"Help requested by user {event.sender_id}")
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await event.respond("鉂� Une erreur est survenue. Veuillez r茅essayer.")

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

        # Informations syst猫me
        python_version = platform.python_version()
        system_info = f"{platform.system()} {platform.release()}"

        # Get active connections
        from bot.connection import active_connections

        if user_id not in active_connections:
            # Afficher quand m锚me les infos serveur
            server_info = f"""
馃寪 **Serveur Replit H茅bergement**

馃摏 **Nom du serveur :** {hostname}
馃彿锔� **Nom du Repl :** {repl_name}
馃懁 **Propri茅taire :** {repl_owner}
馃敆 **URL publique :** {repl_url}
馃實 **Adresse IP :** {server_ip}
馃攲 **Port :** {server_port}
馃悕 **Python :** {python_version}
馃捇 **Syst猫me :** {system_info}
鈴� **Statut :** 鉁� Serveur actif

鉂� **Sessions utilisateur :** Aucune session active trouv茅e.

馃挕 **Note :** Utilisez /connect pour cr茅er une session.
"""
            await event.respond(server_info)
            return

        connection_info = active_connections[user_id]

        # Check if connection is still valid
        if 'client' not in connection_info:
            server_info = f"""
馃寪 **Serveur Replit H茅bergement**

馃摏 **Nom du serveur :** {hostname}
馃彿锔� **Nom du Repl :** {repl_name}
馃懁 **Propri茅taire :** {repl_owner}
馃敆 **URL publique :** {repl_url}
馃實 **Adresse IP :** {server_ip}
馃攲 **Port :** {server_port}
馃悕 **Python :** {python_version}
馃捇 **Syst猫me :** {system_info}
鈴� **Statut :** 鉁� Serveur actif

鉂� **Sessions utilisateur :** Session expir茅e. Veuillez vous reconnecter avec /connect.
"""
            await event.respond(server_info)
            return

        phone = connection_info.get('phone', 'N/A')
        connected_at = connection_info.get('connected_at', 'N/A')

        # Get session from database
        from bot.session_manager import session_manager
        sessions = await session_manager.get_user_sessions(user_id)

        sessions_text = f"""
馃寪 **Serveur Replit H茅bergement**

馃摏 **Nom du serveur :** {hostname}
馃彿锔� **Nom du Repl :** {repl_name}
馃懁 **Propri茅taire :** {repl_owner}
馃敆 **URL publique :** {repl_url}
馃實 **Adresse IP :** {server_ip}
馃攲 **Port :** {server_port}
馃悕 **Python :** {python_version}
馃捇 **Syst猫me :** {system_info}
鈴� **Statut :** 鉁� Serveur actif

馃摫 **Sessions Utilisateur**

馃懁 **Utilisateur :** {user_id}
馃摓 **Num茅ro :** {phone}
鈴� **Connect茅 le :** {connected_at}
馃敆 **Statut :** {'鉁� Connect茅' if connection_info.get('connected', False) else '鉂� D茅connect茅'}

馃搳 **D茅tails des sessions :**
"""

        if sessions:
            for i, session in enumerate(sessions, 1):
                sessions_text += f"""
**Session {i}:**
- 馃摫 Phone: {session['phone']}
- 馃搮 Derni猫re utilisation: {session['last_used']}
- 馃搧 Fichier: {session['session_file']}
"""
        else:
            sessions_text += "\n鉂� Aucune session persistante trouv茅e."

        sessions_text += f"""

馃敡 **Informations Techniques**
- 馃搨 R茅pertoire de travail: /home/runner/workspace
- 馃梽锔� Base de donn茅es: PostgreSQL
- 馃攧 Keep-Alive: Actif
- 馃摗 Webhook: {repl_url}/webhook
"""

        await event.respond(sessions_text)

    except Exception as e:
        logger.error(f"Erreur dans handle_sessions: {e}")
        await event.respond("鉂� Erreur lors de la r茅cup茅ration des sessions.")
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
            await event.respond("鉂� Commande r茅serv茅e aux administrateurs.")
            return

        # Access the keep_alive instance (will be created in start_bot)
        if hasattr(client, 'keep_alive_system'):
            response = client.keep_alive_system.stop_continuous_mode()
            await event.respond(response)
        else:
            await event.respond("鉂� Syst猫me keep-alive non initialis茅.")

        logger.info(f"Continuous mode stopped by admin {user_id}")

    except Exception as e:
        logger.error(f"Error in stop command: {e}")
        await event.respond("鉂� Erreur lors de l'arr锚t du mode continu.")

@client.on(events.NewMessage(pattern="/start_continuous"))
async def start_continuous_command(event):
    """Handle /start_continuous command - Start continuous mode"""
    try:
        user_id = event.sender_id

        # Only allow admin to control
        if user_id != ADMIN_ID:
            await event.respond("鉂� Commande r茅serv茅e aux administrateurs.")
            return

        # Access the keep_alive instance
        if hasattr(client, 'keep_alive_system'):
            response = client.keep_alive_system.start_continuous_mode()
            await event.respond(response)
        else:
            await event.respond("鉂� Syst猫me keep-alive non initialis茅.")

        logger.info(f"Continuous mode started by admin {user_id}")

    except Exception as e:
        logger.error(f"Error in start_continuous command: {e}")
        await event.respond("鉂� Erreur lors du d茅marrage du mode continu.")

@client.on(events.NewMessage(pattern="/keepalive"))
async def keepalive_command(event):
    """Handle /keepalive command - Check keep-alive system status"""
    try:
        user_id = event.sender_id

        # Only allow admin to check status
        if user_id != ADMIN_ID:
            await event.respond("鉂� Commande r茅serv茅e aux administrateurs.")
            return

        # Get status from keep_alive system
        if hasattr(client, 'keep_alive_system'):
            status = client.keep_alive_system.get_status()

            if status['continuous_mode']:
                mode_text = "馃攧 **Mode CONTINU FORC脡**"
                mode_desc = "Messages envoy茅s en permanence"
            elif status['wake_up_active']:
                mode_text = "鈿� **Mode R脡VEIL ACTIF**"
                mode_desc = "脡changes en cours suite 脿 inactivit茅"
            else:
                mode_text = "馃槾 **Mode VEILLE INTELLIGENT**"
                mode_desc = "Surveillance active - r茅veil si inactivit茅"

            status_message = f"""
馃攧 **Statut du Syst猫me Keep-Alive**

{mode_text}
{mode_desc}

鉁� Syst猫me de maintien d'activit茅 actif
馃 Bot TeleFeed: En ligne
馃寪 Serveur HTTP: En fonctionnement

**Statistiques :**
鈥� Messages envoy茅s: {status['message_count']}
鈥� Derni猫re activit茅 bot: {status['server_last_activity']}

**Contr么les :**
鈥� `/stop` - Arr锚ter les 茅changes (mode veille)
鈥� `/start_continuous` - Forcer mode continu

**Fonctionnement intelligent :**
鈥� Surveillance automatique (1 min)
鈥� R茅veil si inactivit茅 > 2 min
鈥� 脡changes jusqu'脿 `/stop`
            """
        else:
            status_message = """
馃攧 **Statut du Syst猫me Keep-Alive**

鉂� Syst猫me keep-alive non initialis茅
            """

        await event.respond(status_message)
        logger.info(f"Keep-alive status checked by admin {user_id}")

    except Exception as e:
        logger.error(f"Error in keepalive command: {e}")
        await event.respond("鉂� Erreur lors de la v茅rification du statut.")

@client.on(events.NewMessage(pattern="/prediction_start"))
async def start_prediction_command(event):
    """Handle /prediction_start command - Start automatic predictions"""
    try:
        user_id = event.sender_id

        # Only allow admin to control
        if user_id != ADMIN_ID:
            await event.respond("鉂� Commande r茅serv茅e aux administrateurs.")
            return

        from bot.prediction_system import prediction_system
        response = prediction_system.start_predictions()
        await event.respond(f"馃敭 {response}")

        logger.info(f"Predictions started by admin {user_id}")

    except Exception as e:
        logger.error(f"Error in prediction start command: {e}")
        await event.respond("鉂� Erreur lors du d茅marrage des pr茅dictions.")

@client.on(events.NewMessage(pattern="/prediction_stop"))
async def stop_prediction_command(event):
    """Handle /prediction_stop command - Stop automatic predictions"""
    try:
        user_id = event.sender_id

        # Only allow admin to control
        if user_id !=    start_bot_sync()
