** {server_ip}
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
鈥� Derni猫re activit茅 bot: {status['bot_last_activity']}
鈥� Derni猫re activit茅 serveur: {status['server_last_activity']}

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
        if user_id != ADMIN_ID:
            await event.respond("鉂� Commande r茅serv茅e aux administrateurs.")
            return

        from bot.prediction_system import prediction_system
        response = prediction_system.stop_predictions()
        await event.respond(f"馃洃 {response}")

        logger.info(f"Predictions stopped by admin {user_id}")

    except Exception as e:
        logger.error(f"Error in prediction stop command: {e}")
        await event.respond("鉂� Erreur lors de l'arr锚t des pr茅dictions.")

@client.on(events.NewMessage(pattern="/prediction_status"))
async def prediction_status_command(event):
    """Handle /prediction_status command - Check prediction system status"""
    try:
        user_id = event.sender_id

        # Only allow admin to check status
        if user_id != ADMIN_ID:
            await event.respond("鉂� Commande r茅serv茅e aux administrateurs.")
            return

        from bot.prediction_system import prediction_system
        status = prediction_system.get_status()

        status_text = "鉁� ACTIF" if status['active'] else "鉂� INACTIF"

        status_message = f"""
馃敭 **Statut du Syst猫me de Pr茅dictions**

**脡tat :** {status_text}
**Total pr茅dictions :** {status['total_predictions']}

**Fonctionnement :**
鈥� Analyse automatique des messages transf茅r茅s
鈥� D茅tection des cartes entre parenth猫ses
鈥� Pr茅diction si 3 cartes de couleurs diff茅rentes
鈥� Notification automatique 脿 l'admin

**Contr么les :**
鈥� `/prediction_start` - Activer les pr茅dictions
鈥� `/prediction_stop` - D茅sactiver les pr茅dictions
鈥� `/prediction_status` - V茅rifier le statut

**Algorithme :**
1. Recherche des cartes : 鈾犫櫍鈾モ櫐 ou SCHD
2. V茅rification de la diversit茅 des couleurs
3. G茅n茅ration du num茅ro pr茅dit (1-9)
4. Message : "Le joueur recevra 3K"
        """

        await event.respond(status_message)
        logger.info(f"Prediction status checked by admin {user_id}")

    except Exception as e:
        logger.error(f"Error in prediction status command: {e}")
        await event.respond("鉂� Erreur lors de la v茅rification du statut des pr茅dictions.")

@client.on(events.NewMessage)
async def handle_unknown_command(event):
    """Handle unknown commands and verification codes"""
    # Mettre 脿 jour l'activit茅 du bot 脿 chaque message
    if hasattr(client, 'keep_alive_system'):
        client.keep_alive_system.update_bot_activity()

    # First check if it's a verification code
    if await handle_verification_code(event, client):
        return  # Message was handled as verification code

    # Check if 
