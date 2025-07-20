import logging
import os
import asyncio
import json
from telethon import TelegramClient
from bot.database import load_data, save_data
from datetime import datetime

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages persistent Telegram sessions using local file storage"""
    
    def __init__(self):
        self.sessions = {}  # In-memory active sessions
        self.sessions_file = "telegram_sessions.json"
        self._init_storage()
    
    def _init_storage(self):
        """Initialize local file storage for sessions"""
        try:
            if not os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'w') as f:
                    json.dump({}, f)
                logger.info("Session storage file created")
            else:
                logger.info("Session storage file found")
        except Exception as e:
            logger.error(f"Error initializing session storage: {e}")
    
    def _load_sessions(self):
        """Load sessions from local file"""
        try:
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            return {}
    
    def _save_sessions(self, sessions_data):
        """Save sessions to local file"""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
    
    async def store_session(self, user_id, phone_number, session_name):
        """Store session information in local file"""
        try:
            sessions_data = self._load_sessions()
            
            # Create unique key for user+phone combination
            session_key = f"{user_id}_{phone_number}"
            
            sessions_data[session_key] = {
                'user_id': user_id,
                'phone_number': phone_number,
                'session_file': session_name,
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat()
            }
            
            self._save_sessions(sessions_data)
            logger.info(f"✅ Session stored locally for user {user_id}, phone {phone_number}")
            
        except Exception as e:
            logger.error(f"Error storing session: {e}")
    
    async def get_user_sessions(self, user_id):
        """Get all active sessions for a user"""
        try:
            sessions_data = self._load_sessions()
            user_sessions = []
            
            for session_key, session_info in sessions_data.items():
                if session_info.get('user_id') == user_id and session_info.get('is_active', False):
                    user_sessions.append({
                        'phone': session_info['phone_number'],
                        'session_file': session_info['session_file'],
                        'last_used': session_info['last_used']
                    })
            
            return user_sessions
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    async def restore_all_sessions(self):
        """Restore all active sessions on bot startup"""
        try:
            sessions_data = self._load_sessions()
            restored_count = 0
            
            for session_key, session_info in sessions_data.items():
                if session_info.get('is_active', False):
                    user_id = session_info['user_id']
                    phone_number = session_info['phone_number']
                    session_file = session_info['session_file']
                    
                    success = await self._restore_session(user_id, phone_number, session_file)
                    if success:
                        restored_count += 1
                
            logger.info(f"✅ Restored {restored_count} active sessions from local storage")
            
        except Exception as e:
            logger.error(f"Error restoring sessions: {e}")
    
    async def _restore_session(self, user_id, phone_number, session_file):
        """Restore a single session"""
        try:
            # Check if session file exists
            if not os.path.exists(session_file):
                logger.warning(f"Session file not found: {session_file}")
                await self.deactivate_session(user_id, phone_number)
                return False
            
            # Create Telegram client with existing session
            client = TelegramClient(
                session_file.replace('.session', ''),  # Telethon expects name without .session
                int(os.getenv("API_ID")),
                os.getenv("API_HASH")
            )
            
            # Try to connect
            await client.connect()
            
            if await client.is_user_authorized():
                # Store in active sessions
                from bot.connection import active_connections
                active_connections[user_id] = {
                    'client': client,
                    'phone': phone_number,
                    'connected': True,
                    'session_name': session_file,
                    'restored': True
                }
                
                # Update last used time
                await self.update_session_activity(user_id, phone_number)
                
                logger.info(f"Session restored for user {user_id}, phone {phone_number}")
                return True
            else:
                # Session expired, deactivate
                await client.disconnect()
                await self.deactivate_session(user_id, phone_number)
                logger.warning(f"Session expired for user {user_id}, phone {phone_number}")
                return False
                
        except Exception as e:
            logger.error(f"Error restoring session for user {user_id}: {e}")
            await self.deactivate_session(user_id, phone_number)
            return False
    
    async def update_session_activity(self, user_id, phone_number):
        """Update last used timestamp for a session"""
        try:
            sessions_data = self._load_sessions()
            session_key = f"{user_id}_{phone_number}"
            
            if session_key in sessions_data:
                sessions_data[session_key]['last_used'] = datetime.now().isoformat()
                self._save_sessions(sessions_data)
            
        except Exception as e:
            logger.error(f"Error updating session activity: {e}")
    
    async def deactivate_session(self, user_id, phone_number):
        """Deactivate a session in local storage"""
        try:
            sessions_data = self._load_sessions()
            session_key = f"{user_id}_{phone_number}"
            
            if session_key in sessions_data:
                sessions_data[session_key]['is_active'] = False
                self._save_sessions(sessions_data)
            
            # Remove from active connections if present
            from bot.connection import active_connections
            if user_id in active_connections:
                client = active_connections[user_id].get('client')
                if client:
                    await client.disconnect()
                del active_connections[user_id]
            
            logger.info(f"Session deactivated for user {user_id}, phone {phone_number}")
            
        except Exception as e:
            logger.error(f"Error deactivating session: {e}")
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions (older than 7 days)"""
        try:
            sessions_data = self._load_sessions()
            current_time = datetime.now()
            expired_count = 0
            
            for session_key, session_info in sessions_data.items():
                if session_info.get('is_active', False):
                    last_used_str = session_info.get('last_used', '')
                    try:
                        last_used = datetime.fromisoformat(last_used_str.replace('Z', '+00:00'))
                        if (current_time - last_used).days > 7:
                            session_info['is_active'] = False
                            expired_count += 1
                    except:
                        # Invalid date format, mark as expired
                        session_info['is_active'] = False
                        expired_count += 1
            
            if expired_count > 0:
                self._save_sessions(sessions_data)
                logger.info(f"Cleaned up {expired_count} expired sessions")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
    
    def close(self):
        """Close session manager (no action needed for file storage)"""
        pass

# Global session manager instance
session_manager = SessionManager()