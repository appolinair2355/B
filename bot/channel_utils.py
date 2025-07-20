import logging
from telethon.tl.functions.messages import CheckChatInviteRequest, ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon import TelegramClient

logger = logging.getLogger(__name__)

async def resolve_invite_link(client, invite_link):
    """
    Resolve a Telegram invite link to get channel/group ID
    """
    try:
        # Extract the invite hash from the link
        if "t.me/+" in invite_link:
            invite_hash = invite_link.split("t.me/+")[1]
        elif "t.me/joinchat/" in invite_link:
            invite_hash = invite_link.split("t.me/joinchat/")[1]
        else:
            raise ValueError("Invalid invite link format")
        
        # Check the invite link details
        invite_info = await client(CheckChatInviteRequest(invite_hash))
        
        # If already a member, get the chat info
        if hasattr(invite_info, 'chat'):
            chat = invite_info.chat
            return chat.id, chat.title
        
        # If not a member but can see info
        if hasattr(invite_info, 'title'):
            logger.info(f"Channel found: {invite_info.title}")
            # Join the channel to get full access
            result = await client(ImportChatInviteRequest(invite_hash))
            if hasattr(result, 'chats') and result.chats:
                chat = result.chats[0]
                return chat.id, chat.title
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error resolving invite link: {e}")
        return None, None

async def get_bot_id(client):
    """
    Get the bot's own user ID
    """
    try:
        me = await client.get_me()
        return me.id
    except Exception as e:
        logger.error(f"Error getting bot ID: {e}")
        return None

async def create_channel_to_bot_redirection(client, user_id, channel_invite_link, bot_id):
    """
    Create a redirection from a channel (using invite link) to the bot
    """
    try:
        # Resolve the channel invite link
        channel_id, channel_title = await resolve_invite_link(client, channel_invite_link)
        
        if not channel_id:
            return False, "Could not resolve channel invite link"
        
        # Convert to proper ID format (negative for channels/groups)
        if channel_id > 0:
            source_id = f"-100{channel_id}"
        else:
            source_id = str(channel_id)
        
        destination_id = str(bot_id)
        
        # Create redirection name based on channel title
        redirection_name = f"channel_to_bot_{channel_id}"
        if channel_title:
            # Clean the title for use as redirection name
            clean_title = "".join(c for c in channel_title if c.isalnum() or c in "_-").lower()
            redirection_name = f"from_{clean_title}"
        
        logger.info(f"Setting up redirection: {source_id} -> {destination_id} (name: {redirection_name})")
        
        return True, {
            "source_id": source_id,
            "destination_id": destination_id,
            "name": redirection_name,
            "channel_title": channel_title
        }
        
    except Exception as e:
        logger.error(f"Error creating channel to bot redirection: {e}")
        return False, str(e)