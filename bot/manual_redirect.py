
import logging
import asyncio
from telethon import TelegramClient, events
from config.settings import API_ID, API_HASH
from bot.connection import active_connections

logger = logging.getLogger(__name__)

class ManualRedirector:
    """Manual redirection system for testing and debugging"""
    
    def __init__(self):
        self.active_redirections = {}
    
    async def setup_manual_redirection(self, user_id, phone_number, source_id, destination_id, name="manual_redirect"):
        """Setup a manual redirection for testing"""
        try:
            if user_id not in active_connections:
                return False, "User not connected. Please use /connect first."
            
            client = active_connections[user_id].get('client')
            if not client or not client.is_connected():
                return False, "Client not available or disconnected."
            
            # Fix channel ID format if needed
            if source_id.isdigit() and len(source_id) >= 10:
                if source_id.startswith('100'):
                    source_id = f"-{source_id}"
                else:
                    source_id = f"-100{source_id}"
            elif source_id.isdigit() and not source_id.startswith('-'):
                source_id = f"-{source_id}"
                
            if destination_id.isdigit() and len(destination_id) >= 10:
                if destination_id.startswith('100'):
                    destination_id = f"-{destination_id}"
                else:
                    destination_id = f"-100{destination_id}"
            elif destination_id.isdigit() and not destination_id.startswith('-'):
                destination_id = f"-{destination_id}"
            
            # Test access to both channels
            try:
                source_entity = await client.get_entity(int(source_id))
                dest_entity = await client.get_entity(int(destination_id))
                
                source_name = getattr(source_entity, 'title', str(source_id))
                dest_name = getattr(dest_entity, 'title', str(destination_id))
                
                logger.info(f"✅ Access confirmed - Source: {source_name}, Destination: {dest_name}")
                
            except Exception as access_error:
                return False, f"Cannot access channels: {access_error}"
            
            # Create the handler
            redirect_key = f"{user_id}_{name}"
            
            @client.on(events.NewMessage(chats=int(source_id)))
            async def manual_message_handler(event):
                try:
                    message = event.message
                    
                    # Log the message details
                    logger.info(f"📨 Message received in {source_id}: {message.text[:100] if message.text else 'Media message'}")
                    
                    # Forward the message
                    if message.text:
                        sent = await client.send_message(int(destination_id), message.text)
                        logger.info(f"✅ Message forwarded to {destination_id}: {sent.id}")
                    elif message.media:
                        sent = await client.forward_messages(int(destination_id), message)
                        logger.info(f"✅ Media forwarded to {destination_id}")
                    
                except Exception as forward_error:
                    logger.error(f"❌ Error forwarding message: {forward_error}")
            
            self.active_redirections[redirect_key] = {
                'handler': manual_message_handler,
                'source_id': source_id,
                'destination_id': destination_id,
                'source_name': source_name,
                'dest_name': dest_name
            }
            
            return True, {
                'source_name': source_name,
                'dest_name': dest_name,
                'source_id': source_id,
                'destination_id': destination_id
            }
            
        except Exception as e:
            logger.error(f"Error setting up manual redirection: {e}")
            return False, str(e)
    
    async def test_channel_access(self, user_id, channel_id):
        """Test access to a specific channel"""
        try:
            if user_id not in active_connections:
                return False, "❌ **Session expirée**\n\n🔄 Reconnectez-vous avec `/connect VOTRE_NUMERO`\nPuis entrez le code reçu avec 'aa' devant."
            
            connection_data = active_connections[user_id]
            client = connection_data.get('client')
            
            if not client:
                return False, "❌ **Client non disponible**\n\n🔄 Reconnectez-vous avec `/connect VOTRE_NUMERO`"
            
            # Test if client is still connected
            if not client.is_connected():
                return False, "❌ **Connexion fermée**\n\n🔄 Reconnectez-vous avec `/connect VOTRE_NUMERO`"
            
            # Fix channel ID format if needed
            if str(channel_id).isdigit() and len(str(channel_id)) >= 10:
                if str(channel_id).startswith('100'):
                    channel_id = f"-{channel_id}"
                else:
                    channel_id = f"-100{channel_id}"
            elif str(channel_id).isdigit() and not str(channel_id).startswith('-'):
                channel_id = f"-{channel_id}"
            
            entity = await client.get_entity(int(channel_id))
            
            name = getattr(entity, 'title', getattr(entity, 'first_name', str(channel_id)))
            channel_type = type(entity).__name__
            
            return True, {
                'name': name,
                'type': channel_type,
                'id': entity.id
            }
            
        except Exception as e:
            return False, str(e)
    
    def get_active_redirections(self):
        """Get list of active manual redirections"""
        return list(self.active_redirections.keys())

# Global instance
manual_redirector = ManualRedirector()
