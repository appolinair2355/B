import asyncio
import aiohttp
import time
from datetime import datetime
import logging
from telethon import TelegramClient
import os

logger = logging.getLogger(__name__)

class KeepAliveSystem:
    """Système de maintien d'activité pour Replit"""
    
    def __init__(self, bot_client, admin_id):
        self.bot_client = bot_client
        self.admin_id = admin_id
        self.last_bot_activity = time.time()
        self.last_server_activity = time.time()
        self.check_interval = 300  # 5 minutes
        self.timeout_threshold = 600  # 10 minutes
        self.server_url = os.getenv('REPLIT_URL', 'http://localhost:5000')  # URL automatique Replit
        self.is_running = False
        
    async def start_keep_alive(self):
        """Démarrer le système de maintien d'activité"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("🔄 Système de maintien d'activité démarré")
        
        # Démarrer les tâches en parallèle
        await asyncio.gather(
            self.monitor_bot_activity(),
            self.monitor_server_activity(),
            self.periodic_health_check()
        )
    
    async def monitor_bot_activity(self):
        """Surveiller l'activité du bot"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Vérifier si le bot n'a pas été actif
                if current_time - self.last_bot_activity > self.timeout_threshold:
                    await self.wake_up_bot()
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Erreur dans monitor_bot_activity: {e}")
                await asyncio.sleep(60)
    
    async def monitor_server_activity(self):
        """Surveiller l'activité du serveur Replit"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Vérifier si le serveur n'a pas été actif
                if current_time - self.last_server_activity > self.timeout_threshold:
                    await self.wake_up_server()
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Erreur dans monitor_server_activity: {e}")
                await asyncio.sleep(60)
    
    async def wake_up_bot(self):
        """Réveiller le bot via message"""
        try:
            # Envoyer un message de réveil au bot
            await self.bot_client.send_message(
                self.admin_id,
                "🔔 Replit: Kouamé réveil toi"
            )
            logger.info("📨 Message de réveil envoyé au bot")
            
            # Simuler la réponse du bot
            await asyncio.sleep(2)
            await self.bot_client.send_message(
                self.admin_id,
                "✅ Bot: D'accord Replit"
            )
            
            self.last_bot_activity = time.time()
            logger.info("🤖 Bot réveillé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du réveil du bot: {e}")
    
    async def wake_up_server(self):
        """Réveiller le serveur Replit via requête HTTP"""
        try:
            # Envoyer message depuis le bot
            await self.bot_client.send_message(
                self.admin_id,
                "🔔 Bot: Replit réveil toi"
            )
            logger.info("📨 Message de réveil envoyé au serveur")
            
            # Faire une requête HTTP pour réveiller le serveur
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{self.server_url}/wake-up",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            logger.info("🌐 Serveur Replit réveillé via HTTP")
                        else:
                            logger.warning(f"Réponse serveur: {response.status}")
                except asyncio.TimeoutError:
                    logger.warning("Timeout lors de la requête au serveur")
                except Exception as e:
                    logger.warning(f"Erreur HTTP: {e}")
            
            # Simuler la réponse du serveur
            await asyncio.sleep(2)
            await self.bot_client.send_message(
                self.admin_id,
                "✅ Replit: D'accord Kouamé"
            )
            
            self.last_server_activity = time.time()
            logger.info("🖥️ Serveur réveillé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du réveil du serveur: {e}")
    
    async def periodic_health_check(self):
        """Vérification périodique de santé"""
        while self.is_running:
            try:
                # Ping périodique pour maintenir l'activité
                await self.ping_bot()
                await self.ping_server()
                
                # Attendre 2 minutes avant le prochain check
                await asyncio.sleep(120)
                
            except Exception as e:
                logger.error(f"Erreur dans periodic_health_check: {e}")
                await asyncio.sleep(60)
    
    async def ping_bot(self):
        """Ping silencieux pour maintenir l'activité du bot"""
        try:
            # Mettre à jour l'activité du bot
            self.last_bot_activity = time.time()
            
            # Log d'activité
            logger.info(f"🤖 Bot ping - {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Erreur ping bot: {e}")
    
    async def ping_server(self):
        """Ping silencieux pour maintenir l'activité du serveur"""
        try:
            # Faire une requête HTTP légère
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{self.server_url}/ping",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            self.last_server_activity = time.time()
                            logger.info(f"🌐 Serveur ping - {datetime.now().strftime('%H:%M:%S')}")
                        else:
                            logger.warning(f"Ping serveur failed: {response.status}")
                except asyncio.TimeoutError:
                    logger.warning("Timeout ping serveur")
                except Exception as e:
                    logger.debug(f"Erreur ping serveur: {e}")
                    
        except Exception as e:
            logger.error(f"Erreur ping serveur: {e}")
    
    def update_bot_activity(self):
        """Mettre à jour l'activité du bot (à appeler lors des commandes)"""
        self.last_bot_activity = time.time()
    
    def update_server_activity(self):
        """Mettre à jour l'activité du serveur (à appeler lors des requêtes HTTP)"""
        self.last_server_activity = time.time()
    
    def stop_keep_alive(self):
        """Arrêter le système de maintien d'activité"""
        self.is_running = False
        logger.info("🔴 Système de maintien d'activité arrêté")
    
    def get_status(self):
        """Obtenir le statut du système"""
        current_time = time.time()
        return {
            "bot_last_activity": datetime.fromtimestamp(self.last_bot_activity).strftime("%Y-%m-%d %H:%M:%S"),
            "server_last_activity": datetime.fromtimestamp(self.last_server_activity).strftime("%Y-%m-%d %H:%M:%S"),
            "bot_inactive_duration": int(current_time - self.last_bot_activity),
            "server_inactive_duration": int(current_time - self.last_server_activity),
            "is_running": self.is_running
        }