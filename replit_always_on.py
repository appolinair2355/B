"""
Système Replit Always On pour TeleFeed Bot
Maintient le bot actif 24/7 sur Replit
"""

import asyncio
import logging
import time
import os
from datetime import datetime
import aiohttp
from config.env_loader import load_env

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('replit_always_on.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReplitAlwaysOn:
    def __init__(self):
        self.repl_url = os.environ.get('REPL_URL', 'https://telefeed-bot.yourname.repl.co')
        self.ping_interval = 300  # 5 minutes
        self.health_check_url = f"{self.repl_url}/health"
        
    async def keep_alive(self):
        """Maintient le bot actif en envoyant des pings réguliers"""
        logger.info("🚀 Démarrage du système Replit Always On")
        
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.health_check_url, timeout=30) as response:
                        if response.status == 200:
                            logger.info(f"✅ Ping réussi - Bot actif ({datetime.now().strftime('%H:%M:%S')})")
                        else:
                            logger.warning(f"⚠️ Ping échoué - Status: {response.status}")
                            
            except Exception as e:
                logger.error(f"❌ Erreur ping: {e}")
                
            await asyncio.sleep(self.ping_interval)
    
    async def start_bot_with_always_on(self):
        """Démarre le bot avec le système Always On"""
        from bot.handlers import start_bot
        
        # Démarrer le bot en arrière-plan
        bot_task = asyncio.create_task(start_bot())
        
        # Démarrer le système keep-alive
        keep_alive_task = asyncio.create_task(self.keep_alive())
        
        logger.info("🔄 Bot TeleFeed et Always On démarrés")
        
        # Attendre les deux tâches
        await asyncio.gather(bot_task, keep_alive_task)

def start_always_on():
    """Point d'entrée pour démarrer le système Always On"""
    load_env()
    
    always_on = ReplitAlwaysOn()
    
    try:
        asyncio.run(always_on.start_bot_with_always_on())
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt du système Always On")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")

if __name__ == "__main__":
    start_always_on()