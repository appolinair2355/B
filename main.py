from config.env_loader import load_env
from http_server import start_server_in_background
import os
import asyncio
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Point d'entrée principal pour Replit"""
    load_env()
    
    # Configuration pour Replit
    replit_port = int(os.environ.get('PORT', 8080))
    os.environ['PORT'] = str(replit_port)
    
    logger.info("🚀 TeleFeed Bot démarré pour Replit Always On")
    
    # Nettoyer les anciennes sessions
    import glob
    for session_file in glob.glob("*.session*"):
        try:
            os.remove(session_file)
            logger.info(f"🧹 Session supprimée: {session_file}")
        except:
            pass
    
    # Start HTTP server in background
    server_thread = start_server_in_background()
    
    # Start the bot with new session
    from bot.handlers import start_bot
    await start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot arrêté par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        # Attendre un peu avant de redémarrer
        import time
        time.sleep(30)