import logging
from channel_utils import resolve_invite_link, get_bot_id, create_channel_to_bot_redirection
from database import store_redirection
from message_handler import message_redirector

logger = logging.getLogger(__name__)

async def handle_channel_to_bot_command(event, client):
    """
    Handle setting up redirection from a channel to the bot using invite link
    """
    try:
        message_text = event.text.strip()
        user_id = event.sender_id
        
        # Check if command is used alone
        if message_text == "/channel_to_bot":
            usage_message = """
🔗 **Configuration de redirection Canal → Bot**

**Utilisation :**
`/channel_to_bot LIEN_INVITATION`

**Exemple :**
`/channel_to_bot https://t.me/+KCuJNqbhpzowN2Y8`

Cette commande configure une redirection automatique de tous les messages du canal vers votre bot.
            """
            await event.respond(usage_message)
            return
        
        # Extract invite link from command
        parts = message_text.split(maxsplit=1)
        if len(parts) != 2:
            await event.respond("❌ Format incorrect. Utilisez : `/channel_to_bot LIEN_INVITATION`")
            return
        
        invite_link = parts[1]
        
        # Validate invite link format
        if not ("t.me/+" in invite_link or "t.me/joinchat/" in invite_link):
            await event.respond("❌ Lien d'invitation invalide. Utilisez un lien t.me/+ ou t.me/joinchat/")
            return
        
        await event.respond("🔄 **Configuration en cours...**\n\nRésolution du lien d'invitation...")
        
        # Get bot's own ID
        bot_id = await get_bot_id(client)
        if not bot_id:
            await event.respond("❌ Impossible d'obtenir l'ID du bot.")
            return
        
        # Resolve the channel invite link
        channel_id, channel_title = await resolve_invite_link(client, invite_link)
        
        if not channel_id:
            await event.respond("❌ Impossible de résoudre le lien d'invitation. Vérifiez que le lien est valide et que le bot peut accéder au canal.")
            return
        
        # Convert to proper ID format
        if channel_id > 0:
            source_id = f"-100{channel_id}"
        else:
            source_id = str(channel_id)
        
        destination_id = str(bot_id)
        
        # Create redirection name
        redirection_name = f"channel_to_bot"
        if channel_title:
            clean_title = "".join(c for c in channel_title if c.isalnum() or c in "_-").lower()[:20]
            redirection_name = f"from_{clean_title}"
        
        # Get user's phone number (we'll use a dummy phone for bot redirections)
        phone_number = "bot_redirection"
        
        # Store the redirection in database
        await store_redirection(user_id, redirection_name, phone_number, "add", 
                               channel_title or "Canal", source_id, destination_id)
        
        # Set up the message redirection handler with user's client
        from message_handler import message_redirector
        handler_added = await message_redirector.add_redirection_handler(user_id, redirection_name, source_id, destination_id)
        
        success_message = f"""
✅ **Redirection configurée avec succès !**

📺 **Canal source :** {channel_title or 'Canal'}
🤖 **Destination :** Bot TeleFeed
📋 **Nom de la redirection :** {redirection_name}
🆔 **ID du canal :** {source_id}
🎯 **ID du bot :** {destination_id}

{"🔄 **Transfert automatique :** Activé" if handler_added else "⚠️ **Transfert automatique :** Erreur d'activation"}

Tous les messages du canal seront maintenant transférés vers ce bot !
        """
        
        await event.respond(success_message)
        logger.info(f"Channel to bot redirection configured for user {user_id}: {source_id} -> {destination_id}")
        
    except Exception as e:
        logger.error(f"Error in channel_to_bot command: {e}")
        await event.respond("❌ Erreur lors de la configuration de la redirection. Veuillez réessayer.")

async def setup_automatic_channel_redirection(client, user_id, channel_invite_link):
    """
    Automatically set up redirection from channel to bot (for direct calls)
    """
    try:
        # Get bot's own ID
        bot_id = await get_bot_id(client)
        if not bot_id:
            logger.error("Could not get bot ID")
            return False, "Could not get bot ID"
        
        # Resolve the channel invite link
        channel_id, channel_title = await resolve_invite_link(client, channel_invite_link)
        
        if not channel_id:
            logger.error("Could not resolve channel invite link")
            return False, "Could not resolve channel invite link"
        
        # Convert to proper ID format
        if channel_id > 0:
            source_id = f"-100{channel_id}"
        else:
            source_id = str(channel_id)
        
        destination_id = str(bot_id)
        
        # Create redirection name
        redirection_name = "auto_channel_to_bot"
        if channel_title:
            clean_title = "".join(c for c in channel_title if c.isalnum() or c in "_-").lower()[:20]
            redirection_name = f"auto_{clean_title}"
        
        # Store the redirection
        phone_number = "bot_redirection"
        await store_redirection(user_id, redirection_name, phone_number, "add", 
                               channel_title or "Canal", source_id, destination_id)
        
        # Set up the handler
        handler_added = await message_redirector.add_redirection_handler(user_id, redirection_name, source_id, destination_id)
        
        logger.info(f"Automatic channel to bot redirection configured: {source_id} -> {destination_id}")
        return True, {
            "source_id": source_id,
            "destination_id": destination_id,
            "name": redirection_name,
            "channel_title": channel_title,
            "handler_added": handler_added
        }
        
    except Exception as e:
        logger.error(f"Error in automatic channel redirection setup: {e}")
        return False, str(e)