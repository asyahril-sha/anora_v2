# test.py
import sys
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("TEST")

logger.info("=== TEST SCRIPT STARTED ===")

try:
    logger.info("Importing config...")
    from config import get_settings
    logger.info("Config imported successfully")
    
    settings = get_settings()
    logger.info(f"Settings loaded: ADMIN_ID={settings.admin_id}")
    
    logger.info("Importing core modules...")
    from core.emotional_engine import get_emotional_engine
    logger.info("Emotional engine imported")
    
    from core.relationship import get_relationship_manager
    logger.info("Relationship imported")
    
    from core.conflict_engine import get_conflict_engine
    logger.info("Conflict engine imported")
    
    from core.brain import get_anora_brain
    logger.info("Brain imported")
    
    from memory.persistent import get_anora_persistent
    logger.info("Persistent imported")
    
    from roleplay.integration import get_anora_roleplay
    logger.info("Roleplay imported")
    
    from roles.manager import get_role_manager
    logger.info("Role manager imported")
    
    from worker.background import get_anora_worker
    logger.info("Worker imported")
    
    logger.info("=== ALL IMPORTS SUCCESSFUL ===")
    
except Exception as e:
    logger.error(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

logger.info("=== TEST SCRIPT FINISHED ===")
