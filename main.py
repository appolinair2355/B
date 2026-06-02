import os, asyncio, logging
from env_loader import load_env
from http_server import start_server_in_background

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    load_env()
    os.environ['PORT'] = str(int(os.environ.get('PORT', 10000)))
    logger.info("TeleFeed Bot demarre")
    import glob
    for s in glob.glob("*.session*"):
        try: os.remove(s)
        except: pass
    start_server_in_background()
    from handlers import start_bot
    await start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot arrete")
    except Exception as e:
        logger.error(f"Erreur: {e}")
        import time; time.sleep(30)
