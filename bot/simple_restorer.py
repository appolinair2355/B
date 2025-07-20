"""
Système de restauration simple et robuste des redirections
Utilise la session du bot principal pour traiter les redirections
"""

import logging
import asyncio
import os
import json
from typing import Dict, List, Optional, Tuple, Any, Union
from telethon import TelegramClient, events
from telethon.types import Message, MessageEntityMention, MessageEntityMentionName
from config.settings import API_ID, API_HASH, BOT_TOKEN
from bot.database import load_data, save_data

logger = logging.getLogger(__name__)

class SimpleRedirectionRestorer:
    """
    Restaurateur simple et robuste des redirections
    Utilise la session du bot principal pour traiter toutes les redirections
    """

    def __init__(self):
        self.bot_client = None
        self.active_redirections = {}
        self.message_mapping = {}

    async def initialize_bot_client(self):
        """Initialise le client bot principal"""
        try:
            if not self.bot_client:
                self.bot_client = TelegramClient('bot_session', API_ID, API_HASH)
                await self.bot_client.start(bot_token=BOT_TOKEN)
                logger.info("✅ Client bot principal initialisé pour les redirections")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur initialisation client bot: {e}")
            return False

    async def restore_redirections(self):
        """Restaure toutes les redirections depuis la base de données"""
        try:
            # Initialiser le client bot
            if not await self.initialize_bot_client():
                return

            # Charger les données de redirection
            data = load_data()
            redirections = data.get("redirections", {})

            total_restored = 0

            for user_id, user_redirections in redirections.items():
                user_count = 0

                for name, redir_data in user_redirections.items():
                    if redir_data.get('active', True):
                        source_id = redir_data.get('source_id')
                        destination_id = redir_data.get('destination_id')

                        if source_id and destination_id:
                            success = await self._setup_redirection_handler(
                                name, source_id, destination_id, user_id
                            )
                            if success:
                                user_count += 1
                                total_restored += 1

                if user_count > 0:
                    logger.info(f"✅ Restauré {user_count} redirections pour utilisateur {user_id}")

            logger.info(f"🔄 Restauration terminée: {total_restored} redirections actives")

        except Exception as e:
            logger.error(f"❌ Erreur restauration redirections: {e}")

    async def _setup_redirection_handler(self, name, source_id, destination_id, user_id):
        """Configure un gestionnaire de redirection"""
        try:
            # Convertir les IDs en entiers
            source_chat_id = int(source_id)
            dest_chat_id = int(destination_id)

            # Vérifier l'accès aux canaux
            try:
                source_entity = await self.bot_client.get_entity(source_chat_id)
                dest_entity = await self.bot_client.get_entity(dest_chat_id)
                logger.info(f"✅ Accès vérifié: {source_entity.title if hasattr(source_entity, 'title') else source_chat_id} → {dest_entity.title if hasattr(dest_entity, 'title') else dest_chat_id}")
            except Exception as e:
                logger.warning(f"⚠️ Impossible d'accéder aux canaux pour {name}: {e}")
                return False

            # Créer le gestionnaire de messages
            @self.bot_client.on(events.NewMessage(chats=source_chat_id))
            async def message_handler(event):
                await self._handle_message_redirection(
                    event, dest_chat_id, name, user_id, is_edit=False
                )

            # Créer le gestionnaire d'édition
            @self.bot_client.on(events.MessageEdited(chats=source_chat_id))
            async def edit_handler(event):
                await self._handle_message_redirection(
                    event, dest_chat_id, name, user_id, is_edit=True
                )

            # Stocker la redirection active
            self.active_redirections[name] = {
                'source_id': source_chat_id,
                'destination_id': dest_chat_id,
                'user_id': user_id,
                'message_handler': message_handler,
                'edit_handler': edit_handler
            }

            logger.info(f"🔄 Redirection '{name}' configurée: {source_chat_id} → {dest_chat_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur configuration redirection {name}: {e}")
            return False

    async def _handle_message_redirection(self, event, destination_id, redirect_name, user_id, is_edit=False):
        """Traite la redirection d'un message"""
        try:
            message = event.message
            original_msg_id = message.id
            mapping_key = f"{event.chat_id}_{original_msg_id}_{destination_id}"

            # Obtenir les noms des canaux pour les logs
            source_name = await self._get_channel_name(event.chat_id)
            dest_name = await self._get_channel_name(destination_id)

            if is_edit:
                # Gérer l'édition de message
                if mapping_key in self.message_mapping:
                    redirected_msg_id = self.message_mapping[mapping_key]
                    try:
                        if message.text:
                            await self.bot_client.edit_message(destination_id, redirected_msg_id, message.text)
                            logger.info(f"📝 Message édité: {source_name} → {dest_name} via {redirect_name}")
                            return
                        else:
                            # Message supprimé ou sans contenu
                            try:
                                await self.bot_client.delete_messages(destination_id, redirected_msg_id)
                                del self.message_mapping[mapping_key]
                                logger.info(f"🗑️ Message supprimé: {source_name} → {dest_name} via {redirect_name}")
                                return
                            except:
                                pass
                    except Exception as edit_error:
                        if "Content of the message was not modified" in str(edit_error):
                            return  # Contenu inchangé
                        logger.warning(f"⚠️ Échec édition message: {edit_error}")
                else:
                    return  # Édition d'un message non mappé

            # Envoyer nouveau message ou remplacer média
            sent_message = None

            if message.text:
                # Message texte
                sent_message = await self.bot_client.send_message(destination_id, message.text)
            elif message.media:
                # Message média - transférer
                sent_message = await self.bot_client.forward_messages(destination_id, message)
            else:
                # Message vide
                sent_message = await self.bot_client.send_message(destination_id, "📎 Message transféré")

            # Stocker le mapping pour futures éditions
            if sent_message and not is_edit:
                if hasattr(sent_message, 'id'):
                    self.message_mapping[mapping_key] = sent_message.id
                elif isinstance(sent_message, list) and len(sent_message) > 0:
                    self.message_mapping[mapping_key] = sent_message[0].id

            action = "édité et redirigé" if is_edit else "redirigé"
            logger.info(f"✅ Message {action}: {source_name} → {dest_name} via {redirect_name}")

        except Exception as e:
            logger.error(f"❌ Erreur redirection message via {redirect_name}: {e}")

    async def _get_channel_name(self, chat_id):
        """Obtient le nom d'un canal"""
        try:
            entity = await self.bot_client.get_entity(chat_id)

            if hasattr(entity, 'title') and entity.title:
                return entity.title
            elif hasattr(entity, 'first_name') and entity.first_name:
                name = entity.first_name
                if hasattr(entity, 'last_name') and entity.last_name:
                    name += f" {entity.last_name}"
                return name
            elif hasattr(entity, 'username') and entity.username:
                return f"@{entity.username}"
            else:
                return f"Chat {chat_id}"

        except Exception as e:
            logger.error(f"❌ Erreur nom canal {chat_id}: {e}")
            return f"Chat {chat_id}"

    async def add_redirection(self, user_id, name, source_id, destination_id):
        """Ajoute une nouvelle redirection"""
        try:
            if not self.bot_client:
                await self.initialize_bot_client()

            success = await self._setup_redirection_handler(
                name, source_id, destination_id, user_id
            )

            if success:
                logger.info(f"✅ Nouvelle redirection ajoutée: {name}")
                return True
            else:
                logger.error(f"❌ Échec ajout redirection: {name}")
                return False

        except Exception as e:
            logger.error(f"❌ Erreur ajout redirection: {e}")
            return False

    async def remove_redirection(self, name):
        """Supprime une redirection"""
        try:
            if name in self.active_redirections:
                del self.active_redirections[name]
                logger.info(f"✅ Redirection supprimée: {name}")
                return True
            else:
                logger.warning(f"⚠️ Redirection non trouvée: {name}")
                return False

        except Exception as e:
            logger.error(f"❌ Erreur suppression redirection: {e}")
            return False

# Instance globale
simple_restorer = SimpleRedirectionRestorer()