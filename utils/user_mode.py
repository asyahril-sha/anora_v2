# anora_v2/utils/user_mode.py
"""
User Mode Management - Menyimpan mode user ke database
"""

import json
import time
import logging
from typing import Optional

from memory.persistent import get_anora_persistent

logger = logging.getLogger(__name__)


async def get_user_mode(user_id: int) -> str:
    """Ambil mode user dari database"""
    persistent = await get_anora_persistent()
    data = await persistent.get_state(f'user_mode_{user_id}')
    if data:
        state = json.loads(data)
        return state.get('mode', 'chat')
    return 'chat'


async def set_user_mode(user_id: int, mode: str, active_role: Optional[str] = None):
    """Simpan mode user ke database"""
    persistent = await get_anora_persistent()
    state = {
        'mode': mode,
        'active_role': active_role,
        'updated_at': time.time()
    }
    await persistent.set_state(f'user_mode_{user_id}', json.dumps(state))
    logger.info(f"👤 User {user_id} mode saved: {mode}, role: {active_role}")


async def get_active_role(user_id: int) -> Optional[str]:
    """Ambil active role dari database"""
    persistent = await get_anora_persistent()
    data = await persistent.get_state(f'user_mode_{user_id}')
    if data:
        state = json.loads(data)
        return state.get('active_role')
    return None
