
import logging
import os
import glob
import json
from database import load_data, save_data
from connection import active_connections

logger = logging.getLogger(__name__)

async def handle_reset_command(event, client):
    """
    Handle /reset command
    Cleans all connections and redirections for a fresh start
    """
    try:
        user_id = event.sender_id
        
        # Confirmation message
        confirmation_message = """
⚠️ **COMMANDE DE RÉINITIALISATION**

Cette commande va supprimer :
• ❌ Toutes vos connexions Telegram
• ❌ Toutes vos redirections actives
• ❌ Tous les fichiers de session
• ❌ Toutes les données persistantes

**Pour confirmer, tapez :**
`/reset CONFIRM`

**Pour annuler, ignorez ce message.**
        """
        
        message_text = event.text.strip()
        parts = message_text.split()
        
        if len(parts) == 1:  # Just /reset
            await event.respond(confirmation_message)
            return
        elif len(parts) == 2 and parts[1] == "CONFIRM":
            await perform_reset(event, user_id)
        else:
            await event.respond("❌ Format incorrect. Utilisez `/reset` puis `/reset CONFIRM`")
            
    except Exception as e:
        logger.error(f"Error in reset command: {e}")
        await event.respond("❌ Erreur lors de la réinitialisation.")

async def perform_reset(event, user_id):
    """Perform the actual reset operation"""
    try:
        reset_count = {
            'sessions_cleaned': 0,
            'redirections_cleaned': 0,
            'files_deleted': 0,
            'connections_closed': 0
        }
        
        await event.respond("🔄 **Démarrage de la réinitialisation...**")
        
        # 1. Clean active connections
        if user_id in active_connections:
            try:
                connection_data = active_connections[user_id]
                client = connection_data.get('client')
                if client:
                    await client.disconnect()
                del active_connections[user_id]
                reset_count['connections_closed'] += 1
                logger.info(f"Active connection closed for user {user_id}")
            except Exception as e:
                logger.error(f"Error closing active connection: {e}")
        
        # 2. Clean session files
        session_patterns = [
            f"session_{user_id}_*.session",
            f"{user_id}_*.session",
            f"session_*_{user_id}.session"
        ]
        
        for pattern in session_patterns:
            session_files = glob.glob(pattern)
            for session_file in session_files:
                try:
                    os.remove(session_file)
                    reset_count['files_deleted'] += 1
                    logger.info(f"Session file deleted: {session_file}")
                except Exception as e:
                    logger.error(f"Error deleting session file {session_file}: {e}")
        
        # Also clean journal files
        journal_files = glob.glob("*.session-journal")
        for journal_file in journal_files:
            try:
                os.remove(journal_file)
                reset_count['files_deleted'] += 1
            except:
                pass
        
        # 3. Clean telegram_sessions.json
        try:
            sessions_file = "telegram_sessions.json"
            if os.path.exists(sessions_file):
                with open(sessions_file, 'r') as f:
                    sessions_data = json.load(f)
                
                # Remove all sessions for this user
                sessions_to_remove = []
                for session_key, session_info in sessions_data.items():
                    if session_info.get('user_id') == user_id:
                        sessions_to_remove.append(session_key)
                
                for session_key in sessions_to_remove:
                    del sessions_data[session_key]
                    reset_count['sessions_cleaned'] += 1
                
                # Save updated sessions
                with open(sessions_file, 'w') as f:
                    json.dump(sessions_data, f, indent=2, default=str)
                
                logger.info(f"Cleaned {len(sessions_to_remove)} sessions from telegram_sessions.json")
        except Exception as e:
            logger.error(f"Error cleaning telegram_sessions.json: {e}")
        
        # 4. Clean user data (redirections)
        try:
            data = load_data()
            
            # Remove user redirections
            if "redirections" in data and str(user_id) in data["redirections"]:
                user_redirections = data["redirections"][str(user_id)]
                reset_count['redirections_cleaned'] = len(user_redirections)
                del data["redirections"][str(user_id)]
            
            # Remove pending redirections
            if "pending_redirections" in data and str(user_id) in data["pending_redirections"]:
                del data["pending_redirections"][str(user_id)]
            
            # Remove user connections
            if "connections" in data and str(user_id) in data["connections"]:
                del data["connections"][str(user_id)]
            
            # Save updated data
            save_data(data)
            logger.info(f"User data cleaned for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning user data: {e}")
        
        # 5. Reset message handlers
        try:
            from message_handler import message_redirector
            # Clear any handlers for this user
            if hasattr(message_redirector, 'user_handlers'):
                message_redirector.user_handlers.pop(user_id, None)
        except Exception as e:
            logger.error(f"Error resetting message handlers: {e}")
        
        # Success message
        success_message = f"""
✅ **RÉINITIALISATION TERMINÉE**

📊 **Résumé des suppressions :**
• 🔌 Connexions fermées : {reset_count['connections_closed']}
• 📁 Fichiers de session supprimés : {reset_count['files_deleted']}
• 🗄️ Sessions nettoyées : {reset_count['sessions_cleaned']}
• 🔄 Redirections supprimées : {reset_count['redirections_cleaned']}

🚀 **Prochaines étapes :**
1. Utilisez `/connect NUMERO` pour reconnecter vos numéros
2. Reconfigurez vos redirections avec `/redirection`

💡 **Votre système est maintenant propre et prêt !**
        """
        
        await event.respond(success_message)
        logger.info(f"Complete reset performed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error performing reset: {e}")
        await event.respond("❌ Erreur lors de la réinitialisation. Contactez l'administrateur.")

async def admin_reset_all(event, client):
    """Admin command to reset everything (use with caution)"""
    try:
        user_id = event.sender_id
        
        # Check if user is admin (you can implement admin check here)
        # For now, we'll assume this is called from admin context
        
        confirmation_message = """
🚨 **RÉINITIALISATION GLOBALE ADMIN**

Cette commande va supprimer TOUT :
• ❌ Toutes les connexions de tous les utilisateurs
• ❌ Toutes les redirections de tous les utilisateurs
• ❌ Tous les fichiers de session
• ❌ Toute la base de données

**Pour confirmer, tapez :**
`/admin_reset CONFIRM_ALL`
        """
        
        message_text = event.text.strip()
        parts = message_text.split()
        
        if len(parts) == 1:  # Just /admin_reset
            await event.respond(confirmation_message)
            return
        elif len(parts) == 2 and parts[1] == "CONFIRM_ALL":
            await perform_global_reset(event)
        else:
            await event.respond("❌ Format incorrect pour admin reset.")
            
    except Exception as e:
        logger.error(f"Error in admin reset command: {e}")
        await event.respond("❌ Erreur lors de la réinitialisation globale.")

async def perform_global_reset(event):
    """Perform global reset (admin only)"""
    try:
        await event.respond("🔄 **Démarrage de la réinitialisation globale...**")
        
        reset_count = {
            'sessions_deleted': 0,
            'connections_closed': 0,
            'files_deleted': 0
        }
        
        # 1. Close all active connections
        for user_id, connection_data in list(active_connections.items()):
            try:
                client = connection_data.get('client')
                if client:
                    await client.disconnect()
                del active_connections[user_id]
                reset_count['connections_closed'] += 1
            except Exception as e:
                logger.error(f"Error closing connection for user {user_id}: {e}")
        
        # 2. Delete all session files
        session_files = glob.glob("*.session")
        for session_file in session_files:
            try:
                os.remove(session_file)
                reset_count['files_deleted'] += 1
            except Exception as e:
                logger.error(f"Error deleting {session_file}: {e}")
        
        # Delete journal files
        journal_files = glob.glob("*.session-journal")
        for journal_file in journal_files:
            try:
                os.remove(journal_file)
                reset_count['files_deleted'] += 1
            except:
                pass
        
        # 3. Reset telegram_sessions.json
        try:
            with open("telegram_sessions.json", 'w') as f:
                json.dump({}, f)
            reset_count['sessions_deleted'] += 1
        except Exception as e:
            logger.error(f"Error resetting telegram_sessions.json: {e}")
        
        # 4. Reset user_data.json
        try:
            initial_data = {
                "connections": {},
                "redirections": {},
                "pending_redirections": {},
                "blacklist": {},
                "whitelist": {}
            }
            save_data(initial_data)
        except Exception as e:
            logger.error(f"Error resetting user_data.json: {e}")
        
        # Success message
        success_message = f"""
✅ **RÉINITIALISATION GLOBALE TERMINÉE**

📊 **Résumé des suppressions :**
• 🔌 Connexions fermées : {reset_count['connections_closed']}
• 📁 Fichiers supprimés : {reset_count['files_deleted']}
• 🗄️ Base de données réinitialisée

🚀 **Le système est maintenant complètement propre !**
        """
        
        await event.respond(success_message)
        logger.info("Global reset completed by admin")
        
    except Exception as e:
        logger.error(f"Error performing global reset: {e}")
        await event.respond("❌ Erreur lors de la réinitialisation globale.")
