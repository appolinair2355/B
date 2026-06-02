import logging
from channel_redirect import setup_automatic_channel_redirection

logger = logging.getLogger(__name__)

async def setup_user_channel_redirection(client, user_id):
    """
    Automatically set up redirection for the user's channel
    """
    try:
        # The channel invite link provided by the user
        channel_invite_link = "https://t.me/+KCuJNqbhpzowN2Y8"
        
        logger.info(f"Setting up automatic channel redirection for user {user_id}")
        
        success, result = await setup_automatic_channel_redirection(client, user_id, channel_invite_link)
        
        if success:
            logger.info(f"Channel redirection successfully configured for user {user_id}")
            return True, result
        else:
            logger.error(f"Failed to set up channel redirection for user {user_id}: {result}")
            return False, result
            
    except Exception as e:
        logger.error(f"Error in auto setup for user {user_id}: {e}")
        return False, str(e)

async def setup_channel_redirection_command(event, client):
    """
    Command to set up the specific channel redirection
    """
    try:
        user_id = event.sender_id
        
        await event.respond("🔄 **Configuration automatique de la redirection...**\n\nConnexion au canal en cours...")
        
        success, result = await setup_user_channel_redirection(client, user_id)
        
        if success:
            message = f"""
✅ **Redirection configurée automatiquement !**

📺 **Canal source :** {result.get('channel_title', 'Canal')}
🤖 **Destination :** Bot TeleFeed
📋 **Nom de la redirection :** {result['name']}
🆔 **ID du canal :** {result['source_id']}
🎯 **ID du bot :** {result['destination_id']}

{"🔄 **Transfert automatique :** Activé" if result.get('handler_added', False) else "⚠️ **Transfert automatique :** Erreur d'activation"}

Tous les messages du canal seront maintenant transférés vers ce bot !
            """
            await event.respond(message)
        else:
            await event.respond(f"❌ **Erreur lors de la configuration :**\n\n{result}")
            
    except Exception as e:
        logger.error(f"Error in setup channel redirection command: {e}")
        await event.respond("❌ Erreur lors de la configuration automatique. Veuillez réessayer.")