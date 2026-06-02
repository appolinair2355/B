import os
import asyncio
import logging
from env_loader import load_env
from http_server import start_server_in_background

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    load_env()
    port = int(os.environ.get('PORT', 10000))
    os.environ['PORT'] = str(port)
    logger.info("🚀 TeleFeed Bot démarré")

    import glob
    for session_file in glob.glob("*.session*"):
        try:
            os.remove(session_file)
        except:
            pass

    start_server_in_background()
    from handlers import start_bot
    await start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot arrêté")
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        import time
        time.sleep(30)
