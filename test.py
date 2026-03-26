# test_main.py
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST_MAIN")

async def test():
    logger.info("=== TEST MAIN START ===")
    try:
        from main import AnoraBot
        logger.info("AnoraBot imported")
        bot = AnoraBot()
        logger.info("Bot instance created")
        
        # Test init application saja
        logger.info("Testing init_application...")
        app = await bot.init_application()
        logger.info(f"Application created: {app}")
        
        logger.info("=== TEST MAIN SUCCESS ===")
    except Exception as e:
        logger.error(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
